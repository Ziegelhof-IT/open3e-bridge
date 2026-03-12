"""Tests for heating curve DIDs 880/881 (read-only)."""
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


class TestHeatingCurveDiscovery:
    """Heating curve entity generation."""

    def test_gradient_generates_sensor(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_880_MixerOneCircuitCentralHeatingCurve/Gradient"
        out = gen.generate_discovery_message(topic, "1.4", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "sensor" in out[0][0]
        assert data["state_class"] == "measurement"

    def test_level_generates_sensor_with_kelvin_unit(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_880_MixerOneCircuitCentralHeatingCurve/Level"
        out = gen.generate_discovery_message(topic, "-3", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert data["unit_of_measurement"] == "K"

    def test_circuit_2_gradient_works(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        topic = "open3e/680_881_MixerTwoCircuitCentralHeatingCurve/Gradient"
        out = gen.generate_discovery_message(topic, "0.8", test_mode=True)
        assert len(out) >= 1

    def test_heating_curve_not_writable(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dp = gen.datapoints["datapoints"][880]
        assert dp.get("writable") is None or dp.get("writable") is False


class TestHeatingCurveGerman:
    """German translations for heating curve."""

    def test_did_880_german_name(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="de", profile="vitocal")
        topic = "open3e/680_880_MixerOneCircuitCentralHeatingCurve/Gradient"
        out = gen.generate_discovery_message(topic, "1.4", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "Heizkurve" in data["name"]
