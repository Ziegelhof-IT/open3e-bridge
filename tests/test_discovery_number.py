"""TEST-02: Number/setpoint entity discovery."""
import json


def test_dhw_setpoint_discovery(generator_en):
    """DID 396 produces a number entity with temperature setpoint config."""
    topic = "open3e/680_396_DomesticHotWaterTemperatureSetpoint"
    out = generator_en.generate_discovery_message(topic, "50.0", test_mode=False)

    assert len(out) == 1
    disc_topic, payload = out[0]

    assert "number/" in disc_topic
    data = json.loads(payload)

    assert data["min"] == 10
    assert data["max"] == 65
    assert data["step"] == 0.5
    assert data["command_topic"] == "open3e/cmnd"
    assert data["device_class"] == "temperature"
    assert "command_template" in data
    assert '"write"' in data["command_template"]


def test_pump_setpoint_discovery(generator_en):
    """DID 1102 sub Setpoint produces a number entity with write-raw template."""
    topic = "open3e/680_1102_MixerOneCircuitPumpMinimumMaximumLimit/Setpoint"
    out = generator_en.generate_discovery_message(topic, "80")

    assert len(out) == 1
    disc_topic, payload = out[0]

    assert "number/" in disc_topic
    data = json.loads(payload)

    assert data["min"] == 20
    assert data["max"] == 100
    assert data["step"] == 5
    assert data["unit_of_measurement"] == "%"
    assert "command_template" in data
    assert "write-raw" in data["command_template"]
    assert "%02x" in data["command_template"]
