"""Tests verifying all Phase 1 fixes are correctly applied (TEST-P1)."""
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

import paho.mqtt.client as mqtt
import pytest


# ---------------------------------------------------------------------------
# 1. paho v2: Client constructed with CallbackAPIVersion.VERSION2
# ---------------------------------------------------------------------------
class TestPahoV2:
    @patch("bridge.mqtt.Client")
    def test_client_uses_callback_api_v2(self, mock_client_cls):
        from bridge import Open3EBridge
        Open3EBridge()
        mock_client_cls.assert_called_once_with(mqtt.CallbackAPIVersion.VERSION2)


# ---------------------------------------------------------------------------
# 2. default_entity_id: discovery config uses default_entity_id, not object_id
# ---------------------------------------------------------------------------
class TestDefaultEntityId:
    def test_sensor_config_has_default_entity_id(self, generator_de):
        topic = "open3e/680_274_OutsideTemperatureSensor/Actual"
        results = generator_de.generate_discovery_message(topic, "12.5", test_mode=False)
        assert results, "Expected at least one discovery message"
        config = json.loads(results[0][1])
        assert "default_entity_id" in config
        assert "object_id" not in config


# ---------------------------------------------------------------------------
# 3. LWT: will_set called; _on_connect publishes "online"
# ---------------------------------------------------------------------------
class TestLWT:
    @patch("bridge.mqtt.Client")
    def test_will_set_called(self, mock_client_cls):
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance
        from bridge import Open3EBridge
        Open3EBridge()
        mock_instance.will_set.assert_called_once_with(
            "open3e/bridge/LWT", "offline", qos=1, retain=True
        )

    @patch("bridge.mqtt.Client")
    def test_on_connect_publishes_online(self, mock_client_cls):
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance
        from bridge import Open3EBridge
        bridge = Open3EBridge()
        # Simulate successful connect callback (paho v2 signature)
        bridge._on_connect(mock_instance, None, {}, 0, None)
        mock_instance.publish.assert_any_call(
            "open3e/bridge/LWT", "online", qos=1, retain=True
        )


# ---------------------------------------------------------------------------
# 4. origin: discovery config contains origin block
# ---------------------------------------------------------------------------
class TestOrigin:
    def test_discovery_contains_origin(self, generator_de):
        topic = "open3e/680_274_OutsideTemperatureSensor/Actual"
        results = generator_de.generate_discovery_message(topic, "12.5", test_mode=False)
        assert results
        config = json.loads(results[0][1])
        origin = config.get("origin")
        assert origin is not None, "Missing 'origin' in discovery config"
        assert "name" in origin
        assert "sw_version" in origin
        assert "support_url" in origin


# ---------------------------------------------------------------------------
# 5. hex fix: DID 1102 command_template uses %02x, not %0x
# ---------------------------------------------------------------------------
class TestHexFix:
    def test_did_1102_uses_02x_format(self, config_dir):
        dp_path = Path(config_dir) / "datapoints.yaml"
        content = dp_path.read_text(encoding="utf-8")
        # Must contain the correct two-digit hex format specifier
        assert "%02x" in content, "datapoints.yaml should contain '%02x'"
        # Must NOT contain the broken single-digit format specifier
        # Match '%0x' that is NOT preceded by '2' (i.e. not part of '%02x')
        import re
        broken = re.findall(r"(?<!2)%0x", content)
        assert not broken, f"Found broken hex format '%0x' in datapoints.yaml"
