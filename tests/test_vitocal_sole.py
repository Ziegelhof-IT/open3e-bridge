"""Tests for Vitocal ground-source (Sole-Wasser) profile."""
import json
from pathlib import Path

from generators.homeassistant import HomeAssistantGenerator

CONFIG_DIR = str(Path(__file__).resolve().parents[1] / "config")


class TestVitocalSoleProfileLoading:
    """Profile chaining: common → vitocal → vitocal-sole."""

    def test_sole_profile_loads(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal-sole")
        assert gen._active_profile == "vitocal-sole"

    def test_sole_profile_inherits_vitocal_devices(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal-sole")
        devices = gen.datapoints.get("devices", {})
        # Should have vitocal devices (indoor, tank, mixer, etc.)
        assert "indoor" in devices
        assert "tank" in devices
        assert "mixer" in devices

    def test_sole_profile_overrides_outdoor_device(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal-sole")
        devices = gen.datapoints.get("devices", {})
        assert "outdoor" in devices
        assert "Ground Source" in devices["outdoor"]["name"]

    def test_sole_profile_has_vitocal_dids(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal-sole")
        dps = gen.datapoints.get("datapoints", {})
        # Vitocal-specific DIDs should be inherited
        assert 2351 in dps  # HeatPumpCompressor
        assert 2496 in dps  # ThermalPower
        assert 880 in dps   # HeatingCurve


class TestBrineTemperature:
    """DID 320 as brine temperature on ground-source."""

    def test_did_320_is_brine_temp(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal-sole")
        dp = gen.datapoints["datapoints"][320]
        assert dp["name"] == "Brine Temperature"

    def test_did_320_generates_sensor(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal-sole")
        topic = "open3e/680_320_PrimaryHeatExchangerLiquidTemperatureSensor/Actual"
        out = gen.generate_discovery_message(topic, "5.2", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "Brine" in data["name"]

    def test_did_320_german_label(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="de", profile="vitocal-sole")
        topic = "open3e/680_320_PrimaryHeatExchangerLiquidTemperatureSensor/Actual"
        out = gen.generate_discovery_message(topic, "5.2", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "Sole" in data["name"]


class TestAirSourceDIDsHidden:
    """Air-source-only DIDs hidden on ground-source profile."""

    def test_fan_did_1775_is_device_info(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal-sole")
        dp = gen.datapoints["datapoints"][1775]
        assert dp["type"] == "device_info"

    def test_fan_did_1776_is_device_info(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal-sole")
        dp = gen.datapoints["datapoints"][1776]
        assert dp["type"] == "device_info"


class TestBaseProfileChaining:
    """base_profile feature in profile loader."""

    def test_vitocal_has_no_base_profile(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        # Vitocal loads directly, no chaining
        assert gen._active_profile == "vitocal"

    def test_sole_chains_through_vitocal(self):
        gen_sole = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal-sole")
        gen_vitocal = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        # Sole should have all vitocal DIDs plus its own overrides
        sole_dps = set(gen_sole.datapoints.get("datapoints", {}).keys())
        vitocal_dps = set(gen_vitocal.datapoints.get("datapoints", {}).keys())
        assert vitocal_dps.issubset(sole_dps)
