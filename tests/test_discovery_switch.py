"""Tests for switch entity discovery (ENT-01)."""
import json


def _discover(gen, topic, value="0"):
    results = gen.generate_discovery_message(topic, value, test_mode=False)
    assert results, f"No discovery messages for {topic}"
    disc_topic, raw = results[0]
    return disc_topic, json.loads(raw)


class TestSwitchDiscovery:
    """DID 1006 QuickMode as switch_toggle."""

    TOPIC = "open3e/680_1006_QuickMode"

    def test_discovery_topic_contains_switch(self, generator_en):
        disc_topic, _ = _discover(generator_en, self.TOPIC)
        assert "/switch/" in disc_topic

    def test_payload_on(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["payload_on"] == "1"

    def test_payload_off(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["payload_off"] == "0"

    def test_state_on(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["state_on"] == "1"

    def test_state_off(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["state_off"] == "0"

    def test_command_topic(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["command_topic"] == "open3e/cmnd"

    def test_command_template_present(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert "command_template" in p

    def test_entity_id(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["default_entity_id"] == "open3e_680_1006"

    def test_origin(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["origin"]["name"] == "Open3E Bridge"

    def test_availability(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["availability_topic"] == "open3e/LWT"

    def test_name_en(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["name"] == "Quick Mode"

    def test_name_de(self, generator_de):
        _, p = _discover(generator_de, self.TOPIC)
        assert p["name"] == "Schnellmodus"
