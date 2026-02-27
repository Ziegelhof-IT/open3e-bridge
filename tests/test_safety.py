"""Tests for write-blacklist safety feature (SAFE-03)."""
import json
from pathlib import Path

from generators.homeassistant import HomeAssistantGenerator

CONFIG_DIR = str(Path(__file__).resolve().parents[1] / "config")


def _gen():
    return HomeAssistantGenerator(
        config_dir=CONFIG_DIR, language="en",
        discovery_prefix="homeassistant", add_test_prefix=False,
    )


class TestWriteBlacklist:
    """SAFE-03: DID 875 is write-blacklisted — read OK, write blocked."""

    def test_is_write_blacklisted_true(self):
        gen = _gen()
        assert gen.is_write_blacklisted(875) is True

    def test_is_write_blacklisted_false_for_normal_did(self):
        gen = _gen()
        assert gen.is_write_blacklisted(268) is False

    def test_blacklisted_did_has_no_command_topic(self):
        """DID 875 must not get a command_topic even if marked writable."""
        gen = _gen()
        topic = "open3e/680_875_LegionellaProtectionActivationTime"
        results = gen.generate_discovery_message(topic, "14:00", test_mode=False)
        assert results, "DID 875 should still produce sensor discovery"
        _, raw = results[0]
        p = json.loads(raw)
        assert "command_topic" not in p

    def test_blacklisted_did_still_produces_sensor(self):
        """DID 875 must produce a sensor discovery (read is allowed)."""
        gen = _gen()
        topic = "open3e/680_875_LegionellaProtectionActivationTime"
        results = gen.generate_discovery_message(topic, "14:00", test_mode=False)
        assert len(results) == 1
        disc_topic, raw = results[0]
        assert "/sensor/" in disc_topic
        p = json.loads(raw)
        assert p["name"] == "Legionella Protection Activation Time"

    def test_non_blacklisted_writable_has_command_topic(self):
        """DID 396 (writable, not blacklisted) should still get command_topic."""
        gen = _gen()
        topic = "open3e/680_396_DomesticHotWaterTemperatureSetpoint"
        results = gen.generate_discovery_message(topic, "50", test_mode=False)
        assert results
        _, raw = results[0]
        p = json.loads(raw)
        assert "command_topic" in p
