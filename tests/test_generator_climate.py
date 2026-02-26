import json
from pathlib import Path

from generators.homeassistant import HomeAssistantGenerator

CONFIG_DIR = str(Path(__file__).resolve().parents[1] / "config")


def _find_payload_by_type(results, entity_type):
    for topic, payload in results:
        if f"/{entity_type}/" in topic:
            return topic, json.loads(payload)
    return None, None


def test_climate_discovery_hk1():
    gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", discovery_prefix="homeassistant")
    topic = "open3e/680_1415_MixerOneCircuitOperationState/Mode/ID"
    results = gen.generate_discovery_message(topic, "1", test_mode=True)
    t, data = _find_payload_by_type(results, "climate")
    assert t and data
    assert t.startswith("test/homeassistant/climate/open3e_680_1415_climate/config")
    assert data["mode_state_topic"] == topic
    assert data["temperature_state_topic"].endswith("1643_MixerOneCircuitCurrentTemperatureSetpoint")


def test_climate_discovery_hk2():
    gen = HomeAssistantGenerator(config_dir=CONFIG_DIR, language="en", discovery_prefix="homeassistant")
    topic = "open3e/680_1416_MixerTwoCircuitOperationState/Mode/ID"
    results = gen.generate_discovery_message(topic, "0", test_mode=True)
    t, data = _find_payload_by_type(results, "climate")
    assert t and data
    assert t.startswith("test/homeassistant/climate/open3e_680_1416_climate/config")
    assert data["mode_state_topic"] == topic
    assert data["temperature_state_topic"].endswith("1644_MixerTwoCircuitCurrentTemperatureSetpoint")
