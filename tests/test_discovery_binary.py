"""TEST-03: Binary sensor discovery messages."""
import json


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
        assert cfg["payload_on"] == "1.0"
        assert cfg["payload_off"] == "0.0"

    def test_has_default_entity_id(self, generator_en):
        _, payload = generator_en.generate_discovery_message(self.TOPIC, "1.0", test_mode=False)[0]
        cfg = json.loads(payload)
        assert "default_entity_id" in cfg

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

    def test_has_default_entity_id(self, generator_en):
        _, payload = generator_en.generate_discovery_message(self.TOPIC, "1.0")[0]
        assert "default_entity_id" in json.loads(payload)

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
        assert cfg["payload_on"] == "1.0"
        assert cfg["payload_off"] == "0.0"

    def test_has_default_entity_id(self, generator_en):
        cfg = json.loads(generator_en.generate_discovery_message(self.TOPIC, "0.0")[0][1])
        assert "default_entity_id" in cfg

    def test_has_origin(self, generator_en):
        cfg = json.loads(generator_en.generate_discovery_message(self.TOPIC, "0.0")[0][1])
        assert "origin" in cfg

    def test_has_availability_topic(self, generator_en):
        cfg = json.loads(generator_en.generate_discovery_message(self.TOPIC, "0.0")[0][1])
        assert cfg["availability_topic"] == "open3e/LWT"
