"""Snapshot-style tests for sensor discovery messages (TEST-01)."""
import json

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
    assert payload["object_id"] == entity_id
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
# TEST-01-4: Energy sensor (DID 548, sub CurrentYear)
# Frueher DID 535 — der ist auf der Vitocal per ignored_dids stillgelegt und
# erzeugt deshalb bewusst keine Discovery mehr.
# ---------------------------------------------------------------------------

def test_energy_sensor_discovery(generator_en):
    topic = "open3e/680_548_EnergyConsumptionCentralHeating/CurrentYear"
    disc_topic, p = _discover(generator_en, topic, "12345.6")

    assert "/sensor/" in disc_topic
    _assert_common_fields(
        p,
        name="Energy Central Heating current_year",
        unique_id="open3e_680_548_currentyear",
        entity_id="open3e_680_548_currentyear",
        state_topic=topic,
    )
    assert p["device_class"] == "energy"
    assert p["unit_of_measurement"] == "kWh"
    assert p["state_class"] == "total_increasing"


# ---------------------------------------------------------------------------
# TEST DATA-03/05: Status DIDs
# ---------------------------------------------------------------------------

def test_four_three_way_valve_discovery(generator_en):
    """Das hydraulische 4/3-Wegeventil ist DID 2735, nicht 2335.

    Der frueher hier gepruefte DID 2335 war ein Zahlendreher. Upstream ist er
    BatteryModuleCoulombCounters und auf einer Vitocal nicht vorhanden.
    """
    topic = "open3e/680_2735_FourThreeWayValveValveCurrentPosition"
    disc_topic, p = _discover(generator_en, topic, "1")
    assert "/sensor/" in disc_topic
    assert p["name"] == "4/3-Way Valve Position"
    assert "value_template" in p


def test_refrigerant_reversing_valve_discovery(generator_en):
    """Kaeltekreis-Umkehrventil (Heizen/Abtauen) — eigene Groesse neben 2735."""
    for did, name in ((1773, "Refrigerant Reversing Valve"),
                      (3190, "Refrigerant Reversing Valve Position")):
        topic = f"open3e/680_{did}_RefrigerantCircuitFourWayValve"
        disc_topic, p = _discover(generator_en, topic, "0")
        assert "/sensor/" in disc_topic
        assert p["name"] == name
        # Enum-Bedeutung ist upstream nicht dokumentiert — nichts raten
        assert "value_template" not in p


def test_compressor_speed_discovery(generator_en):
    topic = "open3e/680_2346_CompressorSpeed"
    disc_topic, p = _discover(generator_en, topic, "45")
    assert "/sensor/" in disc_topic
    assert p["name"] == "Compressor Speed"
    assert p["unit_of_measurement"] == "%"
    assert p["state_class"] == "measurement"


def test_primary_hx_temperature_discovery(generator_en):
    topic = "open3e/680_354_PrimaryHeatExchanger/Actual"
    disc_topic, p = _discover(generator_en, topic, "28.5")
    assert "/sensor/" in disc_topic
    assert p["device_class"] == "temperature"
    assert p["unit_of_measurement"] == "°C"


def test_vitocharge_dids_are_ignored_on_vitocal(generator_en):
    """DIDs des Vitocharge VX3 duerfen auf einer Vitocal keine Entitaet erzeugen.

    1690/1834/2335 stehen in Open3EdatapointsVx3.py, nicht in einer
    Vitocal-Tabelle. Ohne Batteriespeicher am E3-Bus antwortet die ECU mit
    ConditionsNotCorrect (0x22) — der frueher hier erwartete PV-Leistungssensor
    hat nie einen Wert geliefert.
    """
    for did in (535, 1603, 1690, 1834, 2335):
        assert generator_en.is_ignored_did(did), f"DID {did} muesste ignoriert sein"


def test_ignored_dids_keeps_inherited_540(generator_en):
    """merge_config ersetzt ignored_dids komplett — 540 darf dabei nicht verloren gehen."""
    assert generator_en.is_ignored_did(540)
