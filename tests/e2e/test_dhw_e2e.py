"""E2E: DHW discovery messages via real MQTT broker."""

import json
import time

import paho.mqtt.client as mqtt
import pytest

from generators.homeassistant import HomeAssistantGenerator

pytestmark = pytest.mark.e2e

CONFIG_DIR = "config"


@pytest.fixture
def ha_generator():
    return HomeAssistantGenerator(
        config_dir=CONFIG_DIR,
        language="en",
        discovery_prefix="homeassistant",
        add_test_prefix=False,
    )


@pytest.fixture
def ha_generator_de():
    return HomeAssistantGenerator(
        config_dir=CONFIG_DIR,
        language="de",
        discovery_prefix="homeassistant",
        add_test_prefix=False,
    )


def _publish_and_collect(broker, topics_payloads, subscribe_filter, timeout=5):
    """Publish messages and collect what comes back for the published topics."""
    expected_topics = {t for t, _ in topics_payloads}
    received = {}

    def on_message(_client, _userdata, msg):
        if msg.topic in expected_topics:
            received[msg.topic] = json.loads(msg.payload.decode())

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect(broker["host"], broker["port"])
    client.subscribe(subscribe_filter)
    client.loop_start()

    time.sleep(0.5)  # let subscribe propagate

    for topic, payload in topics_payloads:
        client.publish(topic, payload, retain=True)

    time.sleep(timeout)
    client.loop_stop()
    client.disconnect()
    return [(t, p) for t, p in received.items()]


class TestDHWDiscoveryE2E:
    """Verify DHW entity names match ViCare via real MQTT round-trip."""

    def test_did_271_actual_name(self, mqtt_broker, ha_generator):
        """DID 271 sub Actual should have ViCare name 'Hot Water'."""
        msgs = ha_generator.generate_discovery_message(
            "open3e/680_271_DomesticHotWaterSensor/Actual", "48.2",
        )
        assert len(msgs) >= 1
        topic, payload_str = msgs[0]
        config = json.loads(payload_str)
        assert config["name"] == "Hot Water"

        # Round-trip through broker
        collected = _publish_and_collect(
            mqtt_broker,
            [(topic, payload_str)],
            "homeassistant/#",
            timeout=2,
        )
        assert len(collected) >= 1
        assert collected[0][1]["name"] == "Hot Water"

    def test_did_271_vicare_name_de(self, mqtt_broker, ha_generator_de):
        """DID 271 sub Actual in German should be 'Warmwasser' (ViCare parity)."""
        msgs = ha_generator_de.generate_discovery_message(
            "open3e/680_271_DomesticHotWaterSensor/Actual", "48.2",
        )
        assert len(msgs) >= 1
        topic, payload_str = msgs[0]
        config = json.loads(payload_str)
        assert config["name"] == "Warmwasser"

        # Round-trip through broker
        collected = _publish_and_collect(
            mqtt_broker,
            [(topic, payload_str)],
            "homeassistant/#",
            timeout=2,
        )
        assert len(collected) >= 1
        assert collected[0][1]["name"] == "Warmwasser"

    def test_did_396_name(self, mqtt_broker, ha_generator):
        """DID 396 (no subs) should have name 'DHW Setpoint'."""
        msgs = ha_generator.generate_discovery_message(
            "open3e/680_396_DomesticHotWaterTemperatureSetpoint", "50.0",
        )
        assert len(msgs) >= 1
        topic, payload_str = msgs[0]
        config = json.loads(payload_str)
        assert config["name"] == "DHW Setpoint"

        collected = _publish_and_collect(
            mqtt_broker,
            [(topic, payload_str)],
            "homeassistant/#",
            timeout=2,
        )
        assert len(collected) >= 1
        assert collected[0][1]["name"] == "DHW Setpoint"


class TestBufferStorageE2E:
    """Verify buffer storage entity name matches ViCare."""

    def test_did_3016_vicare_name_de(self, mqtt_broker, ha_generator_de):
        """DID 3016 in German must be 'Pufferspeicher' (ViCare exact)."""
        msgs = ha_generator_de.generate_discovery_message(
            "open3e/680_3016_HeatingBufferTemperatureSensor/Actual",
            "25.4",
        )
        assert len(msgs) >= 1
        topic, payload_str = msgs[0]
        config = json.loads(payload_str)
        assert config["name"] == "Pufferspeicher"

        # MQTT round-trip
        collected = _publish_and_collect(
            mqtt_broker,
            [(topic, payload_str)],
            "homeassistant/#",
            timeout=2,
        )
        assert len(collected) >= 1
        assert collected[0][1]["name"] == "Pufferspeicher"

    def test_did_3016_name_en(self, mqtt_broker, ha_generator):
        """DID 3016 in English: 'Heating Buffer Temperature'."""
        msgs = ha_generator.generate_discovery_message(
            "open3e/680_3016_HeatingBufferTemperatureSensor/Actual",
            "25.4",
        )
        assert len(msgs) >= 1
        _, payload_str = msgs[0]
        config = json.loads(payload_str)
        assert config["name"] == "Heating Buffer Temperature"

    def test_did_3016_entity_properties(self, mqtt_broker, ha_generator_de):
        """DID 3016 must be temperature sensor with correct unit."""
        msgs = ha_generator_de.generate_discovery_message(
            "open3e/680_3016_HeatingBufferTemperatureSensor/Actual",
            "25.4",
        )
        _, payload_str = msgs[0]
        config = json.loads(payload_str)
        assert config["device_class"] == "temperature"
        assert config["unit_of_measurement"] == "°C"
        assert config["state_class"] == "measurement"
        assert "homeassistant/sensor/" in msgs[0][0]
