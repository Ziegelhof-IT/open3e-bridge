"""Tests for button entity discovery (ENT-02) — stateless, no state_topic."""
import json


def _discover(gen, topic, value="0"):
    results = gen.generate_discovery_message(topic, value, test_mode=False)
    assert results, f"No discovery messages for {topic}"
    disc_topic, raw = results[0]
    return disc_topic, json.loads(raw)


class TestButtonDiscovery:
    """DID 1710 DomesticHotWaterOneTimeCharge as button_action."""

    TOPIC = "open3e/680_1710_DomesticHotWaterOneTimeCharge"

    def test_discovery_topic_contains_button(self, generator_en):
        disc_topic, _ = _discover(generator_en, self.TOPIC)
        assert "/button/" in disc_topic

    def test_no_state_topic(self, generator_en):
        """Buttons are stateless — state_topic must NOT be present."""
        _, p = _discover(generator_en, self.TOPIC)
        assert "state_topic" not in p

    def test_command_topic(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["command_topic"] == "open3e/cmnd"

    def test_payload_press(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["payload_press"] == "PRESS"

    def test_command_template_present(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert "command_template" in p

    def test_entity_id(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["default_entity_id"] == "open3e_680_1710"

    def test_origin(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["origin"]["name"] == "Open3E Bridge"

    def test_availability(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["availability_topic"] == "open3e/LWT"

    def test_name_en(self, generator_en):
        _, p = _discover(generator_en, self.TOPIC)
        assert p["name"] == "DHW One-Time Charge"

    def test_name_de(self, generator_de):
        _, p = _discover(generator_de, self.TOPIC)
        assert p["name"] == "Warmwasser Einmalladung"


class TestSensorStillHasStateTopic:
    """Regression: non-button entities must still have state_topic."""

    def test_sensor_has_state_topic(self, generator_en):
        topic = "open3e/680_2496_CurrentThermalCapacitySystem"
        _, p = _discover(generator_en, topic, "3500")
        assert "state_topic" in p
        assert p["state_topic"] == topic

    def test_switch_has_state_topic(self, generator_en):
        topic = "open3e/680_1006_QuickMode"
        _, p = _discover(generator_en, topic, "1")
        assert "state_topic" in p
