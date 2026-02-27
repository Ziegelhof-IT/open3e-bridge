"""Error handling edge-case tests (TEST-08)."""
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# 1. Malformed topics -> empty list
# ---------------------------------------------------------------------------

class TestMalformedTopics:

    @pytest.mark.parametrize("topic", [
        "",
        "not_open3e/foo",
        "open3e/invalid",
        "open3e/",
    ])
    def test_malformed_topic_returns_empty(self, generator_en, topic):
        result = generator_en.generate_discovery_message(topic, "42")
        assert result == []


# ---------------------------------------------------------------------------
# 2. Unknown DID -> empty list
# ---------------------------------------------------------------------------

class TestUnknownDid:

    def test_unknown_did_returns_empty(self, generator_en):
        result = generator_en.generate_discovery_message(
            "open3e/680_99999_UnknownSensor/Actual", "123"
        )
        assert result == []


# ---------------------------------------------------------------------------
# 3. Ignored DID -> empty list
# ---------------------------------------------------------------------------

class TestIgnoredDid:

    def test_ignored_did_540_returns_empty(self, generator_en):
        result = generator_en.generate_discovery_message(
            "open3e/680_540_SomeIgnoredSensor/Actual", "1"
        )
        assert result == []


# ---------------------------------------------------------------------------
# 4. Non-UTF-8 payload in bridge._on_message
# ---------------------------------------------------------------------------

class TestBridgeNonUtf8:

    def test_non_utf8_payload_does_not_raise(self):
        with patch("paho.mqtt.client.Client") as MockClient:
            MockClient.return_value = MagicMock()
            from bridge import Open3EBridge
            bridge = Open3EBridge(test_mode=True)

        msg = MagicMock()
        msg.topic = "open3e/680_268_FlowTemperatureSensor/Actual"
        msg.payload = b"\xff\xfe\x80\x81"  # invalid UTF-8

        # Should be caught by UnicodeDecodeError handler, not raise
        bridge._on_message(None, None, msg)


# ---------------------------------------------------------------------------
# 5. Empty payload -> no crash
# ---------------------------------------------------------------------------

class TestEmptyPayload:

    def test_empty_string_value_no_crash(self, generator_en):
        result = generator_en.generate_discovery_message(
            "open3e/680_268_FlowTemperatureSensor/Actual", ""
        )
        # Should not raise; may or may not produce output
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# 6. Missing sub_item for complex DID
# ---------------------------------------------------------------------------

class TestMissingSubItem:

    def test_complex_did_without_sub_item(self, generator_en):
        """DID 268 has subs defined but topic has no sub_item path."""
        result = generator_en.generate_discovery_message(
            "open3e/680_268_FlowTemperatureSensor", "22.5"
        )
        # Should not crash; generator decides whether to produce output
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# 7. _generate_typed_discovery edge cases
# ---------------------------------------------------------------------------

class TestTypedDiscoveryEdgeCases:

    def test_type_name_missing_returns_empty(self, generator_en):
        """Datapoint with type=None returns empty list (L88)."""
        # Inject a DID with no type
        generator_en.datapoints.setdefault("datapoints", {})[77771] = {
            "name": "Test Sensor",
        }
        result = generator_en.generate_discovery_message(
            "open3e/680_77771_TestSensor/Actual", "42",
        )
        assert result == []

    def test_type_template_not_found_returns_empty(self, generator_en):
        """Datapoint with unknown type template returns empty list (L92)."""
        generator_en.datapoints.setdefault("datapoints", {})[77772] = {
            "type": "nonexistent_type_xyz",
            "name": "Test Sensor",
        }
        result = generator_en.generate_discovery_message(
            "open3e/680_77772_TestSensor/Actual", "42",
        )
        assert result == []


# ---------------------------------------------------------------------------
# 8. Disabled sub-item branch (93->114)
# ---------------------------------------------------------------------------

class TestDisabledSubItem:

    def test_disabled_sub_returns_no_entity(self, generator_en):
        """Sub with enabled=False produces no discovery (93->114)."""
        generator_en.datapoints.setdefault("datapoints", {})[77773] = {
            "type": "temperature_sensor",
            "name": "Test Sensor",
            "subs": {
                "Actual": {"type": "current", "enabled": False},
            },
        }
        result = generator_en.generate_discovery_message(
            "open3e/680_77773_TestSensor/Actual", "42",
        )
        assert result == []


# ---------------------------------------------------------------------------
# 9. Climate config branch coverage (152-166)
# ---------------------------------------------------------------------------

class TestClimateConfigBranches:

    def test_climate_minimal_config(self, generator_en):
        """Climate with no optional templates or ranges (all False branches)."""
        generator_en.datapoints.setdefault("datapoints", {})[77774] = {
            "type": "select_mode",
            "name": "Test Climate",
            "subs": {
                "Mode/ID": {
                    "entity_type": "select",
                    "options": ["off", "auto"],
                },
            },
            "climate": {
                "name": "Test Climate",
                "trigger_sub": "Mode/ID",
                # No mode_state_template (152->154)
                # No mode_command_template (154->158)
                # No temperature_did / temperature_did_name (158->160)
                # No temperature_command_template (161->165)
                # No min_temp/max_temp/precision/temperature_unit (166->165)
            },
        }
        results = generator_en.generate_discovery_message(
            "open3e/680_77774_TestClimate/Mode/ID", "1",
        )
        # Should produce select + climate entities
        climate_results = [(t, p) for t, p in results if "/climate/" in t]
        assert len(climate_results) == 1
        import json
        config = json.loads(climate_results[0][1])
        assert "mode_state_template" not in config
        assert "mode_command_template" not in config
        assert "temperature_state_topic" not in config
        assert "temperature_command_template" not in config
        assert "min_temp" not in config


# ---------------------------------------------------------------------------
# 10. Writable entity with no min/max/step in dp_config or template (219->216)
# ---------------------------------------------------------------------------

class TestWritableNoMinMaxStep:

    def test_writable_without_min_max_step(self, generator_en):
        """Writable entity where min/max/step not in dp_config or template (219->216)."""
        generator_en.datapoints.setdefault("datapoints", {})[77775] = {
            "type": "generic_sensor",
            "name": "Test Writable",
            "writable": True,
            # No min, max, step here
        }
        # generic_sensor template also has no min/max/step
        results = generator_en.generate_discovery_message(
            "open3e/680_77775_TestWritable", "42",
        )
        assert len(results) == 1
        import json
        config = json.loads(results[0][1])
        assert "command_topic" in config
        assert "min" not in config
        assert "max" not in config
        assert "step" not in config
