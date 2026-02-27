"""Additional bridge.py tests to increase coverage."""
import json
import signal
from unittest.mock import MagicMock, patch

import pytest


class FakeMessage:
    def __init__(self, topic, payload, retain=False):
        self.topic = topic
        self.payload = payload if isinstance(payload, bytes) else payload.encode("utf-8")
        self.retain = retain


@pytest.fixture
def mock_bridge():
    with patch("bridge.mqtt.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        from bridge import Open3EBridge
        b = Open3EBridge(test_mode=True, add_test_prefix=False)
        yield b, mock_client


# --- _graceful_shutdown ---
def test_graceful_shutdown_publishes_offline(mock_bridge):
    bridge, mock_client = mock_bridge
    bridge._graceful_shutdown(signum=signal.SIGTERM)
    mock_client.publish.assert_any_call(bridge.lwt_topic, "offline", qos=1, retain=True)
    mock_client.disconnect.assert_called_once()


def test_graceful_shutdown_handles_exception(mock_bridge):
    bridge, mock_client = mock_bridge
    mock_client.publish.side_effect = Exception("connection lost")
    # Should not raise
    bridge._graceful_shutdown(signum=signal.SIGINT)


# --- _on_connect ---
def test_on_connect_subscribes_ha_status(mock_bridge):
    bridge, mock_client = mock_bridge
    bridge._on_connect(mock_client, None, {}, 0, None)
    subscribe_topics = [c[0][0] for c in mock_client.subscribe.call_args_list]
    assert "homeassistant/status" in subscribe_topics
    assert "open3e/+/+" in subscribe_topics


def test_on_connect_failure_logs_error(mock_bridge):
    bridge, mock_client = mock_bridge
    # Should not raise on failure code
    bridge._on_connect(mock_client, None, {}, 5, None)
    mock_client.publish.assert_not_called()


# --- _on_disconnect ---
def test_on_disconnect_clean(mock_bridge):
    bridge, mock_client = mock_bridge
    bridge._on_disconnect(mock_client, None, {}, 0, None)


def test_on_disconnect_unexpected(mock_bridge):
    bridge, mock_client = mock_bridge
    bridge._on_disconnect(mock_client, None, {}, 7, None)


# --- _on_message edge cases ---
def test_on_message_bridge_lwt_skipped(mock_bridge):
    bridge, mock_client = mock_bridge
    msg = FakeMessage("open3e/680_268_Foo/LWT", "online")
    bridge._on_message(mock_client, None, msg)
    mock_client.publish.assert_not_called()


def test_on_message_unknown_did_no_publish(mock_bridge):
    """Unknown DID (not in config) produces no discovery publish."""
    bridge, mock_client = mock_bridge
    msg = FakeMessage("open3e/680_99999_Unknown/Value", "not-json")
    bridge._on_message(mock_client, None, msg)
    mock_client.publish.assert_not_called()


# --- _republish_all_discovery ---
def test_republish_empty_cache(mock_bridge):
    bridge, mock_client = mock_bridge
    bridge.published_configs = {}
    bridge._republish_all_discovery()
    mock_client.publish.assert_not_called()


def test_republish_sends_all(mock_bridge):
    bridge, mock_client = mock_bridge
    bridge.published_configs = {
        "ha/sensor/a/config": '{"a":1}',
        "ha/sensor/b/config": '{"b":2}',
        "ha/sensor/c/config": '{"c":3}',
    }
    bridge._republish_all_discovery()
    assert mock_client.publish.call_count == 3


# --- main() paths ---
def test_main_validate_config():
    from bridge import main
    with patch("bridge.HomeAssistantGenerator") as MockGen, \
         patch("sys.argv", ["bridge", "--validate-config"]):
        MockGen.return_value.validate.return_value = {"errors": [], "warnings": []}
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_main_validate_config_fail():
    from bridge import main
    with patch("bridge.HomeAssistantGenerator") as MockGen, \
         patch("sys.argv", ["bridge", "--validate-config"]):
        MockGen.return_value.validate.return_value = {"errors": ["bad"], "warnings": []}
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_main_cleanup():
    from bridge import main
    with patch("bridge.Open3EBridge") as MockBridge, \
         patch("sys.argv", ["bridge", "--cleanup"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
        MockBridge.return_value.cleanup.assert_called_once()


# --- simulate_from_file ---
def test_simulate_from_file(tmp_path):
    from bridge import Open3EBridge, simulate_from_file
    test_file = tmp_path / "test.txt"
    test_file.write_text("# comment\nopen3e/680_268_FlowTemperatureSensor/Actual 42.5\n")

    with patch("bridge.mqtt.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        bridge = Open3EBridge(test_mode=True, add_test_prefix=False)
        with patch("bridge.time.sleep"):
            simulate_from_file(bridge, str(test_file))
        mock_client.connect.assert_called_once()
        assert mock_client.publish.called


def test_simulate_file_not_found():
    from bridge import Open3EBridge, simulate_from_file
    with patch("bridge.mqtt.Client") as MockClient:
        MockClient.return_value = MagicMock()
        bridge = Open3EBridge(test_mode=True, add_test_prefix=False)
        # Should not raise
        simulate_from_file(bridge, "/nonexistent/path.txt")


# --- Open3EBridge constructor options ---
def test_bridge_with_auth():
    with patch("bridge.mqtt.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        from bridge import Open3EBridge
        Open3EBridge(mqtt_user="user", mqtt_password="pass")
        mock_client.username_pw_set.assert_called_once_with("user", "pass")


def test_bridge_start_keyboard_interrupt():
    with patch("bridge.mqtt.Client") as MockClient:
        mock_client = MagicMock()
        mock_client.loop_forever.side_effect = KeyboardInterrupt()
        MockClient.return_value = mock_client
        from bridge import Open3EBridge
        b = Open3EBridge(test_mode=True)
        b.start()
        mock_client.disconnect.assert_called()


def test_bridge_start_generic_error():
    with patch("bridge.mqtt.Client") as MockClient:
        mock_client = MagicMock()
        mock_client.connect.side_effect = Exception("connection refused")
        MockClient.return_value = mock_client
        from bridge import Open3EBridge
        b = Open3EBridge(test_mode=True)
        with pytest.raises(SystemExit) as exc_info:
            b.start()
        assert exc_info.value.code == 1


# --- cleanup() ---

def test_cleanup_clears_matching_retained(mock_bridge):
    """cleanup() should publish empty payload for matching open3e topics."""
    bridge, mock_client = mock_bridge

    prefix = bridge.generator.discovery_prefix

    def fake_loop_start():
        # Simulate the _on_connect callback
        on_connect = bridge.client.on_connect
        on_connect(mock_client, None, {}, 0, None)

        # Simulate retained messages arriving via _on_message
        on_message = bridge.client.on_message
        matching = FakeMessage(
            f"{prefix}/sensor/open3e_680_268_actual/config", "payload", retain=True,
        )
        non_matching = FakeMessage(
            f"{prefix}/sensor/other_device/config", "payload", retain=True,
        )
        on_message(mock_client, None, matching)
        on_message(mock_client, None, non_matching)

    mock_client.loop_start.side_effect = fake_loop_start

    with patch("bridge.time.sleep"):
        bridge.cleanup()

    # Should subscribe to prefix/#
    mock_client.subscribe.assert_any_call(f"{prefix}/#")
    # Should clear matching topic
    mock_client.publish.assert_any_call(
        f"{prefix}/sensor/open3e_680_268_actual/config", payload="", retain=True,
    )
    # Should NOT clear non-matching topic
    clear_calls = [
        c for c in mock_client.publish.call_args_list
        if c[1].get("payload") == "" or (len(c[0]) > 1 and c[0][1] == "")
    ]
    clear_topics = [c[0][0] for c in clear_calls]
    assert f"{prefix}/sensor/other_device/config" not in clear_topics
    mock_client.disconnect.assert_called_once()


def test_cleanup_connect_failure(mock_bridge):
    """cleanup() with failed connection should not subscribe."""
    bridge, mock_client = mock_bridge

    def fake_loop_start():
        on_connect = bridge.client.on_connect
        on_connect(mock_client, None, {}, 5, None)

    mock_client.loop_start.side_effect = fake_loop_start

    with patch("bridge.time.sleep"):
        bridge.cleanup()

    mock_client.subscribe.assert_not_called()


# --- _on_message exception handlers ---

def test_on_message_json_decode_error_via_generator(mock_bridge):
    """JSONDecodeError in generator should be caught."""
    bridge, mock_client = mock_bridge
    bridge.generator.generate_discovery_message = MagicMock(
        side_effect=json.JSONDecodeError("bad json", "", 0),
    )
    msg = FakeMessage("open3e/680_268_Sensor/Actual", "42.5")
    bridge._on_message(mock_client, None, msg)
    # No crash, no publish
    mock_client.publish.assert_not_called()


def test_on_message_value_error_via_generator(mock_bridge):
    """ValueError in generator should be caught."""
    bridge, mock_client = mock_bridge
    bridge.generator.generate_discovery_message = MagicMock(
        side_effect=ValueError("bad value"),
    )
    msg = FakeMessage("open3e/680_268_Sensor/Actual", "42.5")
    bridge._on_message(mock_client, None, msg)
    mock_client.publish.assert_not_called()


def test_on_message_generic_exception_via_generator(mock_bridge):
    """Unexpected exception in generator should be caught."""
    bridge, mock_client = mock_bridge
    bridge.generator.generate_discovery_message = MagicMock(
        side_effect=RuntimeError("boom"),
    )
    msg = FakeMessage("open3e/680_268_Sensor/Actual", "42.5")
    bridge._on_message(mock_client, None, msg)
    mock_client.publish.assert_not_called()


# --- main() branches ---

def test_main_custom_discovery_prefix(tmp_path):
    """--discovery-prefix sets custom prefix."""
    from bridge import main
    test_file = tmp_path / "test.txt"
    test_file.write_text("open3e/680_268_Sensor/Actual 42\n")
    with patch("bridge.Open3EBridge") as mock_bridge_cls, \
         patch("bridge.simulate_from_file"), \
         patch("sys.argv", ["bridge", "--discovery-prefix", "custom", "--simulate", str(test_file)]):
        main()
        # Bridge should be created with custom prefix
        call_kwargs = mock_bridge_cls.call_args
        assert call_kwargs[1]["discovery_prefix"] == "custom" or call_kwargs.kwargs["discovery_prefix"] == "custom"


def test_main_test_flag_sets_test_prefix():
    """--test without --simulate uses test/homeassistant prefix."""
    from bridge import main
    with patch("bridge.Open3EBridge") as MockBridge, \
         patch("sys.argv", ["bridge", "--test"]):
        MockBridge.return_value.start = MagicMock()
        main()
        call_kwargs = MockBridge.call_args
        assert "test/" in (call_kwargs[1].get("discovery_prefix") or call_kwargs.kwargs.get("discovery_prefix", ""))


def test_main_simulate_calls_simulate_from_file(tmp_path):
    """--simulate should call simulate_from_file."""
    from bridge import main
    test_file = tmp_path / "test.txt"
    test_file.write_text("open3e/680_268_Sensor/Actual 42\n")
    with patch("bridge.Open3EBridge"), \
         patch("bridge.simulate_from_file") as mock_sim, \
         patch("sys.argv", ["bridge", "--simulate", str(test_file)]):
        main()
        mock_sim.assert_called_once()


def test_main_no_simulate_calls_start():
    """Without --simulate, main() calls bridge.start()."""
    from bridge import main
    with patch("bridge.Open3EBridge") as MockBridge, \
         patch("sys.argv", ["bridge"]):
        main()
        MockBridge.return_value.start.assert_called_once()


# --- simulate_from_file generic exception ---

def test_simulate_generic_exception():
    """Generic exception in simulate_from_file is caught."""
    from bridge import Open3EBridge, simulate_from_file
    with patch("bridge.mqtt.Client") as MockClient:
        mock_client = MagicMock()
        mock_client.connect.side_effect = RuntimeError("refused")
        MockClient.return_value = mock_client
        bridge = Open3EBridge(test_mode=True, add_test_prefix=False)
        # Should not raise
        simulate_from_file(bridge, "/some/file.txt")


# --- Branch: cleanup _on_message with retain=False (98->exit) ---

def test_cleanup_non_retained_message_ignored(mock_bridge):
    """Non-retained messages in cleanup are ignored."""
    bridge, mock_client = mock_bridge
    prefix = bridge.generator.discovery_prefix

    def fake_loop_start():
        on_connect = bridge.client.on_connect
        on_connect(mock_client, None, {}, 0, None)
        on_message = bridge.client.on_message
        # Send a non-retained message — should be ignored
        non_retained = FakeMessage(
            f"{prefix}/sensor/open3e_680_268_actual/config", "payload", retain=False,
        )
        on_message(mock_client, None, non_retained)

    mock_client.loop_start.side_effect = fake_loop_start

    with patch("bridge.time.sleep"):
        bridge.cleanup()

    # No matching retained topics found, so no clearing publishes
    clear_calls = [
        c for c in mock_client.publish.call_args_list
        if len(c[0]) > 1 and c[0][1] == ""
    ]
    assert clear_calls == []


# --- Branch: _on_message with test_mode=False (169->171) ---

def test_on_message_publishes_without_debug_in_non_test_mode():
    """Discovery is published when test_mode=False (no debug log branch)."""
    with patch("bridge.mqtt.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        from bridge import Open3EBridge
        bridge = Open3EBridge(test_mode=False, add_test_prefix=False)

    msg = FakeMessage("open3e/680_268_FlowTemperatureSensor/Actual", "42.5")
    bridge._on_message(mock_client, None, msg)
    # Should publish discovery even with test_mode=False
    assert mock_client.publish.called


# --- Branch: simulate_from_file with malformed line (283->276) ---

def test_simulate_malformed_line_skipped(tmp_path):
    """Lines without space separator are skipped in simulate."""
    from bridge import Open3EBridge, simulate_from_file
    test_file = tmp_path / "test.txt"
    test_file.write_text("no_space_here\nopen3e/680_268_Sensor/Actual 42.5\n")

    with patch("bridge.mqtt.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        bridge = Open3EBridge(test_mode=True, add_test_prefix=False)
        with patch("bridge.time.sleep"):
            simulate_from_file(bridge, str(test_file))
        # Should still process the valid line
        mock_client.connect.assert_called_once()
