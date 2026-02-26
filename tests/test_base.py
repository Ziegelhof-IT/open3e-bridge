"""Comprehensive tests for BaseGenerator (TEST-CORE)."""
import pytest

from generators.base import BaseGenerator


# ---------------------------------------------------------------------------
# 1. parse_open3e_topic
# ---------------------------------------------------------------------------

class TestParseOpen3eTopic:
    """Tests for BaseGenerator.parse_open3e_topic."""

    def test_valid_topic_with_sub_item(self, generator_de):
        result = generator_de.parse_open3e_topic("open3e/680_268_FlowTemperatureSensor/Actual")
        assert result is not None
        assert result["ecu_addr"] == "680"
        assert result["did"] == 268
        assert result["sensor_name"] == "FlowTemperatureSensor"
        assert result["sub_item"] == "Actual"
        assert result["full_topic"] == "open3e/680_268_FlowTemperatureSensor/Actual"

    def test_valid_topic_without_sub_item(self, generator_de):
        result = generator_de.parse_open3e_topic("open3e/680_268_FlowTemperatureSensor")
        assert result is not None
        assert result["ecu_addr"] == "680"
        assert result["did"] == 268
        assert result["sensor_name"] == "FlowTemperatureSensor"
        assert result["sub_item"] is None

    def test_deep_path_sub_item(self, generator_en):
        """Deep paths like Mode/ID are joined with '/'."""
        result = generator_en.parse_open3e_topic(
            "open3e/680_1415_MixerOneCircuitOperationState/Mode/ID"
        )
        assert result is not None
        assert result["did"] == 1415
        assert result["sub_item"] == "Mode/ID"

    def test_invalid_prefix(self, generator_de):
        assert generator_de.parse_open3e_topic("other/680_268_Sensor/Actual") is None

    def test_no_underscores(self, generator_de):
        assert generator_de.parse_open3e_topic("open3e/nounderscores") is None

    def test_only_one_underscore(self, generator_de):
        """Need at least two underscores to split ecu_addr, did, name."""
        assert generator_de.parse_open3e_topic("open3e/680_268") is None

    def test_non_numeric_did(self, generator_de):
        assert generator_de.parse_open3e_topic("open3e/680_abc_Sensor/Actual") is None

    def test_empty_string(self, generator_de):
        assert generator_de.parse_open3e_topic("") is None

    def test_single_segment(self, generator_de):
        assert generator_de.parse_open3e_topic("open3e") is None

    def test_sensor_name_with_underscores(self, generator_de):
        """Underscores in sensor name after the first two splits are kept."""
        result = generator_de.parse_open3e_topic(
            "open3e/680_268_Some_Long_Name/Actual"
        )
        assert result is not None
        assert result["sensor_name"] == "Some_Long_Name"


# ---------------------------------------------------------------------------
# 2. validate
# ---------------------------------------------------------------------------

class TestValidate:
    """Tests for BaseGenerator.validate against real config."""

    def test_valid_config_has_no_errors(self, generator_de):
        result = generator_de.validate()
        assert result["errors"] == [], f"Unexpected errors: {result['errors']}"

    def test_valid_config_en_has_no_errors(self, generator_en):
        result = generator_en.validate()
        assert result["errors"] == []

    def test_detects_unknown_type(self, config_dir):
        gen = BaseGenerator(config_dir=config_dir, language="de")
        # Inject a datapoint with an unknown type
        gen.datapoints.setdefault("datapoints", {})[99999] = {"type": "nonexistent_type"}
        result = gen.validate()
        error_msgs = " ".join(result["errors"])
        assert "unknown type" in error_msgs

    def test_detects_missing_type(self, config_dir):
        gen = BaseGenerator(config_dir=config_dir, language="de")
        gen.datapoints.setdefault("datapoints", {})[99998] = {"name_key": "test"}
        result = gen.validate()
        error_msgs = " ".join(result["errors"])
        assert "missing 'type'" in error_msgs

    def test_detects_non_integer_key(self, config_dir):
        gen = BaseGenerator(config_dir=config_dir, language="de")
        gen.datapoints.setdefault("datapoints", {})["not_a_number"] = {
            "type": "temperature_sensor"
        }
        result = gen.validate()
        error_msgs = " ".join(result["errors"])
        assert "not an integer" in error_msgs

    def test_detects_non_numeric_min(self, config_dir):
        gen = BaseGenerator(config_dir=config_dir, language="de")
        gen.datapoints.setdefault("datapoints", {})[99997] = {
            "type": "temperature_sensor",
            "min": "not_a_number",
        }
        result = gen.validate()
        error_msgs = " ".join(result["errors"])
        assert "'min' must be number" in error_msgs

    def test_detects_invalid_options_type(self, config_dir):
        gen = BaseGenerator(config_dir=config_dir, language="de")
        gen.datapoints.setdefault("datapoints", {})[99996] = {
            "type": "temperature_sensor",
            "options": "should_be_a_list",
        }
        result = gen.validate()
        error_msgs = " ".join(result["errors"])
        assert "'options' must be a list" in error_msgs

    def test_detects_invalid_subs_options(self, config_dir):
        gen = BaseGenerator(config_dir=config_dir, language="de")
        gen.datapoints.setdefault("datapoints", {})[99995] = {
            "type": "temperature_sensor",
            "subs": {
                "Actual": {"type": "current", "min": "bad"},
            },
        }
        result = gen.validate()
        error_msgs = " ".join(result["errors"])
        assert "'min' must be number" in error_msgs
        assert "sub 'Actual'" in error_msgs

    def test_warning_for_missing_translation(self, config_dir):
        gen = BaseGenerator(config_dir=config_dir, language="de")
        gen.datapoints.setdefault("datapoints", {})[99994] = {
            "type": "temperature_sensor",
            "name_key": "totally_unknown_key",
        }
        result = gen.validate()
        warning_msgs = " ".join(result["warnings"])
        assert "totally_unknown_key" in warning_msgs

    def test_device_info_type_is_accepted(self, config_dir):
        """Type 'device_info' must not trigger 'unknown type' errors."""
        gen = BaseGenerator(config_dir=config_dir, language="de")
        gen.datapoints.setdefault("datapoints", {})[99993] = {
            "type": "device_info",
        }
        result = gen.validate()
        did_errors = [e for e in result["errors"] if "99993" in e]
        assert did_errors == []


