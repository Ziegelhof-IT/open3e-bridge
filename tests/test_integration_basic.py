"""TEST-INT-BASIC: Basic integration tests with mocked MQTT broker."""
import json
import pytest
from unittest.mock import patch, MagicMock


class FakeMessage:
    """Simulates a paho-mqtt MQTTMessage."""

    def __init__(self, topic: str, payload: str):
        self.topic = topic
        self.payload = payload.encode("utf-8")


@pytest.fixture
def mock_bridge():
    with patch("bridge.mqtt.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        from bridge import Open3EBridge

        b = Open3EBridge(test_mode=True, add_test_prefix=False)
        yield b, mock_client


# ---------------------------------------------------------------------------
# 1. Temperature message triggers sensor discovery publish
# ---------------------------------------------------------------------------
def test_bridge_processes_temperature_message(mock_bridge):
    bridge, mock_client = mock_bridge

    msg = FakeMessage("open3e/680_268_FlowTemperatureSensor/Actual", "42.5")
    bridge._on_message(mock_client, None, msg)

    # At least one publish call with a discovery topic
    assert mock_client.publish.called
    calls = mock_client.publish.call_args_list
    discovery_call = [c for c in calls if "sensor/" in str(c)]
    assert len(discovery_call) >= 1, f"Expected sensor/ discovery, got: {calls}"

    # Inspect payload of first matching call
    _topic, payload_str = discovery_call[0][0][0], discovery_call[0][0][1]
    payload = json.loads(payload_str)
    assert payload["device_class"] == "temperature"


# ---------------------------------------------------------------------------
# 2. LWT messages are silently skipped
# ---------------------------------------------------------------------------
def test_bridge_skips_lwt_messages(mock_bridge):
    bridge, mock_client = mock_bridge

    msg = FakeMessage("open3e/LWT", "online")
    bridge._on_message(mock_client, None, msg)

    mock_client.publish.assert_not_called()


# ---------------------------------------------------------------------------
# 3. Discovery is only published once per config (caching)
# ---------------------------------------------------------------------------
def test_bridge_caches_discovery(mock_bridge):
    bridge, mock_client = mock_bridge

    msg = FakeMessage("open3e/680_268_FlowTemperatureSensor/Actual", "42.5")

    bridge._on_message(mock_client, None, msg)
    first_count = mock_client.publish.call_count

    bridge._on_message(mock_client, None, msg)
    second_count = mock_client.publish.call_count

    assert second_count == first_count, (
        f"Second message should not trigger additional publishes "
        f"(first={first_count}, second={second_count})"
    )


# ---------------------------------------------------------------------------
# 4. HA restart (homeassistant/status online) republishes all cached configs
# ---------------------------------------------------------------------------
def test_bridge_republish_on_ha_restart(mock_bridge):
    bridge, mock_client = mock_bridge

    # Pre-fill the cache with two fake discovery entries
    bridge.published_configs = {
        "homeassistant/sensor/open3e_680_268_actual/config": '{"name":"a"}',
        "homeassistant/sensor/open3e_680_274_actual/config": '{"name":"b"}',
    }

    msg = FakeMessage("homeassistant/status", "online")
    bridge._on_message(mock_client, None, msg)

    # All cached configs must be republished
    published_topics = [call[0][0] for call in mock_client.publish.call_args_list]
    for topic in bridge.published_configs:
        assert topic in published_topics, f"Expected {topic} to be republished"


# ---------------------------------------------------------------------------
# 5. Unknown DID causes no publish and no exception
# ---------------------------------------------------------------------------
def test_bridge_handles_unknown_did(mock_bridge):
    bridge, mock_client = mock_bridge

    msg = FakeMessage("open3e/680_99999_UnknownSensor/Value", "123")
    # Must not raise
    bridge._on_message(mock_client, None, msg)

    mock_client.publish.assert_not_called()
