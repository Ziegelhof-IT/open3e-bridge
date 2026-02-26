#!/usr/bin/env python3
"""
Open3E Home Assistant Bridge

Automatische Erstellung von Home Assistant MQTT Discovery Messages
aus Open3E Datenpunkten.
"""
import argparse
import logging
import time
import json
from typing import Dict, Set
import paho.mqtt.client as mqtt
from pathlib import Path
import re

from generators.homeassistant import HomeAssistantGenerator

logger = logging.getLogger("open3e_bridge")

class Open3EBridge:
    def __init__(self, mqtt_host: str = "localhost", mqtt_port: int = 1883, 
                 mqtt_user: str = None, mqtt_password: str = None,
                 language: str = "de", test_mode: bool = True,
                 discovery_prefix: str = "homeassistant",
                 add_test_prefix: bool = True):
        
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.test_mode = test_mode
        self.discovery_prefix = discovery_prefix
        self.add_test_prefix = add_test_prefix
        
        # MQTT Client
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        
        if mqtt_user and mqtt_password:
            self.client.username_pw_set(mqtt_user, mqtt_password)
        
        # Generator
        config_dir = Path(__file__).parent / "config"
        self.generator = HomeAssistantGenerator(str(config_dir), language, discovery_prefix=discovery_prefix, add_test_prefix=add_test_prefix)
        
        # Cache veröffentlichter Discovery-Konfigurationen (Topic -> Payload)
        self.published_configs: Dict[str, str] = {}
        
        logger.info("Open3E Bridge initialized: MQTT=%s:%d lang=%s test=%s prefix=%s",
                    mqtt_host, mqtt_port, language, test_mode, self.generator.discovery_prefix)
        
    def start(self):
        """Startet die Bridge"""
        try:
            logger.info("Connecting to MQTT broker %s:%d ...", self.mqtt_host, self.mqtt_port)
            self.client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.client.loop_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.client.disconnect()
        except Exception as e:
            logger.error("Error: %s", e)

    def cleanup(self, timeout_s: float = 2.0):
        """Löscht alte Discovery-Konfigurationen (Retain leeren) für open3e-Entities."""
        retained: Set[str] = set()

        def _on_connect(client, userdata, flags, rc):
            if rc == 0:
                client.subscribe(f"{self.generator.discovery_prefix}/#")
            else:
                logger.error("Failed to connect for cleanup: rc=%s", rc)

        def _on_message(client, userdata, msg):
            if getattr(msg, 'retain', False):
                retained.add(msg.topic)

        self.client.on_connect = _on_connect
        self.client.on_message = _on_message

        logger.info("Connecting for cleanup to %s:%d ...", self.mqtt_host, self.mqtt_port)
        self.client.connect(self.mqtt_host, self.mqtt_port, 60)
        self.client.loop_start()
        time.sleep(timeout_s)
        self.client.loop_stop()

        pattern = re.compile(rf"^{re.escape(self.generator.discovery_prefix)}/(sensor|number|select|binary_sensor|climate)/open3e_[^/]+/config$")
        targets = [t for t in retained if pattern.match(t)]
        logger.info("Found %d retained under prefix, %d matching open3e entities.", len(retained), len(targets))
        for t in targets:
            logger.debug("Clearing retain: %s", t)
            self.client.publish(t, payload="", retain=True)
        self.client.disconnect()
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT Connect Callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            client.subscribe("open3e/+/+")
            client.subscribe("open3e/+")
            client.subscribe("open3e/LWT")
            logger.debug("Subscribed to open3e topics")
        else:
            logger.error("Failed to connect to MQTT broker: %s", rc)
    
    def _on_message(self, client, userdata, msg):
        """MQTT Message Callback"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # Skip LWT und andere Systemnachrichten
            if '/LWT' in topic or topic.endswith('/LWT'):
                return
                
            logger.debug("Processing: %s = %s", topic, payload)
            
            # Generiere Discovery Messages
            discovery_messages = self.generator.generate_discovery_message(
                topic, payload, self.test_mode
            )
            
            # Publiziere Discovery Messages
            for discovery_topic, discovery_payload in discovery_messages:
                previous = self.published_configs.get(discovery_topic)
                if previous == discovery_payload:
                    # No change, skip re-publish
                    continue
                logger.info("Publishing discovery: %s", discovery_topic)
                if self.test_mode:
                    logger.debug("Payload: %s", discovery_payload)
                # Always use instance client to support simulation calls
                self.client.publish(discovery_topic, discovery_payload, retain=True)
                self.published_configs[discovery_topic] = discovery_payload
            
        except Exception as e:
            logger.error("Error processing message %s: %s", topic, e)

def main():
    parser = argparse.ArgumentParser(description="Open3E Home Assistant Bridge")
    parser.add_argument("--mqtt-host", default="localhost", help="MQTT broker host")
    parser.add_argument("--mqtt-port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--mqtt-user", help="MQTT username")
    parser.add_argument("--mqtt-password", help="MQTT password")
    parser.add_argument("--language", default="de", choices=["de", "en"], help="Language for entity names")
    parser.add_argument("--test", action="store_true", help="Test mode (publish to test/ topics)")
    parser.add_argument("--discovery-prefix", default=None, help="MQTT discovery prefix (default: homeassistant; with --test => test/homeassistant)")
    parser.add_argument("--no-test-prefix", action="store_true", help="Do not prepend 'test/' to discovery prefix even in simulation/test mode")
    parser.add_argument("--simulate", help="Simulate with MQTT messages from file")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup retained discovery for open3e entities")
    parser.add_argument("--validate-config", action="store_true", help="Validate datapoints/templates and exit")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Logging level (default: INFO)")

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    
    # Test Mode nur wenn explizit gewünscht
    test_mode = args.test or bool(args.simulate)

    # Discovery Prefix auflösen
    if args.discovery_prefix:
        discovery_prefix = args.discovery_prefix
    else:
        discovery_prefix = "homeassistant"
        if test_mode and not args.no_test_prefix:
            discovery_prefix = f"test/{discovery_prefix}"
    
    bridge = Open3EBridge(
        mqtt_host=args.mqtt_host,
        mqtt_port=args.mqtt_port,
        mqtt_user=args.mqtt_user,
        mqtt_password=args.mqtt_password,
        language=args.language,
        test_mode=test_mode,
        discovery_prefix=discovery_prefix,
        add_test_prefix=not args.no_test_prefix
    )
    
    # Validate-only mode
    if args.validate_config:
        # Use the same generator as bridge to validate
        validator = HomeAssistantGenerator(str(Path(__file__).parent / "config"), args.language, discovery_prefix=discovery_prefix)
        result = validator.validate()
        if result["errors"]:
            logger.error("Config validation FAILED:")
            for e in result["errors"]:
                logger.error("  %s", e)
            raise SystemExit(1)
        else:
            logger.info("Config validation OK.")
            raise SystemExit(0)

    # Cleanup-only mode
    if args.cleanup:
        bridge.cleanup()
        raise SystemExit(0)

    # Simulation Mode
    if args.simulate:
        simulate_from_file(bridge, args.simulate)
    else:
        bridge.start()

def simulate_from_file(bridge: Open3EBridge, filepath: str):
    """Simuliert MQTT Messages aus Datei"""
    logger.info("Simulating MQTT messages from %s", filepath)
    
    try:
        # Ensure MQTT connection for publishing discovery during simulation
        logger.info("Connecting to MQTT broker %s:%d for simulation...", bridge.mqtt_host, bridge.mqtt_port)
        bridge.client.connect(bridge.mqtt_host, bridge.mqtt_port, 60)
        bridge.client.loop_start()
        # Fake MQTT Client für Simulation
        class FakeMessage:
            def __init__(self, topic, payload):
                self.topic = topic
                self.payload = payload.encode('utf-8')
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Format: topic payload
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    topic, payload = parts
                    msg = FakeMessage(topic, payload)
                    bridge._on_message(None, None, msg)
                    time.sleep(0.1)  # Kurze Pause zwischen Messages
        # Let any pending publishes flush
        time.sleep(0.5)
        bridge.client.loop_stop()
        bridge.client.disconnect()
    except FileNotFoundError:
        logger.error("File not found: %s", filepath)
    except Exception as e:
        logger.error("Error in simulation: %s", e)

if __name__ == "__main__":
    main()