# ---------------------------------------------------------------------------
# 3. update_device_info
# ---------------------------------------------------------------------------

class TestUpdateDeviceInfo:
    """Tests for BaseGenerator.update_device_info."""

    def test_cache_populated_for_identification_did(self, config_dir):
        gen = BaseGenerator(config_dir=config_dir, language="de")
        # DID 377 is in device_identification_dids in the real config
        gen.update_device_info("680", 377, "Vitocal 250-A HO2C")
        assert "680" in gen.device_cache
        info = gen.device_cache["680"]
        assert info["name"] == "Vitocal 250-A"
        assert info["model"] == "Vitocal 250-A"
        # DID 377 also extracts serial
        assert info["serial"] == "Vitocal 250-A HO2C"

    def test_cache_not_populated_for_non_identification_did(self, config_dir):
        gen = BaseGenerator(config_dir=config_dir, language="de")
        gen.update_device_info("680", 268, "some value")
        assert "680" not in gen.device_cache

    def test_multiple_ecus(self, config_dir):
        gen = BaseGenerator(config_dir=config_dir, language="de")
        gen.update_device_info("680", 377, "VX3-unit")
        gen.update_device_info("690", 377, "VDENS-unit")
        assert gen.device_cache["680"]["name"] == "Viessmann VX3"
        assert gen.device_cache["690"]["name"] == "Viessmann Vitodens"

    def test_fallback_when_no_pattern_matches(self, config_dir):
        gen = BaseGenerator(config_dir=config_dir, language="de")
        gen.update_device_info("680", 377, "UnknownModel XYZ-123")
        info = gen.device_cache["680"]
        # Fallback: cleaned value used directly
        assert "UnknownModel" in info["name"]


# ---------------------------------------------------------------------------
# 4. translate
# ---------------------------------------------------------------------------

class TestTranslate:
    """Tests for BaseGenerator.translate."""

    def test_returns_translated_value_de(self, generator_de):
        assert generator_de.translate("flow_temperature") == "Vorlauftemperatur"

    def test_returns_translated_value_en(self, generator_en):
        # English translation file should have its own value
        result = generator_en.translate("flow_temperature")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_key_as_fallback(self, generator_de):
        missing_key = "this_key_does_not_exist_anywhere"
        assert generator_de.translate(missing_key) == missing_key

    def test_suggested_area_de(self, generator_de):
        assert generator_de.translate("suggested_area") == "Heizung"


# ---------------------------------------------------------------------------
# 5. generate_entity_id
# ---------------------------------------------------------------------------

class TestGenerateEntityId:
    """Tests for BaseGenerator.generate_entity_id."""

    def test_basic_id(self, generator_de):
        result = generator_de.generate_entity_id("680", 268)
        assert result == "open3e_680_268"

    def test_with_sub_item(self, generator_de):
        result = generator_de.generate_entity_id("680", 268, "Actual")
        assert result == "open3e_680_268_actual"

    def test_unknown_sub_item_excluded(self, generator_de):
        """sub_item='Unknown' (case-insensitive) should be excluded."""
        assert generator_de.generate_entity_id("680", 268, "Unknown") == "open3e_680_268"
        assert generator_de.generate_entity_id("680", 268, "unknown") == "open3e_680_268"
        assert generator_de.generate_entity_id("680", 268, "UNKNOWN") == "open3e_680_268"

    def test_none_sub_item(self, generator_de):
        result = generator_de.generate_entity_id("680", 268, None)
        assert result == "open3e_680_268"

    def test_sub_item_with_slash(self, generator_de):
        """Slashes in sub_item are replaced with underscores."""
        result = generator_de.generate_entity_id("680", 1415, "Mode/ID")
        assert result == "open3e_680_1415_mode_id"

    def test_sub_item_with_spaces(self, generator_de):
        """Spaces and special chars are sanitized."""
        result = generator_de.generate_entity_id("680", 268, "Some Value")
        assert result == "open3e_680_268_some_value"

    def test_sub_item_special_characters(self, generator_de):
        result = generator_de.generate_entity_id("680", 268, "A-B.C")
        # Non-alphanumeric (except underscore) replaced by underscore
        assert result == "open3e_680_268_a_b_c"
