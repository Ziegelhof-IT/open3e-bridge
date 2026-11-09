"""Tests for the DeviceRegistry (multi-device support)."""
import pytest
import yaml

from generators.devices import DeviceConfig, DeviceRegistry


class TestDeviceConfig:
    def test_basic_creation(self):
        dc = DeviceConfig(name="vitocal", ecu="680", profile="vitocal")
        assert dc.name == "vitocal"
        assert dc.ecu == "680"
        assert dc.profile == "vitocal"
        assert dc.extra == {}

    def test_extra_fields(self):
        dc = DeviceConfig(name="test", ecu="690", extra={"custom": True})
        assert dc.extra["custom"] is True


class TestDeviceRegistrySingleDevice:
    def test_from_single_device_defaults(self):
        reg = DeviceRegistry.from_single_device(config_dir="config")
        assert len(reg.ecu_addresses) == 1
        assert "680" in reg.ecu_addresses
        assert reg.get_generator("680") is not None
        assert reg.get_default_generator() is not None

    def test_from_single_device_custom_ecu(self):
        reg = DeviceRegistry.from_single_device(config_dir="config", ecu_addr="690")
        assert "690" in reg.ecu_addresses
        assert reg.get_generator("690") is not None

    def test_from_single_device_custom_profile(self):
        reg = DeviceRegistry.from_single_device(
            config_dir="config", profile="vitodens"
        )
        gen = reg.get_default_generator()
        assert gen._active_profile == "vitodens"

    def test_get_generator_unknown_ecu(self):
        reg = DeviceRegistry.from_single_device(config_dir="config")
        assert reg.get_generator("999") is None

    def test_devices_property(self):
        reg = DeviceRegistry.from_single_device(config_dir="config")
        devs = reg.devices
        assert "680" in devs
        assert devs["680"].name == "default"

    def test_generators_property_returns_copy(self):
        reg = DeviceRegistry.from_single_device(config_dir="config")
        g1 = reg.generators
        g2 = reg.generators
        assert g1 is not g2  # returns a copy each time
        assert list(g1.keys()) == list(g2.keys())


class TestDeviceRegistryMultiDevice:
    def test_two_devices(self):
        devices = [
            DeviceConfig(name="vitocal", ecu="680", profile="vitocal"),
            DeviceConfig(name="vitodens", ecu="690", profile="vitodens"),
        ]
        reg = DeviceRegistry(devices, config_dir="config")
        assert len(reg.ecu_addresses) == 2
        assert reg.get_generator("680") is not None
        assert reg.get_generator("690") is not None
        # Each generator has its own profile
        assert reg.get_generator("680")._active_profile == "vitocal"
        assert reg.get_generator("690")._active_profile == "vitodens"

    def test_default_generator_is_first(self):
        devices = [
            DeviceConfig(name="first", ecu="680", profile="common"),
            DeviceConfig(name="second", ecu="690", profile="common"),
        ]
        reg = DeviceRegistry(devices, config_dir="config")
        default = reg.get_default_generator()
        assert default is reg.get_generator("680")


class TestDeviceRegistryFromYaml:
    def test_load_valid_yaml(self, tmp_path):
        cfg = {
            "devices": [
                {"name": "vitocal", "ecu": "680", "profile": "vitocal"},
                {"name": "vitodens", "ecu": "690", "profile": "vitodens"},
            ]
        }
        p = tmp_path / "devices.yaml"
        p.write_text(yaml.dump(cfg))
        reg = DeviceRegistry.from_yaml(str(p), config_dir="config")
        assert len(reg.ecu_addresses) == 2

    def test_ecu_0x_prefix_stripped(self, tmp_path):
        cfg = {"devices": [{"name": "test", "ecu": "0x680", "profile": "common"}]}
        p = tmp_path / "devices.yaml"
        p.write_text(yaml.dump(cfg))
        reg = DeviceRegistry.from_yaml(str(p), config_dir="config")
        assert "680" in reg.ecu_addresses

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError, match="not found"):
            DeviceRegistry.from_yaml("/nonexistent/devices.yaml", config_dir="config")

    def test_empty_devices_raises(self, tmp_path):
        p = tmp_path / "devices.yaml"
        p.write_text("devices: []")
        with pytest.raises(ValueError, match="non-empty list"):
            DeviceRegistry.from_yaml(str(p), config_dir="config")

    def test_no_devices_key_raises(self, tmp_path):
        p = tmp_path / "devices.yaml"
        p.write_text("something_else: true")
        with pytest.raises(ValueError, match="non-empty list"):
            DeviceRegistry.from_yaml(str(p), config_dir="config")

    def test_duplicate_ecu_raises(self, tmp_path):
        cfg = {
            "devices": [
                {"name": "a", "ecu": "680", "profile": "common"},
                {"name": "b", "ecu": "680", "profile": "vitocal"},
            ]
        }
        p = tmp_path / "devices.yaml"
        p.write_text(yaml.dump(cfg))
        with pytest.raises(ValueError, match="Duplicate ECU"):
            DeviceRegistry.from_yaml(str(p), config_dir="config")

    def test_duplicate_name_raises(self, tmp_path):
        cfg = {
            "devices": [
                {"name": "same", "ecu": "680", "profile": "common"},
                {"name": "same", "ecu": "690", "profile": "vitocal"},
            ]
        }
        p = tmp_path / "devices.yaml"
        p.write_text(yaml.dump(cfg))
        with pytest.raises(ValueError, match="Duplicate device name"):
            DeviceRegistry.from_yaml(str(p), config_dir="config")

    def test_missing_name_raises(self, tmp_path):
        cfg = {"devices": [{"ecu": "680"}]}
        p = tmp_path / "devices.yaml"
        p.write_text(yaml.dump(cfg))
        with pytest.raises(ValueError, match="'name' is required"):
            DeviceRegistry.from_yaml(str(p), config_dir="config")

    def test_missing_ecu_raises(self, tmp_path):
        cfg = {"devices": [{"name": "test"}]}
        p = tmp_path / "devices.yaml"
        p.write_text(yaml.dump(cfg))
        with pytest.raises(ValueError, match="'ecu' is required"):
            DeviceRegistry.from_yaml(str(p), config_dir="config")

    def test_non_dict_entry_raises(self, tmp_path):
        cfg = {"devices": ["not a dict"]}
        p = tmp_path / "devices.yaml"
        p.write_text(yaml.dump(cfg))
        with pytest.raises(ValueError, match="must be a mapping"):
            DeviceRegistry.from_yaml(str(p), config_dir="config")

    def test_default_profile_auto(self, tmp_path):
        cfg = {"devices": [{"name": "test", "ecu": "680"}]}
        p = tmp_path / "devices.yaml"
        p.write_text(yaml.dump(cfg))
        reg = DeviceRegistry.from_yaml(str(p), config_dir="config")
        dev = reg.devices["680"]
        assert dev.profile == "auto"

    def test_extra_fields_preserved(self, tmp_path):
        cfg = {"devices": [{"name": "test", "ecu": "680", "profile": "common", "custom_field": "value"}]}
        p = tmp_path / "devices.yaml"
        p.write_text(yaml.dump(cfg))
        reg = DeviceRegistry.from_yaml(str(p), config_dir="config")
        assert reg.devices["680"].extra["custom_field"] == "value"


