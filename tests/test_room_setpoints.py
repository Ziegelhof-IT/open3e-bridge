"""Tests for room temperature setpoint DIDs 424/426 (writable number entities)."""
import json
from pathlib import Path

from generators.homeassistant import HomeAssistantGenerator

CONFIG_DIR = str(Path(__file__).resolve().parents[1] / "config")


class TestRoomSetpointConfig:
    """Room setpoint DID configuration."""

    def test_did_424_exists_in_vitocal(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dps = gen.datapoints.get("datapoints", {})
        assert 424 in dps

    def test_did_426_exists_in_vitocal(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dps = gen.datapoints.get("datapoints", {})
        assert 426 in dps

    def test_did_424_not_in_common(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dps = gen.datapoints.get("datapoints", {})
        assert 424 not in dps

    def test_did_424_has_three_subs(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dp = gen.datapoints["datapoints"][424]
        subs = dp.get("subs", {})
        assert "Comfort" in subs
        assert "Standard" in subs
        assert "Reduced" in subs

    def test_comfort_sub_is_writable_number(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dp = gen.datapoints["datapoints"][424]
        comfort = dp["subs"]["Comfort"]
        assert comfort["entity_type"] == "number"
        assert comfort["writable"] is True
        assert comfort["min"] == 3
        assert comfort["max"] == 37
        assert comfort["step"] == 0.5

    def test_standard_sub_is_writable_number(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dp = gen.datapoints["datapoints"][424]
        standard = dp["subs"]["Standard"]
        assert standard["entity_type"] == "number"
        assert standard["writable"] is True

    def test_reduced_sub_is_writable_number(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dp = gen.datapoints["datapoints"][424]
        reduced = dp["subs"]["Reduced"]
        assert reduced["entity_type"] == "number"
        assert reduced["writable"] is True


class TestRoomSetpointDiscovery:
    """Room setpoint entity generation."""

    def test_comfort_generates_number_entity(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_424_MixerOneCircuitRoomTemperatureSetpoint/Comfort"
        out = gen.generate_discovery_message(topic, "22.0", test_mode=True)
        assert len(out) >= 1
        disc_topic, payload = out[0]
        data = json.loads(payload)
        assert "number" in disc_topic
        assert data.get("command_topic") == "open3e/cmnd"
        assert data["min"] == 3
        assert data["max"] == 37
        assert data["step"] == 0.5
        assert data["unit_of_measurement"] == "°C"

    def test_comfort_command_template_contains_write_raw(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_424_MixerOneCircuitRoomTemperatureSetpoint/Comfort"
        out = gen.generate_discovery_message(topic, "22.0", test_mode=True)
        data = json.loads(out[0][1])
        assert "write-raw" in data["command_template"]
        assert "424" in data["command_template"]

    def test_standard_generates_number_entity(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_424_MixerOneCircuitRoomTemperatureSetpoint/Standard"
        out = gen.generate_discovery_message(topic, "20.0", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "number" in out[0][0]

    def test_reduced_generates_number_entity(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_424_MixerOneCircuitRoomTemperatureSetpoint/Reduced"
        out = gen.generate_discovery_message(topic, "16.0", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "number" in out[0][0]

    def test_circuit_2_comfort_generates_number(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_426_MixerTwoCircuitRoomTemperatureSetpoint/Comfort"
        out = gen.generate_discovery_message(topic, "22.0", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "number" in out[0][0]
        assert "426" in data["command_template"]


class TestRoomSetpointGerman:
    """German translations for room setpoints."""

    def test_did_424_german_comfort(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="de", profile="vitocal")
        topic = "open3e/680_424_MixerOneCircuitRoomTemperatureSetpoint/Comfort"
        out = gen.generate_discovery_message(topic, "22.0", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        # Should contain translated name
        assert "Solltemperatur" in data["name"] or "Raumsolltemperatur" in data["name"] or "Setpoint" in data["name"]
