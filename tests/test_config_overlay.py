"""Tests for the config/local/ overlay mechanism."""

import pytest


@pytest.fixture
def config_with_overlay(tmp_path):
    """Create a config directory with main + local overlay."""
    # Main config
    dp_yaml = tmp_path / "datapoints.yaml"
    dp_yaml.write_text("""
schema_version: 1
devices:
  indoor:
    name: "Indoor Unit"
    model: "Vitocal"
datapoints:
  268:
    type: "temperature_sensor"
    name: "Flow Temperature"
    device: "indoor"
    subs:
      Actual: { suffix: "current" }
""")

    types_yaml = tmp_path / "templates" / "types.yaml"
    types_yaml.parent.mkdir(parents=True)
    types_yaml.write_text("""
temperature_sensor:
  entity_type: sensor
  device_class: temperature
  unit_of_measurement: "°C"
  state_class: measurement
""")

    return tmp_path


@pytest.fixture
def config_with_local_overlay(config_with_overlay):
    """Config with a local overlay adding custom DIDs."""
    local_dir = config_with_overlay / "local"
    local_dir.mkdir()

    local_dp = local_dir / "datapoints.yaml"
    local_dp.write_text("""
devices:
  my_buffer:
    name: "Buffer Tank"
    model: "Custom Buffer"
datapoints:
  9999:
    type: "temperature_sensor"
    name: "Buffer Temperature"
    device: "my_buffer"
    subs:
      Actual: { suffix: "current" }
""")

    return config_with_overlay


def test_no_local_dir_works(config_with_overlay):
    """Generator works without a local/ directory."""
    from generators.base import BaseGenerator
    gen = BaseGenerator(str(config_with_overlay), language="en")
    assert gen.get_datapoint_config(268) is not None
    assert gen.get_datapoint_config(9999) is None


def test_local_overlay_adds_datapoints(config_with_local_overlay):
    """Local overlay adds new datapoints."""
    from generators.base import BaseGenerator
    gen = BaseGenerator(str(config_with_local_overlay), language="en")

    # Original DID still there
    assert gen.get_datapoint_config(268) is not None

    # New DID from overlay
    dp = gen.get_datapoint_config(9999)
    assert dp is not None
    assert dp["name"] == "Buffer Temperature"
    assert dp["device"] == "my_buffer"


def test_local_overlay_adds_devices(config_with_local_overlay):
    """Local overlay adds new devices."""
    from generators.base import BaseGenerator
    gen = BaseGenerator(str(config_with_local_overlay), language="en")

    devices = gen.datapoints.get("devices", {})
    assert "indoor" in devices  # original
    assert "my_buffer" in devices  # from overlay


def test_local_overlay_overrides_existing_did(config_with_overlay):
    """Local overlay can override existing DIDs (local wins)."""
    local_dir = config_with_overlay / "local"
    local_dir.mkdir()
    local_dp = local_dir / "datapoints.yaml"
    local_dp.write_text("""
datapoints:
  268:
    type: "temperature_sensor"
    name: "My Custom Flow Temperature"
    device: "indoor"
""")

    from generators.base import BaseGenerator
    gen = BaseGenerator(str(config_with_overlay), language="en")

    dp = gen.get_datapoint_config(268)
    assert dp is not None
    assert dp["name"] == "My Custom Flow Temperature"


def test_local_types_overlay(config_with_overlay):
    """Local types.yaml overlay adds custom type templates."""
    local_dir = config_with_overlay / "local"
    local_dir.mkdir()
    local_types = local_dir / "types.yaml"
    local_types.write_text("""
custom_sensor:
  entity_type: sensor
  icon: "mdi:custom"
""")

    from generators.base import BaseGenerator
    gen = BaseGenerator(str(config_with_overlay), language="en")

    # Original type still there
    assert "temperature_sensor" in gen.type_templates

    # Custom type from overlay
    assert "custom_sensor" in gen.type_templates
    assert gen.type_templates["custom_sensor"]["icon"] == "mdi:custom"


def test_empty_local_overlay_harmless(config_with_overlay):
    """Empty local/ directory doesn't break anything."""
    local_dir = config_with_overlay / "local"
    local_dir.mkdir()

    from generators.base import BaseGenerator
    gen = BaseGenerator(str(config_with_overlay), language="en")
    assert gen.get_datapoint_config(268) is not None
