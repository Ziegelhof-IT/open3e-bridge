"""Additional bridge.py tests to increase coverage."""
import signal
from unittest.mock import MagicMock, patch

import pytest


class FakeMessage:
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload if isinstance(payload, bytes) else payload.encode("utf-8")
        self.retain = False


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


def test_on_message_json_decode_error(mock_bridge):
    """Triggers ValueError path via a topic that parses but DID not in config."""
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
        # Should not raise
        b.start()
