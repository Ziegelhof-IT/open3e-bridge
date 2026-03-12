"""Layer 1: Complete German translation tests.

Every configured entity must have a German name when language=de.
Modes, sub-items, and system entities must be translated.
"""
import json

import pytest


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _discover(gen, topic, value="0"):
    results = gen.generate_discovery_message(topic, value, test_mode=False)
    assert results, f"No discovery for {topic}"
    return results[0][0], json.loads(results[0][1])


def _discover_all(gen, topic, value="0"):
    """Return all discovery payloads for a topic (may emit multiple entities)."""
    results = gen.generate_discovery_message(topic, value, test_mode=False)
    return [(t, json.loads(p)) for t, p in results]


# ---------------------------------------------------------------------------
# Entity name translation completeness
# ---------------------------------------------------------------------------

class TestAllEntityNamesTranslated:
    """Every configured DID in datapoints must have a German name in de.yaml."""

    def test_no_translation_warnings(self, generator_de):
        """Validation should produce zero 'missing in de translations' warnings."""
        result = generator_de.validate()
        missing = [w for w in result["warnings"] if "missing in de translations" in w]
        assert missing == [], f"Untranslated entities: {missing}"


# ---------------------------------------------------------------------------
# Climate mode translations
# ---------------------------------------------------------------------------

class TestClimateModeTranslation:
    """Climate entity modes must be German when language=de."""

    TOPIC = "open3e/680_1415_MixerOneCircuitOperationState/Mode/ID"

    def test_climate_modes_de(self, generator_de):
        """Climate modes list should contain German mode names."""
        results = _discover_all(generator_de, self.TOPIC, "1")
        climate_payloads = [(t, p) for t, p in results if "/climate/" in t]
        assert climate_payloads, "No climate entity generated"
        _, payload = climate_payloads[0]
        modes = payload["modes"]
        assert "Aus" in modes
        assert "Heizen" in modes
        assert "Automatik" in modes

    def test_climate_modes_en(self, generator_en):
        """Climate modes stay English when language=en."""
        results = _discover_all(generator_en, self.TOPIC, "1")
        climate_payloads = [(t, p) for t, p in results if "/climate/" in t]
        assert climate_payloads
        _, payload = climate_payloads[0]
        modes = payload["modes"]
        assert "off" in modes
        assert "heat" in modes
        assert "auto" in modes


# ---------------------------------------------------------------------------
# Select mode translations
# ---------------------------------------------------------------------------

class TestSelectModeTranslation:
    """Select entity options must be German when language=de."""

    TOPIC = "open3e/680_1415_MixerOneCircuitOperationState/Mode/ID"

    def test_select_options_de(self, generator_de):
        """Select options should be German."""
        results = _discover_all(generator_de, self.TOPIC, "1")
        select_payloads = [(t, p) for t, p in results if "/select/" in t]
        assert select_payloads, "No select entity generated"
        _, payload = select_payloads[0]
        options = payload["options"]
        assert "Aus" in options
        assert "Heizen" in options

    def test_select_options_en(self, generator_en):
        """Select options stay English when language=en."""
        results = _discover_all(generator_en, self.TOPIC, "1")
        select_payloads = [(t, p) for t, p in results if "/select/" in t]
        assert select_payloads
        _, payload = select_payloads[0]
        options = payload["options"]
        assert "off" in options
        assert "heat" in options


# ---------------------------------------------------------------------------
# Water heater mode translations
# ---------------------------------------------------------------------------

class TestWaterHeaterModeTranslation:
    """Water heater modes must be German when language=de."""

    TOPIC = "open3e/680_531_DomesticHotWaterOperationState"

    def test_water_heater_modes_de(self, generator_de):
        """Water heater modes should be German."""
        results = _discover_all(generator_de, self.TOPIC, "0")
        wh_payloads = [(t, p) for t, p in results if "/water_heater/" in t]
        assert wh_payloads, "No water_heater entity generated"
        _, payload = wh_payloads[0]
        modes = payload["modes"]
        assert "Aus" in modes
        assert "Eco" in modes
        assert "Leistung" in modes

    def test_water_heater_modes_en(self, generator_en):
        """Water heater modes stay English when language=en."""
        results = _discover_all(generator_en, self.TOPIC, "0")
        wh_payloads = [(t, p) for t, p in results if "/water_heater/" in t]
        assert wh_payloads
        _, payload = wh_payloads[0]
        modes = payload["modes"]
        assert "off" in modes
        assert "eco" in modes
        assert "performance" in modes


