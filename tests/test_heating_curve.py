"""Tests for heating curve DIDs 880/881 (writable number entities)."""
import json
from pathlib import Path

from generators.homeassistant import HomeAssistantGenerator

CONFIG_DIR = str(Path(__file__).resolve().parents[1] / "config")


class TestHeatingCurveConfig:
    """Heating curve DID configuration."""

    def test_did_880_exists_in_vitocal(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dps = gen.datapoints.get("datapoints", {})
        assert 880 in dps

    def test_did_881_exists_in_vitocal(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dps = gen.datapoints.get("datapoints", {})
        assert 881 in dps

    def test_did_880_not_in_common(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dps = gen.datapoints.get("datapoints", {})
        assert 880 not in dps

    def test_did_880_has_gradient_and_level_subs(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dp = gen.datapoints["datapoints"][880]
        subs = dp.get("subs", {})
        assert "Gradient" in subs
        assert "Level" in subs

    def test_gradient_sub_is_writable_number(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dp = gen.datapoints["datapoints"][880]
        grad = dp["subs"]["Gradient"]
        assert grad["entity_type"] == "number"
        assert grad["writable"] is True
        assert grad["min"] == 0.1
        assert grad["max"] == 3.5
        assert grad["step"] == 0.1

    def test_level_sub_is_writable_number(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dp = gen.datapoints["datapoints"][880]
        lvl = dp["subs"]["Level"]
        assert lvl["entity_type"] == "number"
        assert lvl["writable"] is True
        assert lvl["min"] == -15
        assert lvl["max"] == 40
        assert lvl["step"] == 1


class TestHeatingCurveDiscovery:
    """Heating curve entity generation."""

    def test_gradient_generates_number_entity(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_880_MixerOneCircuitCentralHeatingCurve/Gradient"
        out = gen.generate_discovery_message(topic, "1.4", test_mode=True)
        assert len(out) >= 1
        disc_topic, payload = out[0]
        data = json.loads(payload)
        assert "number" in disc_topic
        assert data.get("command_topic") == "open3e/cmnd"
        assert "command_template" in data
        assert data["min"] == 0.1
        assert data["max"] == 3.5
        assert data["step"] == 0.1

    def test_level_generates_number_with_kelvin_unit(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_880_MixerOneCircuitCentralHeatingCurve/Level"
        out = gen.generate_discovery_message(topic, "-3", test_mode=True)
        assert len(out) >= 1
        disc_topic, payload = out[0]
        data = json.loads(payload)
        assert "number" in disc_topic
        assert data["unit_of_measurement"] == "K"
        assert data.get("command_topic") == "open3e/cmnd"
        assert data["min"] == -15
        assert data["max"] == 40

    def test_gradient_command_template_encodes_write_raw(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_880_MixerOneCircuitCentralHeatingCurve/Gradient"
        out = gen.generate_discovery_message(topic, "1.4", test_mode=True)
        data = json.loads(out[0][1])
        tmpl = data["command_template"]
        assert "write-raw" in tmpl
        assert "880" in tmpl

    def test_level_command_template_encodes_write_raw(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_880_MixerOneCircuitCentralHeatingCurve/Level"
        out = gen.generate_discovery_message(topic, "0", test_mode=True)
        data = json.loads(out[0][1])
        tmpl = data["command_template"]
        assert "write-raw" in tmpl
        assert "880" in tmpl

    def test_circuit_2_gradient_generates_number(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_881_MixerTwoCircuitCentralHeatingCurve/Gradient"
        out = gen.generate_discovery_message(topic, "0.8", test_mode=True)
        assert len(out) >= 1
        disc_topic = out[0][0]
        assert "number" in disc_topic

    def test_circuit_2_level_generates_number(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_881_MixerTwoCircuitCentralHeatingCurve/Level"
        out = gen.generate_discovery_message(topic, "2", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "number" in out[0][0]
        assert data["unit_of_measurement"] == "K"


class TestHeatingCurveGerman:
    """German translations for heating curve."""

    def test_did_880_german_name(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="de", profile="vitocal")
        topic = "open3e/680_880_MixerOneCircuitCentralHeatingCurve/Gradient"
        out = gen.generate_discovery_message(topic, "1.4", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "Heizkurve" in data["name"]


class TestHeatingCurveSole:
    """Vitocal-sole profile inherits heating curve from vitocal."""

    def test_did_880_exists_in_vitocal_sole(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal-sole")
        dps = gen.datapoints.get("datapoints", {})
        assert 880 in dps

    def test_sole_gradient_is_writable(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal-sole")
        dp = gen.datapoints["datapoints"][880]
        assert dp["subs"]["Gradient"]["writable"] is True
