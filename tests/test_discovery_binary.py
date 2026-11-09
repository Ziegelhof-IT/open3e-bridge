"""TEST-03: Binary sensor discovery messages."""
import json

import jinja2
import pytest


class TestBinaryFrostProtection:
    """DID 2442 HeatPumpFrostProtection."""

    TOPIC = "open3e/680_2442_HeatPumpFrostProtection"

    def test_discovery_topic_contains_binary_sensor(self, generator_en):
        results = generator_en.generate_discovery_message(self.TOPIC, "1.0", test_mode=False)
        assert results
        disc_topic, _ = results[0]
        assert "binary_sensor/" in disc_topic

    def test_payload_on_off(self, generator_en):
        _, payload = generator_en.generate_discovery_message(self.TOPIC, "1.0", test_mode=False)[0]
        cfg = json.loads(payload)
        assert cfg["payload_on"] == "1"
        assert cfg["payload_off"] == "0"

    def test_has_object_id(self, generator_en):
        _, payload = generator_en.generate_discovery_message(self.TOPIC, "1.0", test_mode=False)[0]
        cfg = json.loads(payload)
        assert "object_id" in cfg

    def test_has_origin(self, generator_en):
        _, payload = generator_en.generate_discovery_message(self.TOPIC, "1.0", test_mode=False)[0]
        cfg = json.loads(payload)
        assert "origin" in cfg
        assert cfg["origin"]["name"] == "Open3E Bridge"

    def test_has_availability_topic(self, generator_en):
        _, payload = generator_en.generate_discovery_message(self.TOPIC, "1.0", test_mode=False)[0]
        cfg = json.loads(payload)
        assert cfg["availability_topic"] == "open3e/LWT"


class TestBinaryMixer1Pump:
    """DID 401 MixerOneCircuitPump."""

    TOPIC = "open3e/680_401_MixerOneCircuitPump"

    def test_entity_type_binary_sensor(self, generator_en):
        results = generator_en.generate_discovery_message(self.TOPIC, "1.0")
        disc_topic, _ = results[0]
        assert "binary_sensor/" in disc_topic

    def test_icon_pump(self, generator_en):
        _, payload = generator_en.generate_discovery_message(self.TOPIC, "1.0")[0]
        cfg = json.loads(payload)
        assert cfg["icon"] == "mdi:pump"

    def test_has_object_id(self, generator_en):
        _, payload = generator_en.generate_discovery_message(self.TOPIC, "1.0")[0]
        assert "object_id" in json.loads(payload)

    def test_has_origin(self, generator_en):
        cfg = json.loads(generator_en.generate_discovery_message(self.TOPIC, "1.0")[0][1])
        assert "origin" in cfg

    def test_has_availability_topic(self, generator_en):
        cfg = json.loads(generator_en.generate_discovery_message(self.TOPIC, "1.0")[0][1])
        assert cfg["availability_topic"] == "open3e/LWT"


class TestBinaryCompressor:
    """DID 2351 HeatPumpCompressor."""

    TOPIC = "open3e/680_2351_HeatPumpCompressor"

    def test_entity_type_binary_sensor(self, generator_en):
        disc_topic, _ = generator_en.generate_discovery_message(self.TOPIC, "0.0")[0]
        assert "binary_sensor/" in disc_topic

    def test_payload_on_off(self, generator_en):
        cfg = json.loads(generator_en.generate_discovery_message(self.TOPIC, "0.0")[0][1])
        assert cfg["payload_on"] == "1"
        assert cfg["payload_off"] == "0"

    def test_has_object_id(self, generator_en):
        cfg = json.loads(generator_en.generate_discovery_message(self.TOPIC, "0.0")[0][1])
        assert "object_id" in cfg

    def test_has_origin(self, generator_en):
        cfg = json.loads(generator_en.generate_discovery_message(self.TOPIC, "0.0")[0][1])
        assert "origin" in cfg

    def test_has_availability_topic(self, generator_en):
        cfg = json.loads(generator_en.generate_discovery_message(self.TOPIC, "0.0")[0][1])
        assert cfg["availability_topic"] == "open3e/LWT"


class TestBinaryFrostProtectionState:
    """BIN-01: the raw payload must actually resolve to payload_on/payload_off.

    DID 2442 is published as a float ("0.0"/"1.0"). Without a normalizing
    value_template the state matches neither payload_on ("1") nor payload_off
    ("0"), and Home Assistant leaves the entity 'unknown' forever.
    """

    TOPIC = "open3e/6CF_2442_HeatPumpFrostProtection"

    def _config(self, generator_en, value):
        results = generator_en.generate_discovery_message(self.TOPIC, value, test_mode=False)
        assert results, "no discovery generated"
        return json.loads(results[0][1])

    def test_has_value_template(self, generator_en):
        cfg = self._config(generator_en, "0.0")
        assert "value_template" in cfg, "float payload needs normalization"

    @pytest.mark.parametrize("raw,expected_key", [
        ("0.0", "payload_off"),
        ("1.0", "payload_on"),
        ("0", "payload_off"),
        ("1", "payload_on"),
    ])
    def test_rendered_state_matches_a_payload(self, generator_en, raw, expected_key):
        cfg = self._config(generator_en, raw)
        env = jinja2.Environment(undefined=jinja2.StrictUndefined)
        rendered = env.from_string(cfg["value_template"]).render(value=raw).strip()
        assert rendered == cfg[expected_key], (
            f"payload {raw!r} rendered to {rendered!r}, expected {cfg[expected_key]!r}"
        )