# ---------------------------------------------------------------------------
# Sub-item name translations (Comfort/Standard/Reduced)
# ---------------------------------------------------------------------------

class TestSubItemTranslation:
    """Sub-item names (Comfort, Standard, Reduced) must be translated."""

    def test_comfort_de(self, generator_de):
        """DID 424 Comfort sub-item name should contain 'Komfort'."""
        topic = "open3e/680_424_MixerOneCircuitRoomTemperatureSetpoint/Comfort"
        _, payload = _discover(generator_de, topic, "21.0")
        assert "Komfort" in payload["name"]

    def test_standard_de(self, generator_de):
        topic = "open3e/680_424_MixerOneCircuitRoomTemperatureSetpoint/Standard"
        _, payload = _discover(generator_de, topic, "19.0")
        assert "Standard" in payload["name"]

    def test_reduced_de(self, generator_de):
        topic = "open3e/680_424_MixerOneCircuitRoomTemperatureSetpoint/Reduced"
        _, payload = _discover(generator_de, topic, "17.0")
        assert "Reduziert" in payload["name"]

    def test_comfort_en(self, generator_en):
        """English names should stay unchanged."""
        topic = "open3e/680_424_MixerOneCircuitRoomTemperatureSetpoint/Comfort"
        _, payload = _discover(generator_en, topic, "21.0")
        assert "Comfort" in payload["name"]


# ---------------------------------------------------------------------------
# Error list value template translations
# ---------------------------------------------------------------------------

class TestErrorListTranslation:
    """Error list value templates should use German strings when language=de."""

    def test_error_list_no_errors_de(self, generator_de):
        """DID 257 should show 'Keine Fehler' when count is 0."""
        topic = "open3e/680_257_StatusDtcList"
        _, payload = _discover(generator_de, topic, '{"Count": 0}')
        vt = payload.get("value_template", "")
        assert "Keine Fehler" in vt

    def test_error_list_active_de(self, generator_de):
        topic = "open3e/680_257_StatusDtcList"
        _, payload = _discover(generator_de, topic, '{"Count": 2}')
        vt = payload.get("value_template", "")
        assert "aktiv" in vt


# ---------------------------------------------------------------------------
# Schedule display translation
# ---------------------------------------------------------------------------

class TestScheduleTranslation:
    """Schedule sensor value templates should use translated strings."""

    def test_schedule_inactive_de(self, generator_de):
        """Schedule should show 'Inaktiv' (not 'inactive') when language=de."""
        topic = "open3e/680_691_DomesticHotWaterTimeScheduleMonday"
        _, payload = _discover(generator_de, topic, '{"Schedules": []}')
        vt = payload.get("value_template", "")
        assert "Inaktiv" in vt or "inaktiv" in vt.lower()


# ---------------------------------------------------------------------------
# Command template robustness with translated modes
# ---------------------------------------------------------------------------

class TestTranslatedCommandTemplates:
    """Command templates must work with translated mode names."""

    def test_select_command_template_uses_translated_keys(self, generator_de):
        """Select command_template should map German mode names to raw values."""
        topic = "open3e/680_1415_MixerOneCircuitOperationState/Mode/ID"
        results = _discover_all(generator_de, topic, "1")
        select_payloads = [(t, p) for t, p in results if "/select/" in t]
        assert select_payloads
        _, payload = select_payloads[0]
        ct = payload.get("command_template", "")
        # Template must map German names to raw values
        assert "Aus" in ct or "Heizen" in ct or "Automatik" in ct
