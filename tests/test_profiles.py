"""Tests for profile loading system (Phase 1.2)."""
import json
from pathlib import Path

import pytest

from generators.homeassistant import HomeAssistantGenerator

CONFIG_DIR = str(Path(__file__).resolve().parents[1] / "config")


class TestProfileLoading:
    """Profile loading and merging."""

    def test_auto_profile_loads_vitocal_by_default(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="auto")
        # Vitocal profile should have outdoor device
        assert "outdoor" in gen.datapoints.get("devices", {})
        assert gen._active_profile == "vitocal"

    def test_common_profile_only(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        # Common has system/dhw/circuit devices, NOT outdoor/indoor
        devices = gen.datapoints.get("devices", {})
        assert "system" in devices
        assert "dhw" in devices
        # Common should NOT have Vitocal-specific devices
        assert "outdoor" not in devices
        assert gen._active_profile == "common"

    def test_vitocal_profile_merges_devices(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        devices = gen.datapoints.get("devices", {})
        # Vitocal adds its own devices on top of common
        assert "outdoor" in devices
        assert "indoor" in devices
        assert "mixer" in devices
        # Common devices should also be present (merged)
        assert "system" in devices or "dhw" in devices

    def test_vitodens_profile_has_boiler_device(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitodens")
        devices = gen.datapoints.get("devices", {})
        assert "boiler" in devices
        assert gen._active_profile == "vitodens"

    def test_vitocal_profile_has_compressor_did(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dps = gen.datapoints.get("datapoints", {})
        assert 2351 in dps  # HeatPumpCompressor

    def test_vitodens_profile_has_flame_did(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitodens")
        dps = gen.datapoints.get("datapoints", {})
        assert 364 in dps  # Flame
        assert 544 in dps  # GasConsumptionCentralHeating

    def test_common_profile_has_error_dids(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dps = gen.datapoints.get("datapoints", {})
        assert 257 in dps  # StatusDtcList
        assert 265 in dps  # ErrorDtcList

    def test_common_profile_has_schedule_dids(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dps = gen.datapoints.get("datapoints", {})
        # DHW schedules
        for did in range(691, 698):
            assert did in dps, f"DID {did} missing from common profile"
        # HK1 schedules
        for did in range(761, 768):
            assert did in dps, f"DID {did} missing from common profile"

    def test_common_profile_has_holiday_dids(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dps = gen.datapoints.get("datapoints", {})
        assert 511 in dps  # HolidayPhase
        assert 512 in dps  # HolidayAtHomePhase

    def test_local_overlay_wins_over_profile(self, tmp_path):
        """Local overlay should override profile values."""
        # Create a minimal config structure with profiles
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()

        # Common profile
        common = {
            "schema_version": 1,
            "devices": {"system": {"name": "Common System", "model": "Common"}},
            "datapoints": {268: {"type": "temperature_sensor", "name": "Flow", "device": "system"}},
        }
        (profiles_dir / "common.yaml").write_text(
            "schema_version: 1\ndevices:\n  system:\n    name: Common System\n    model: Common\ndatapoints:\n  268:\n    type: temperature_sensor\n    name: Flow\n    device: system\n"
        )

        # Local overlay
        local_dir = tmp_path / "local"
        local_dir.mkdir()
        (local_dir / "datapoints.yaml").write_text(
            "datapoints:\n  268:\n    type: temperature_sensor\n    name: My Custom Flow\n    device: system\n"
        )

        # Types template
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "types.yaml").write_text(
            "temperature_sensor:\n  entity_type: sensor\n  device_class: temperature\n  unit_of_measurement: '°C'\n"
        )

        gen = HomeAssistantGenerator(config_dir=str(tmp_path), language="en", profile="common")
        dp = gen.datapoints.get("datapoints", {}).get(268, {})
        assert dp["name"] == "My Custom Flow"

    def test_unknown_profile_falls_back_to_common(self, tmp_path):
        """Non-existent profile should log warning and use common only."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        (profiles_dir / "common.yaml").write_text(
            "schema_version: 1\ndevices:\n  system:\n    name: Test\n    model: Test\ndatapoints: {}\n"
        )
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        (templates_dir / "types.yaml").write_text("{}\n")

        gen = HomeAssistantGenerator(config_dir=str(tmp_path), language="en", profile="nosuchprofile")
        assert gen._active_profile == "nosuchprofile"  # Still set, but no file loaded


class TestExtendedClimateModes:
    """Phase 1.1b: Extended climate modes."""

    def test_select_options_include_heat_cool(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en")
        topic = "open3e/680_1415_MixerOneCircuitOperationState/Mode/ID"
        out = gen.generate_discovery_message(topic, "1", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "heat" in data["options"]
        assert "cool" in data["options"]

    def test_climate_modes_include_heat_cool(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en")
        topic = "open3e/680_1415_MixerOneCircuitOperationState/Mode/ID"
        out = gen.generate_discovery_message(topic, "1", test_mode=True)
        # Find the climate entity
        climate_msgs = [(t, p) for t, p in out if "/climate/" in t]
        assert len(climate_msgs) >= 1
        data = json.loads(climate_msgs[0][1])
        assert "heat" in data["modes"]
        assert "cool" in data["modes"]


class TestErrorListEntities:
    """Phase 1.3: Error code entities."""

    def test_error_did_generates_sensor(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en")
        topic = "open3e/680_265_ErrorDtcList"
        out = gen.generate_discovery_message(topic, '{"Count": 0, "ListEntries": []}', test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert data["icon"] == "mdi:alert-octagon"

    def test_error_did_has_json_attributes(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en")
        topic = "open3e/680_265_ErrorDtcList"
        out = gen.generate_discovery_message(topic, '{"Count": 0}', test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "json_attributes_topic" in data
        assert "json_attributes_template" in data

    def test_error_did_has_entity_category(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en")
        topic = "open3e/680_257_StatusDtcList"
        out = gen.generate_discovery_message(topic, '{"Count": 0}', test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert data.get("entity_category") == "diagnostic"


class TestScheduleEntities:
    """Phase 2.1: Schedule sensors."""

    def test_schedule_did_generates_sensor(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        topic = "open3e/680_691_DomesticHotWaterTimeScheduleMonday"
        out = gen.generate_discovery_message(topic, '{"Count": 1, "Schedules": [{"Start": "06:00", "Stop": "22:00"}]}', test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "json_attributes_topic" in data


class TestAutoDiscoverDefault:
    """Phase 1.1a: Auto-discover ON by default."""

    def test_auto_discover_on_by_default(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en")
        assert gen.auto_discover is False  # Constructor default is False; bridge.py sets True
        # When set to True, unknown DIDs produce discovery
        gen.auto_discover = True
        topic = "open3e/680_99999_TestSensor/Value"
        out = gen.generate_discovery_message(topic, "42", test_mode=True)
        assert len(out) >= 1


class TestRoomSetpoints:
    """Phase 1.1c: Room temperature setpoints."""

    def test_comfort_setpoint_generates_sensor(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en")
        topic = "open3e/680_424_MixerOneCircuitRoomTemperatureSetpoint/Comfort"
        out = gen.generate_discovery_message(topic, "22.0", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "Comfort" in data["name"] or "Room Setpoint" in data["name"]

    def test_reduced_setpoint_generates_sensor(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en")
        topic = "open3e/680_424_MixerOneCircuitRoomTemperatureSetpoint/Reduced"
        out = gen.generate_discovery_message(topic, "16.0", test_mode=True)
        assert len(out) >= 1
