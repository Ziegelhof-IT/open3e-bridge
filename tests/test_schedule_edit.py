"""Tests for writable schedule DIDs 691-697 (DHW) and 761-767 (HK1)."""
import json
from pathlib import Path

from generators.homeassistant import HomeAssistantGenerator

CONFIG_DIR = str(Path(__file__).resolve().parents[1] / "config")


class TestScheduleEditConfig:
    """Schedule DID configuration."""

    def test_dhw_schedule_dids_exist(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dps = gen.datapoints.get("datapoints", {})
        for did in range(691, 698):
            assert did in dps, f"DID {did} missing"

    def test_hk1_schedule_dids_exist(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dps = gen.datapoints.get("datapoints", {})
        for did in range(761, 768):
            assert did in dps, f"DID {did} missing"

    def test_schedule_type_is_schedule_edit(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dp = gen.datapoints["datapoints"][691]
        assert dp["type"] == "schedule_edit"

    def test_schedule_is_writable(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dp = gen.datapoints["datapoints"][691]
        assert dp["writable"] is True

    def test_schedule_has_command_template(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dp = gen.datapoints["datapoints"][691]
        assert "command_template" in dp

    def test_schedule_has_value_template(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dp = gen.datapoints["datapoints"][691]
        assert "value_template" in dp


class TestScheduleEditDiscovery:
    """Schedule text entity generation."""

    def test_dhw_monday_generates_text_entity(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        topic = "open3e/680_691_DomesticHotWaterTimeScheduleMonday"
        value = '{"Count": 1, "Schedules": [{"Start": "06:00", "Stop": "22:00", "Unknown": "0000", "Mode": 4}]}'
        out = gen.generate_discovery_message(topic, value, test_mode=True)
        assert len(out) >= 1
        disc_topic, payload = out[0]
        data = json.loads(payload)
        assert "text" in disc_topic
        assert data.get("command_topic") == "open3e/cmnd"
        assert "command_template" in data

    def test_hk1_monday_generates_text_entity(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        topic = "open3e/680_761_MixerOneCircuitTimeScheduleMonday"
        value = '{"Count": 1, "Schedules": [{"Start": "07:00", "Stop": "21:00", "Unknown": "0000", "Mode": 4}]}'
        out = gen.generate_discovery_message(topic, value, test_mode=True)
        assert len(out) >= 1
        disc_topic = out[0][0]
        assert "text" in disc_topic

    def test_command_template_contains_did(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dp = gen.datapoints["datapoints"][691]
        assert "691" in dp["command_template"]

    def test_each_did_has_unique_command_template(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dps = gen.datapoints["datapoints"]
        for did in [691, 692, 693, 694, 695, 696, 697]:
            assert str(did) in dps[did]["command_template"]
        for did in [761, 762, 763, 764, 765, 766, 767]:
            assert str(did) in dps[did]["command_template"]

    def test_command_template_uses_write_mode(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dp = gen.datapoints["datapoints"][691]
        # Uses structured write (not write-raw) for O3EList codec
        assert "'write'" in dp["command_template"] or '"write"' in dp["command_template"]

    def test_value_template_extracts_time_ranges(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        dp = gen.datapoints["datapoints"][691]
        # The value_template should reference Schedules
        assert "Schedules" in dp["value_template"]
        assert "Start" in dp["value_template"]
        assert "Stop" in dp["value_template"]

    def test_schedule_entity_has_min_max(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="common")
        topic = "open3e/680_691_DomesticHotWaterTimeScheduleMonday"
        value = '{"Count": 0, "Schedules": []}'
        out = gen.generate_discovery_message(topic, value, test_mode=True)
        data = json.loads(out[0][1])
        assert "min" in data
        assert "max" in data


class TestScheduleEditGerman:
    """German translations for schedule entities."""

    def test_dhw_schedule_german_name(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="de", profile="common")
        topic = "open3e/680_691_DomesticHotWaterTimeScheduleMonday"
        value = '{"Count": 0, "Schedules": []}'
        out = gen.generate_discovery_message(topic, value, test_mode=True)
        data = json.loads(out[0][1])
        # Should be translated
        assert "Zeitprogramm" in data["name"] or "Schedule" in data["name"] or "WW" in data["name"] or "DHW" in data["name"]


class TestScheduleEditVitocal:
    """Schedule entities work in vitocal profile (inherited from common)."""

    def test_vitocal_has_schedule_dids(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dps = gen.datapoints.get("datapoints", {})
        assert 691 in dps
        assert 761 in dps

    def test_vitocal_schedule_is_writable(self):
        gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", profile="vitocal")
        dp = gen.datapoints["datapoints"][691]
        assert dp["writable"] is True


class TestScheduleTriggerSub:
    """SUB-02: only the 'Count' sub-item may drive discovery.

    The reader splits these DIDs into many sub-topics (Count, Schedules/0/Start,
    Schedules/0/Mode, ...). Every sub-topic that reaches the generator rebuilds
    the discovery config and sets state_topic to whatever arrived last, so
    without an explicit trigger_sub the entity ends up pointing at an arbitrary
    deep topic instead of the DID root.
    """

    DEEP_SUBS = ["Schedules/0/Start", "Schedules/0/Stop", "Schedules/0/Mode",
                 "Schedules/0/Unknown"]

    def _gen(self):
        return HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en",
                                      discovery_prefix="homeassistant",
                                      add_test_prefix=False, profile="common")

    def test_count_sub_item_generates_discovery(self):
        gen = self._gen()
        out = gen.generate_discovery_message(
            "open3e/680_691_DomesticHotWaterTimeScheduleMonday/Count", "1", test_mode=False)
        assert out, "Count must generate discovery"
        cfg = json.loads(out[0][1])
        assert cfg["state_topic"].endswith("/Count")

    def test_deep_sub_items_generate_nothing(self):
        gen = self._gen()
        for did in (691, 697, 761, 767):
            for sub in self.DEEP_SUBS:
                topic = f"open3e/680_{did}_Schedule/{sub}"
                out = gen.generate_discovery_message(topic, "0", test_mode=False)
                assert out == [], f"{topic} must not generate discovery, got {out}"

    def test_status_list_deep_sub_items_generate_nothing(self):
        gen = self._gen()
        for sub in ("ListEntries/0/State/ID", "ListEntries/0/DateTime/Timestamp",
                    "ListEntries/0/Unknown"):
            topic = f"open3e/680_257_StatusDtcList/{sub}"
            assert gen.generate_discovery_message(topic, "0", test_mode=False) == []
