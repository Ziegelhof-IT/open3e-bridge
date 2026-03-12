"""Tests for the bridge health entity (binary_sensor with diagnostic attributes)."""
import json
from unittest.mock import MagicMock, patch

import pytest


class FakeMessage:
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload.encode("utf-8") if isinstance(payload, str) else payload


@pytest.fixture
def mock_bridge():
    with patch("bridge.mqtt.Client") as MockClient:
        mock_client = MagicMock()
        MockClient.return_value = mock_client
        from bridge import Open3EBridge
        b = Open3EBridge(test_mode=True, add_test_prefix=False)
        yield b, mock_client


def test_health_discovery_published_on_connect(mock_bridge):
    """Health entity discovery is published when bridge connects."""
    bridge, mock_client = mock_bridge
    bridge._on_connect(mock_client, None, {}, 0, None)

    calls = mock_client.publish.call_args_list
    health_calls = [c for c in calls if "binary_sensor/open3e_bridge_status/config" in str(c)]
    assert len(health_calls) >= 1, f"Expected health discovery, got: {[str(c) for c in calls]}"

    # Verify payload structure
    payload = json.loads(health_calls[0][0][1])
    assert payload["device_class"] == "connectivity"
    assert payload["entity_category"] == "diagnostic"
    assert payload["json_attributes_topic"] == "open3e/bridge/health/attributes"
    assert payload["unique_id"] == "open3e_bridge_status"


def test_health_state_published_on_connect(mock_bridge):
    """Health state 'ON' is published when bridge connects."""
    bridge, mock_client = mock_bridge
    bridge._on_connect(mock_client, None, {}, 0, None)

    calls = mock_client.publish.call_args_list
    state_calls = [c for c in calls if c[0][0] == "open3e/bridge/health"]
    assert len(state_calls) >= 1
    assert state_calls[0][0][1] == "ON"


def test_health_attributes_published_on_connect(mock_bridge):
    """Health attributes JSON is published when bridge connects."""
    bridge, mock_client = mock_bridge
    bridge._on_connect(mock_client, None, {}, 0, None)

    calls = mock_client.publish.call_args_list
    attr_calls = [c for c in calls if c[0][0] == "open3e/bridge/health/attributes"]
    assert len(attr_calls) >= 1

    attrs = json.loads(attr_calls[0][0][1])
    assert "version" in attrs
    assert "uptime_s" in attrs
    assert "failed_writes" in attrs
    assert "last_error" in attrs
    assert attrs["failed_writes"] == 0


def test_health_updated_on_write_failure(mock_bridge):
    """Health entity is updated when write verification fails."""
    bridge, mock_client = mock_bridge
    # Simulate a pending write
    bridge._pending_writes[("680", 396)] = "50.0"
    # Read-back with different value
    bridge._check_write_verification("680", 396, "45.0")

    assert bridge._failed_writes == 1
    assert "FAILED" in bridge._last_error

    # Health state should have been published
    calls = mock_client.publish.call_args_list
    health_calls = [c for c in calls if c[0][0] == "open3e/bridge/health"]
    assert len(health_calls) >= 1


def test_health_updated_on_nrc(mock_bridge):
    """Health entity is updated when NRC is detected."""
    bridge, mock_client = mock_bridge
    bridge._handle_nrc("open3e/680_396_DHW/Actual", "NRC 0x22")

    assert "NRC" in bridge._last_error
    assert "ConditionsNotCorrect" in bridge._last_error


def test_health_attributes_contain_error_context(mock_bridge):
    """Health attributes contain actionable error information."""
    bridge, mock_client = mock_bridge
    bridge._pending_writes[("680", 396)] = "50.0"
    bridge._check_write_verification("680", 396, "45.0")

    calls = mock_client.publish.call_args_list
    attr_calls = [c for c in calls if c[0][0] == "open3e/bridge/health/attributes"]
    assert len(attr_calls) >= 1

    attrs = json.loads(attr_calls[-1][0][1])
    assert attrs["failed_writes"] == 1
    assert "FAILED" in attrs["last_error"]
    assert "range" in attrs["last_error"].lower() or "rejected" in attrs["last_error"].lower()


def test_diagnostics_include_health_fields(mock_bridge):
    """get_diagnostics includes failed_writes and last_error."""
    bridge, _ = mock_bridge
    diag = bridge.get_diagnostics()
    assert "failed_writes" in diag
    assert "last_error" in diag
    assert diag["failed_writes"] == 0
    assert diag["last_error"] == "none"


def test_health_publish_exception_handled(mock_bridge):
    """_publish_health_state handles MQTT publish failures gracefully."""
    bridge, mock_client = mock_bridge
    mock_client.publish.side_effect = Exception("not connected")
    # Should not raise
    bridge._publish_health_state("ON", error="test error")
