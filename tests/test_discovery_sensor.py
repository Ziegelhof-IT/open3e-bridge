"""Snapshot-style tests for sensor discovery messages (TEST-01)."""
import json

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _discover(gen, topic, value="0"):
    """Call generate_discovery_message and return (discovery_topic, parsed payload)."""
    results = gen.generate_discovery_message(topic, value, test_mode=False)
    assert results, f"No discovery messages generated for {topic}"
    disc_topic, raw_payload = results[0]
    return disc_topic, json.loads(raw_payload)


def _assert_common_fields(payload, *, name, unique_id, entity_id, state_topic):
    """Assert fields shared by every sensor discovery payload."""
    assert payload["name"] == name
    assert payload["unique_id"] == unique_id
    assert payload["default_entity_id"] == entity_id
    assert payload["state_topic"] == state_topic

    # Device block
    dev = payload["device"]
    assert "identifiers" in dev
    assert isinstance(dev["identifiers"], list)
    assert any("open3e_680" in i for i in dev["identifiers"])
    assert dev["manufacturer"] == "Viessmann"

    # Origin block
    origin = payload["origin"]
    assert origin["name"] == "Open3E Bridge"
    assert "sw_version" in origin

    # Availability
    assert payload["availability_topic"] == "open3e/LWT"


# ---------------------------------------------------------------------------
# TEST-01-1: Temperature sensor (DID 268, sub Actual)
# ---------------------------------------------------------------------------

def test_temperature_sensor_discovery(generator_en):
    topic = "open3e/680_268_FlowTemperatureSensor/Actual"
    disc_topic, p = _discover(generator_en, topic, "42.5")

    assert "/sensor/" in disc_topic
    _assert_common_fields(
        p,
        name="Flow Temperature Current",
        unique_id="open3e_680_268_actual",
        entity_id="open3e_680_268_actual",
        state_topic=topic,
    )
    assert p["device_class"] == "temperature"
    assert p["unit_of_measurement"] == "°C"
    assert p["state_class"] == "measurement"


# ---------------------------------------------------------------------------
# TEST-01-2: Pressure sensor (DID 318, sub Actual)
# ---------------------------------------------------------------------------

def test_pressure_sensor_discovery(generator_en):
    topic = "open3e/680_318_WaterPressureSensor/Actual"
    disc_topic, p = _discover(generator_en, topic, "1.8")

    assert "/sensor/" in disc_topic
    _assert_common_fields(
        p,
        name="Water Pressure Current",
        unique_id="open3e_680_318_actual",
        entity_id="open3e_680_318_actual",
        state_topic=topic,
    )
    assert p["device_class"] == "pressure"
    assert p["unit_of_measurement"] == "bar"
    assert p["state_class"] == "measurement"


# ---------------------------------------------------------------------------
# TEST-01-3: Power sensor (DID 2496, no sub)
# ---------------------------------------------------------------------------

def test_power_sensor_discovery(generator_en):
    topic = "open3e/680_2496_CurrentThermalCapacitySystem"
    disc_topic, p = _discover(generator_en, topic, "3500")

    assert "/sensor/" in disc_topic
    _assert_common_fields(
        p,
        name="Thermal Power (System)",
        unique_id="open3e_680_2496",
        entity_id="open3e_680_2496",
        state_topic=topic,
    )
    assert p["device_class"] == "power"
    assert p["unit_of_measurement"] == "W"
    assert p["state_class"] == "measurement"


# ---------------------------------------------------------------------------
# TEST-01-4: Energy sensor (DID 535, sub GridSuppliedEnergy)
# ---------------------------------------------------------------------------

def test_energy_sensor_discovery(generator_en):
    topic = "open3e/680_535_ObjectElectricalEnergyStatistical/GridSuppliedEnergy"
    disc_topic, p = _discover(generator_en, topic, "12345.6")

    assert "/sensor/" in disc_topic
    _assert_common_fields(
        p,
        name="Electrical Energy Statistics GridSuppliedEnergy",
        unique_id="open3e_680_535_gridsuppliedenergy",
        entity_id="open3e_680_535_gridsuppliedenergy",
        state_topic=topic,
    )
    assert p["device_class"] == "energy"
    assert p["unit_of_measurement"] == "kWh"
    assert p["state_class"] == "total_increasing"
