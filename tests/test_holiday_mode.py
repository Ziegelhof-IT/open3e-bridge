"""Tests for holiday mode DIDs 511/512 (decoded sub-items)."""
import json
from pathlib import Path

import pytest

from generators.homeassistant import HomeAssistantGenerator

CONFIG_DIR = str(Path(__file__).resolve().parents[1] / "config")


class TestHolidayPhaseConfig:
    """Holiday phase DID configuration."""

    def test_did_511_exists_in_common(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dps = gen.datapoints.get("datapoints", {})
        assert 511 in dps

    def test_did_512_exists_in_common(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dps = gen.datapoints.get("datapoints", {})
        assert 512 in dps

    def test_did_511_type_is_holiday_phase(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dp = gen.datapoints["datapoints"][511]
        assert dp["type"] == "holiday_phase"

    def test_did_511_has_four_subs(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dp = gen.datapoints["datapoints"][511]
        subs = dp.get("subs", {})
        assert "PhaseBegin" in subs
        assert "PhaseEnd" in subs
        assert "Planned" in subs
        assert "Active" in subs


class TestHolidayPhaseDiscovery:
    """Holiday phase entity generation."""

    def test_phase_begin_generates_sensor(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        topic = "open3e/680_511_HolidayPhase/PhaseBegin"
        out = gen.generate_discovery_message(topic, "15.03.2026", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert data["icon"] == "mdi:calendar-arrow-right"
        assert "sensor" in out[0][0]

    def test_phase_end_generates_sensor(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        topic = "open3e/680_511_HolidayPhase/PhaseEnd"
        out = gen.generate_discovery_message(topic, "22.03.2026", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert data["icon"] == "mdi:calendar-arrow-left"

    def test_planned_generates_binary_sensor(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        topic = "open3e/680_511_HolidayPhase/Planned"
        out = gen.generate_discovery_message(topic, "1", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "binary_sensor" in out[0][0]
        assert data["payload_on"] == "1"
        assert data["payload_off"] == "0"

    def test_active_generates_binary_sensor(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        topic = "open3e/680_511_HolidayPhase/Active"
        out = gen.generate_discovery_message(topic, "0", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "binary_sensor" in out[0][0]
        assert data["device_class"] == "running"

    def test_did_512_phase_begin_also_works(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        topic = "open3e/680_512_HolidayAtHomePhase/PhaseBegin"
        out = gen.generate_discovery_message(topic, "01.04.2026", test_mode=True)
        assert len(out) >= 1

    def test_did_511_unknown_sub_ignored(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        topic = "open3e/680_511_HolidayPhase/UnknownField"
        out = gen.generate_discovery_message(topic, "42", test_mode=True)
        assert len(out) == 0


class TestHolidayPhaseGerman:
    """German translations for holiday mode."""

    def test_did_511_german_name(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="de", profile="common")
        topic = "open3e/680_511_HolidayPhase/PhaseBegin"
        out = gen.generate_discovery_message(topic, "15.03.2026", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "Urlaubsmodus" in data["name"]

    def test_did_512_german_name(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="de", profile="common")
        topic = "open3e/680_512_HolidayAtHomePhase/PhaseBegin"
        out = gen.generate_discovery_message(topic, "01.04.2026", test_mode=True)
        assert len(out) >= 1
        data = json.loads(out[0][1])
        assert "Ferien Zuhause" in data["name"]


class TestHolidayPhaseTypeTemplate:
    """Holiday phase type template validation."""

    def test_holiday_phase_in_types(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        assert "holiday_phase" in gen.type_templates

    def test_holiday_phase_has_sub_types(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        tp = gen.type_templates["holiday_phase"]
        assert "sub_types" in tp
        assert "start_date" in tp["sub_types"]
        assert "end_date" in tp["sub_types"]
        assert "planned" in tp["sub_types"]
        assert "active" in tp["sub_types"]