class TestDeviceRegistryBridgeIntegration:
    """Test DeviceRegistry integration with bridge message routing."""

    def test_multi_device_message_routing(self):
        """Messages from different ECUs route to correct generators."""
        devices = [
            DeviceConfig(name="vitocal", ecu="680", profile="vitocal"),
            DeviceConfig(name="vitodens", ecu="690", profile="vitodens"),
        ]
        reg = DeviceRegistry(devices, config_dir="config")

        gen_680 = reg.get_generator("680")
        gen_690 = reg.get_generator("690")

        # Vitocal-specific DID should be in 680 generator but not necessarily in 690
        # (vitodens profile has different DIDs)
        assert gen_680 is not gen_690

    def test_unknown_ecu_returns_none(self):
        devices = [DeviceConfig(name="vitocal", ecu="680", profile="vitocal")]
        reg = DeviceRegistry(devices, config_dir="config")
        assert reg.get_generator("999") is None


class TestEcuNormalization:
    """ECU addresses must match the reader's '{ecuAddr:03X}' topic format.

    The reader publishes uppercase hex (e.g. '6CF'). Hand-written config files
    routinely use lowercase or an '0x' prefix; without normalization the
    registry lookup misses and messages silently fall back to the default
    generator.
    """

    @pytest.mark.parametrize("written", ["6CF", "6cf", "0x6CF", "0x6cf", " 6cf "])
    def test_config_spelling_variants_resolve_to_topic_form(self, written):
        dc = DeviceConfig(name="wp", ecu=written, profile="vitocal")
        assert dc.ecu == "6CF"

    def test_lookup_is_case_insensitive(self):
        devices = [DeviceConfig(name="wp", ecu="6cf", profile="vitocal")]
        reg = DeviceRegistry(devices, config_dir="config")
        # Topic form (uppercase) must hit even though config used lowercase
        assert reg.get_generator("6CF") is not None
        assert reg.get_generator("6cf") is not None
        assert reg.ecu_addresses == ["6CF"]

    def test_yaml_spelling_variants_collide_as_duplicates(self, tmp_path):
        path = tmp_path / "devices.yaml"
        path.write_text(yaml.safe_dump({"devices": [
            {"name": "a", "ecu": "6cf", "profile": "vitocal"},
            {"name": "b", "ecu": "0x6CF", "profile": "vitocal"},
        ]}), encoding="utf-8")
        with pytest.raises(ValueError, match="Duplicate ECU"):
            DeviceRegistry.from_yaml(path, config_dir="config")

    def test_yaml_lowercase_ecu_routes_uppercase_topic(self, tmp_path):
        path = tmp_path / "devices.yaml"
        path.write_text(yaml.safe_dump({"devices": [
            {"name": "vitocal", "ecu": "680", "profile": "vitocal"},
            {"name": "wp", "ecu": "6cf", "profile": "vitocal"},
        ]}), encoding="utf-8")
        reg = DeviceRegistry.from_yaml(path, config_dir="config")
        assert reg.get_generator("6CF") is not None
        assert reg.get_generator("6CF") is not reg.get_generator("680")
