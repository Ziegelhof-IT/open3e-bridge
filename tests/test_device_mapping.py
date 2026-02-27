"""Tests for per-DID device mapping (physical device separation in HA)."""
import json

from generators.base import BaseGenerator


class TestDeviceInfoForDid:
    """Tests for BaseGenerator.create_device_info_for_did."""

    def test_known_device_key_returns_correct_identifier(self, generator_en):
        """DID with device: 'tank' → identifier open3e_680_tank."""
        info = generator_en.create_device_info_for_did("680", 271)
        assert info["identifiers"] == ["open3e_680_tank"]
        assert info["name"] == "Vitocell 100-E Hot Water Tank"
        assert info["model"] == "Vitocell 100-E"
        assert info["manufacturer"] == "Viessmann"

    def test_outdoor_device(self, generator_en):
        info = generator_en.create_device_info_for_did("680", 274)
        assert info["identifiers"] == ["open3e_680_outdoor"]
        assert info["name"] == "Vitocal 250-A Outdoor Unit"
        assert info["model"] == "Vitocal 250-A"

    def test_mixer_device(self, generator_en):
        info = generator_en.create_device_info_for_did("680", 284)
        assert info["identifiers"] == ["open3e_680_mixer"]
        assert info["name"] == "Heating Circuit Mixer"

    def test_heater_device(self, generator_en):
        info = generator_en.create_device_info_for_did("680", 2626)
        assert info["identifiers"] == ["open3e_680_heater"]
        assert info["name"] == "Auxiliary Heater"

    def test_energy_device(self, generator_en):
        info = generator_en.create_device_info_for_did("680", 1603)
        assert info["identifiers"] == ["open3e_680_energy"]
        assert info["name"] == "Energy Management"

    def test_indoor_device(self, generator_en):
        info = generator_en.create_device_info_for_did("680", 268)
        assert info["identifiers"] == ["open3e_680_indoor"]
        assert info["name"] == "Vitocal 252-A Indoor Unit"

    def test_fallback_for_unknown_did(self, generator_en):
        """DID not in datapoints → falls back to create_device_info."""
        info = generator_en.create_device_info_for_did("680", 99999)
        # Should fall back to default device (no device key)
        assert "open3e_680" in info["identifiers"]

    def test_suggested_area_en(self, generator_en):
        info = generator_en.create_device_info_for_did("680", 271)
        assert info["suggested_area"] == "Heating"

    def test_suggested_area_de(self, generator_de):
        info = generator_de.create_device_info_for_did("680", 271)
        assert info["suggested_area"] == "Heizung"


class TestDeviceNameTranslation:
    """Tests for device name translation (DE overlay)."""

    def test_tank_name_de(self, generator_de):
        info = generator_de.create_device_info_for_did("680", 271)
        assert info["name"] == "Vitocell 100-E Warmwasserspeicher"

    def test_outdoor_name_de(self, generator_de):
        info = generator_de.create_device_info_for_did("680", 274)
        assert info["name"] == "Vitocal 250-A Ausseneinheit"

    def test_mixer_name_de(self, generator_de):
        info = generator_de.create_device_info_for_did("680", 284)
        assert info["name"] == "Heizkreismischer"

    def test_heater_name_de(self, generator_de):
        info = generator_de.create_device_info_for_did("680", 2626)
        assert info["name"] == "Zusatzheizung"

    def test_energy_name_de(self, generator_de):
        info = generator_de.create_device_info_for_did("680", 1603)
        assert info["name"] == "Energiemanagement"

    def test_indoor_name_de(self, generator_de):
        info = generator_de.create_device_info_for_did("680", 268)
        assert info["name"] == "Vitocal 252-A Inneneinheit"

    def test_translate_device_name_passthrough_en(self, generator_en):
        assert generator_en.translate_device_name("Foo") == "Foo"

    def test_translate_device_name_unknown_de(self, generator_de):
        """Unknown device name falls back to English."""
        assert generator_de.translate_device_name("Unknown Device") == "Unknown Device"


class TestDiscoveryDeviceMapping:
    """Verify that discovery messages use per-DID device info."""

    def test_discovery_tank_device(self, generator_en):
        """DID 271 (tank) discovery message has tank device identifiers."""
        msgs = generator_en.generate_discovery_message(
            "open3e/680_271_DomesticHotWaterSensor/Actual", "52.1"
        )
        assert len(msgs) >= 1
        payload = json.loads(msgs[0][1])
        assert payload["device"]["identifiers"] == ["open3e_680_tank"]
        assert payload["device"]["name"] == "Vitocell 100-E Hot Water Tank"

    def test_discovery_outdoor_device(self, generator_en):
        """DID 274 (outdoor) discovery message has outdoor device."""
        msgs = generator_en.generate_discovery_message(
            "open3e/680_274_OutsideTemperatureSensor/Actual", "8.5"
        )
        assert len(msgs) >= 1
        payload = json.loads(msgs[0][1])
        assert payload["device"]["identifiers"] == ["open3e_680_outdoor"]

    def test_discovery_mixer_device_de(self, generator_de):
        """DID 284 (mixer) in DE has translated device name."""
        msgs = generator_de.generate_discovery_message(
            "open3e/680_284_MixerOneCircuitFlowTemperatureSensor/Actual", "35.0"
        )
        assert len(msgs) >= 1
        payload = json.loads(msgs[0][1])
        assert payload["device"]["identifiers"] == ["open3e_680_mixer"]
        assert payload["device"]["name"] == "Heizkreismischer"

    def test_different_dids_same_device(self, generator_en):
        """Multiple DIDs on same device share the same identifier."""
        msgs_271 = generator_en.generate_discovery_message(
            "open3e/680_271_DomesticHotWaterSensor/Actual", "52.1"
        )
        msgs_396 = generator_en.generate_discovery_message(
            "open3e/680_396_DomesticHotWaterTemperatureSetpoint", "50.0"
        )
        dev_271 = json.loads(msgs_271[0][1])["device"]
        dev_396 = json.loads(msgs_396[0][1])["device"]
        assert dev_271["identifiers"] == dev_396["identifiers"]
        assert dev_271["identifiers"] == ["open3e_680_tank"]

    def test_different_devices_different_identifiers(self, generator_en):
        """DIDs on different devices have distinct identifiers."""
        msgs_tank = generator_en.generate_discovery_message(
            "open3e/680_271_DomesticHotWaterSensor/Actual", "52.1"
        )
        msgs_outdoor = generator_en.generate_discovery_message(
            "open3e/680_274_OutsideTemperatureSensor/Actual", "8.5"
        )
        dev_tank = json.loads(msgs_tank[0][1])["device"]["identifiers"]
        dev_outdoor = json.loads(msgs_outdoor[0][1])["device"]["identifiers"]
        assert dev_tank != dev_outdoor


class TestDeviceValidation:
    """Tests for device: key validation."""

    def test_valid_config_no_device_errors(self, generator_en):
        result = generator_en.validate()
        device_errors = [e for e in result["errors"] if "device" in e.lower()]
        assert device_errors == [], f"Unexpected device errors: {device_errors}"

    def test_invalid_device_ref_detected(self, generator_en):
        """Injecting an invalid device ref should produce a validation error."""
        # Temporarily inject bad config
        generator_en.datapoints["datapoints"][99998] = {
            "type": "temperature_sensor",
            "name": "Test Bad Device",
            "device": "nonexistent",
        }
        result = generator_en.validate()
        device_errors = [e for e in result["errors"] if "99998" in e and "device" in e.lower()]
        assert len(device_errors) == 1
        # Cleanup
        del generator_en.datapoints["datapoints"][99998]
