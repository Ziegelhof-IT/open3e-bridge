#!/usr/bin/env python3
"""
Open3E Home Assistant Bridge

Automatische Erstellung von Home Assistant MQTT Discovery Messages
aus Open3E Datenpunkten.
"""
import argparse
import json
import logging
import os
import re
import signal
import threading
import time
from collections import Counter
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from pathlib import Path

import paho.mqtt.client as mqtt

from generators.homeassistant import HomeAssistantGenerator  # noqa: F401 — used by tests
from generators.registry import get_generator_class

try:
    __version__ = pkg_version("open3e-bridge")
except PackageNotFoundError:
    __version__ = "0.1.0-dev"

logger = logging.getLogger("open3e_bridge")

class Open3EBridge:
    def __init__(self, mqtt_host: str = "localhost", mqtt_port: int = 1883,
                 mqtt_user: str | None = None, mqtt_password: str | None = None,
                 language: str = "de", test_mode: bool = True,
                 discovery_prefix: str = "homeassistant",
                 add_test_prefix: bool = True,
                 config_dir: str | None = None,
                 diagnostics_interval: int = 0,
                 auto_discover: bool = True,
                 generator_type: str = "homeassistant",
                 profile: str = "auto"):

        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_password = mqtt_password
        self.test_mode = test_mode
        self.discovery_prefix = discovery_prefix
        self.add_test_prefix = add_test_prefix

        # MQTT Client (paho-mqtt v2 API)
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # type: ignore[attr-defined]
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        if mqtt_user and mqtt_password:
            self.client.username_pw_set(mqtt_user, mqtt_password)

        # LWT (Last Will and Testament)
        self.lwt_topic = "open3e/bridge/LWT"
        self.client.will_set(self.lwt_topic, "offline", qos=1, retain=True)

        # ROB-02: Reconnect with exponential backoff
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)

        # Generator — use registry to select generator type
        resolved_config_dir = config_dir or str(Path(__file__).parent / "config")
        generator_cls = get_generator_class(generator_type)
        self.generator = generator_cls(
            resolved_config_dir, language,
            discovery_prefix=discovery_prefix, add_test_prefix=add_test_prefix,
            auto_discover=auto_discover, profile=profile,
        )

        # Cache veröffentlichter Discovery-Konfigurationen (Topic -> Payload)
        self.published_configs: dict[str, str] = {}

        # Diagnostics counters
        self._start_time = time.monotonic()
        self._messages_processed = 0
        self._discovery_published = 0
        self._entity_types: Counter = Counter()
        self._failed_writes = 0
        self._last_error: str = ""

        # Periodic diagnostics publishing
        self._diagnostics_interval = diagnostics_interval
        self._diagnostics_topic = "open3e/bridge/diagnostics"
        self._diagnostics_timer: threading.Timer | None = None

        # Health entity
        self._health_topic = "open3e/bridge/health"
        self._health_attributes_topic = "open3e/bridge/health/attributes"

        # A01: Write verification — pending writes awaiting read-back
        # Key: (ecu_addr, did) → expected value (str)
        self._pending_writes: dict[tuple[str, int], str] = {}

        # A08: COP calculation — latest power values
        self._electrical_power: float | None = None  # DID 2488
        self._thermal_power: float | None = None     # DID 2496
        self._cop_topic = "open3e/bridge/cop"

        # A09: NRC code mapping for human-readable logging
        self._nrc_codes: dict[str, str] = {
            "0x22": "ConditionsNotCorrect — device rejected (wrong mode/state)",
            "0x31": "RequestOutOfRange — value outside allowed range",
            "0x14": "ResponseTooLong — response data too large",
            "0x33": "SecurityAccessDenied — authentication required",
        }

        logger.info("Open3E Bridge v%s initialized: MQTT=%s:%d lang=%s config=%s prefix=%s generator=%s auto_discover=%s",
                    __version__, mqtt_host, mqtt_port, language, resolved_config_dir,
                    self.generator.discovery_prefix, generator_type, auto_discover)

    def _schedule_diagnostics(self):
        """Schedule the next periodic diagnostics publish."""
        if self._diagnostics_interval <= 0:
            return
        self._diagnostics_timer = threading.Timer(
            self._diagnostics_interval, self._publish_diagnostics
        )
        self._diagnostics_timer.daemon = True
        self._diagnostics_timer.start()

    def _publish_diagnostics(self):
        """Publish diagnostics JSON to MQTT and reschedule."""
        try:
            diag = self.get_diagnostics()
            self.client.publish(
                self._diagnostics_topic,
                json.dumps(diag),
                retain=True,
            )
            logger.debug("Published diagnostics: %s", diag)
        except Exception as e:
            logger.warning("Failed to publish diagnostics: %s", e)
        self._schedule_diagnostics()

    def _cancel_diagnostics(self):
        """Cancel the periodic diagnostics timer."""
        if self._diagnostics_timer is not None:
            self._diagnostics_timer.cancel()
            self._diagnostics_timer = None

    def _graceful_shutdown(self, signum=None, frame=None):
        """Graceful shutdown: publish offline LWT, then disconnect."""
        self._cancel_diagnostics()
        sig_name = signal.Signals(signum).name if signum else "unknown"
        logger.info("Received %s, shutting down gracefully...", sig_name)
        try:
            self.client.publish(self.lwt_topic, "offline", qos=1, retain=True)
            self.client.disconnect()
        except Exception:  # noqa: S110
            pass  # best-effort during shutdown

    def start(self):
        """Startet die Bridge"""
        signal.signal(signal.SIGTERM, self._graceful_shutdown)
        signal.signal(signal.SIGINT, self._graceful_shutdown)
        try:
            logger.info("Connecting to MQTT broker %s:%d ...", self.mqtt_host, self.mqtt_port)
            self.client.connect(self.mqtt_host, self.mqtt_port, 60)
            self.client.loop_forever()
        except KeyboardInterrupt:
            self._graceful_shutdown(signum=signal.SIGINT)
        except Exception as e:
            logger.error("Fatal error (host=%s, port=%d): %s", self.mqtt_host, self.mqtt_port, e)
            raise SystemExit(1) from e

    def cleanup(self, timeout_s: float = 2.0):
        """Löscht alte Discovery-Konfigurationen (Retain leeren) für open3e-Entities."""
        retained: set[str] = set()

        def _on_connect(client, userdata, connect_flags, reason_code, properties):
            if reason_code == 0:
                client.subscribe(f"{self.generator.discovery_prefix}/#")
            else:
                logger.error("Failed to connect for cleanup: rc=%s", reason_code)

        def _on_message(client, userdata, msg):
            if getattr(msg, 'retain', False):
                retained.add(msg.topic)

        self.client.on_connect = _on_connect
        self.client.on_message = _on_message

        logger.info("Connecting for cleanup to %s:%d ...", self.mqtt_host, self.mqtt_port)
        self.client.connect(self.mqtt_host, self.mqtt_port, 60)
        self.client.loop_start()
        time.sleep(timeout_s)

        pattern = re.compile(rf"^{re.escape(self.generator.discovery_prefix)}/(sensor|number|select|binary_sensor|climate|switch|button|water_heater)/open3e_[^/]+/config$")
        targets = [t for t in retained if pattern.match(t)]
        logger.info("Found %d retained under prefix, %d matching open3e entities.", len(retained), len(targets))
        for t in targets:
            logger.debug("Clearing retain: %s", t)
            self.client.publish(t, payload="", retain=True)

        # Let queued publishes flush while network thread is still running
        if targets:
            time.sleep(0.5)
        self.client.loop_stop()
        self.client.disconnect()

    def _on_connect(self, client, userdata, connect_flags, reason_code, properties):
        """MQTT Connect Callback (paho v2)"""
        if reason_code == 0:
            logger.info("Connected to MQTT broker")
            client.publish(self.lwt_topic, "online", qos=1, retain=True)
            client.subscribe("open3e/+/+")
            client.subscribe("open3e/+")
            client.subscribe("open3e/LWT")
            # ROB-01: Re-publish discovery when HA restarts
            client.subscribe("homeassistant/status")
            logger.debug("Subscribed to open3e topics and homeassistant/status")
            # A08: Publish COP sensor discovery
            self._publish_cop_discovery()
            # Publish health entity discovery
            self._publish_health_discovery()
            self._publish_health_state("ON")
            self._schedule_diagnostics()
        else:
            reason_hints = {
                1: "incorrect protocol version",
                2: "invalid client identifier",
                3: "server unavailable",
                4: "bad username or password — check --mqtt-user and --mqtt-password (or MQTT_PASSWORD env var)",
                5: "not authorized — check MQTT broker ACL configuration",
            }
            hint = reason_hints.get(int(reason_code) if isinstance(reason_code, int) else 0, "")
            extra = f" ({hint})" if hint else ""
            logger.error("Failed to connect to MQTT broker at %s:%d: rc=%s%s",
                         self.mqtt_host, self.mqtt_port, reason_code, extra)

    def _republish_all_discovery(self):
        """ROB-01: Re-publish all cached discovery configs (e.g. after HA restart)."""
        count = len(self.published_configs)
        if count == 0:
            return
        logger.info("Re-publishing %d cached discovery configs", count)
        for topic, payload in self.published_configs.items():
            self.client.publish(topic, payload, retain=True)

    # ------------------------------------------------------------------
    # A01: Write verification
    # ------------------------------------------------------------------

    def write_and_verify(self, ecu_addr: str, did: int, value: str):
        """Publish a write command and schedule a read-back verification.

        After the write, a read command is published. When the state topic
        updates, _check_write_verification compares the value.
        """
        # Publish the write command
        write_cmd = json.dumps({"mode": "write", "data": [[did, value]]})
        self.client.publish("open3e/cmnd", write_cmd)
        logger.info("Write command sent: DID %d = %s", did, value)

        # Track the pending write for verification
        self._pending_writes[(ecu_addr, did)] = str(value)

        # Publish a read command to verify
        read_cmd = json.dumps({"mode": "read", "data": [did]})
        self.client.publish("open3e/cmnd", read_cmd)
        logger.debug("Read-back command sent for DID %d", did)

    def _check_write_verification(self, ecu_addr: str, did: int, actual_value: str):
        """Check if a pending write matches the read-back value."""
        key = (ecu_addr, did)
        expected = self._pending_writes.pop(key, None)
        if expected is None:
            return
        if str(actual_value).strip() != str(expected).strip():
            self._failed_writes += 1
            msg = (f"Write verification FAILED for DID {did}: expected={expected}, actual={actual_value}. "
                   f"The controller may have rejected the value (out of range or wrong mode). "
                   f"Check if the value is within allowed limits.")
            self._last_error = msg
            logger.warning(msg)
            self._publish_health_state("ON", error=msg)
        else:
            logger.info("Write verification OK for DID %d: %s", did, actual_value)

    # ------------------------------------------------------------------
    # A08: COP calculation
    # ------------------------------------------------------------------

    def _publish_cop_discovery(self):
        """Publish HA MQTT Discovery config for the COP sensor."""
        prefix = self.discovery_prefix or "homeassistant"
        if self.add_test_prefix and self.test_mode and not prefix.startswith("test/"):
            prefix = f"test/{prefix}"
        discovery_topic = f"{prefix}/sensor/open3e_bridge_cop/config"
        config = {
            "name": "COP",
            "unique_id": "open3e_bridge_cop",
            "object_id": "open3e_bridge_cop",
            "state_topic": self._cop_topic,
            "device_class": "power_factor",
            "icon": "mdi:gauge",
            "availability_topic": "open3e/bridge/LWT",
            "payload_available": "online",
            "payload_not_available": "offline",
            "device": {
                "identifiers": ["open3e_bridge"],
                "name": "Open3E Bridge",
                "manufacturer": "Open3E",
            },
            "origin": {
                "name": "Open3E Bridge",
                "sw_version": __version__,
                "support_url": "https://github.com/open3e/open3e-bridge",
            },
        }
        payload = json.dumps(config, ensure_ascii=False)
        self.client.publish(discovery_topic, payload, retain=True)
        self.published_configs[discovery_topic] = payload
        logger.debug("Published COP discovery: %s", discovery_topic)

    def _update_cop(self, did: int, value: str):
        """Update COP calculation when power DIDs arrive."""
        try:
            fval = float(value)
        except (ValueError, TypeError):
            return

        if did == 2488:
            self._electrical_power = fval
        elif did == 2496:
            self._thermal_power = fval
        else:
            return

        # Calculate and publish COP if both values available and electrical > 0
        if (self._electrical_power is not None
                and self._thermal_power is not None
                and self._electrical_power > 0):
            cop = round(self._thermal_power / self._electrical_power, 2)
            self.client.publish(self._cop_topic, str(cop), retain=True)
            logger.debug("COP updated: %.2f (thermal=%.0fW, electrical=%.0fW)",
                         cop, self._thermal_power, self._electrical_power)

    # ------------------------------------------------------------------
    # Health entity (binary_sensor with diagnostic attributes)
    # ------------------------------------------------------------------

    def _publish_health_discovery(self):
        """Publish HA MQTT Discovery for bridge health binary_sensor (entity_category: diagnostic)."""
        prefix = self.discovery_prefix or "homeassistant"
        if self.add_test_prefix and self.test_mode and not prefix.startswith("test/"):
            prefix = f"test/{prefix}"
        discovery_topic = f"{prefix}/binary_sensor/open3e_bridge_status/config"
        config = {
            "name": "Bridge Status",
            "unique_id": "open3e_bridge_status",
            "object_id": "open3e_bridge_status",
            "state_topic": self._health_topic,
            "payload_on": "ON",
            "payload_off": "OFF",
            "device_class": "connectivity",
            "entity_category": "diagnostic",
            "json_attributes_topic": self._health_attributes_topic,
            "availability_topic": self.lwt_topic,
            "payload_available": "online",
            "payload_not_available": "offline",
            "device": {
                "identifiers": ["open3e_bridge"],
                "name": "Open3E Bridge",
                "manufacturer": "Open3E",
            },
            "origin": {
                "name": "Open3E Bridge",
                "sw_version": __version__,
                "support_url": "https://github.com/open3e/open3e-bridge",
            },
        }
        payload = json.dumps(config, ensure_ascii=False)
        self.client.publish(discovery_topic, payload, retain=True)
        self.published_configs[discovery_topic] = payload
        logger.debug("Published health entity discovery: %s", discovery_topic)

    def _publish_health_state(self, state: str = "ON", error: str | None = None):
        """Publish health state and attributes to MQTT."""
        try:
            self.client.publish(self._health_topic, state, retain=True)
            uptime = time.monotonic() - self._start_time
            attributes = {
                "version": __version__,
                "uptime_s": round(uptime, 1),
                "messages_processed": self._messages_processed,
                "discovery_published": self._discovery_published,
                "failed_writes": self._failed_writes,
                "last_error": error or self._last_error or "none",
                "entities_cached": len(self.published_configs),
            }
            self.client.publish(
                self._health_attributes_topic,
                json.dumps(attributes, ensure_ascii=False),
                retain=True,
            )
        except Exception as e:
            logger.debug("Failed to publish health state: %s", e)

    # ------------------------------------------------------------------
    # A09: NRC handling
    # ------------------------------------------------------------------

    _NRC_PATTERN = re.compile(r"NRC\s*(0x[0-9a-fA-F]{2})")

    def _is_nrc_payload(self, payload: str) -> bool:
        """Check if payload is an NRC (Negative Response Code) from open3e."""
        if not payload:
            return False
        stripped = payload.strip()
        return stripped.startswith("NRC") or stripped.startswith("ConditionsNotCorrect") or stripped.startswith("RequestOutOfRange")

    def _handle_nrc(self, topic: str, payload: str) -> bool:
        """Handle NRC payloads — log human-readable message, return True if NRC detected."""
        if not self._is_nrc_payload(payload):
            return False

        match = self._NRC_PATTERN.search(payload)
        if match:
            code = match.group(1)
            meaning = self._nrc_codes.get(code, f"Unknown NRC code {code}")
            msg = f"NRC on {topic}: {code} ({meaning})"
            logger.warning(msg)
            self._last_error = msg
        else:
            msg = f"NRC on {topic}: {payload.strip()}"
            logger.warning(msg)
            self._last_error = msg
        self._publish_health_state("ON", error=self._last_error)
        return True

    # ------------------------------------------------------------------
    # Main message processing
    # ------------------------------------------------------------------

    def process_message(self, topic: str, payload: str):
        """Public API: process an Open3E message (topic + decoded payload string).

        Use this for simulation, testing, or feeding messages from non-MQTT sources.
        """
        # ROB-01: HA birth message → republish all discovery
        if topic == "homeassistant/status" and payload == "online":
            self._republish_all_discovery()
            return

        # Skip LWT und andere Systemnachrichten
        if '/LWT' in topic or topic.endswith('/LWT'):
            return

        logger.debug("Processing: %s = %s", topic, payload)
        self._messages_processed += 1

        # A09: NRC detection — log but don't generate discovery
        if self._handle_nrc(topic, payload):
            return

        # A08: COP calculation for power DIDs
        parsed = self.generator.parse_open3e_topic(topic)
        if parsed:
            did = parsed['did']
            ecu_addr = parsed['ecu_addr']
            self._update_cop(did, payload)
            # A01: Write verification check
            self._check_write_verification(ecu_addr, did, payload)

        # Generiere Discovery Messages
        discovery_messages = self.generator.generate_discovery_message(
            topic, payload, self.test_mode
        )

        # Publiziere Discovery Messages
        for discovery_topic, discovery_payload in discovery_messages:
            previous = self.published_configs.get(discovery_topic)
            if previous == discovery_payload:
                continue
            logger.info("Publishing discovery: %s", discovery_topic)
            if self.test_mode:
                logger.debug("Payload: %s", discovery_payload)
            self.client.publish(discovery_topic, discovery_payload, retain=True)
            self.published_configs[discovery_topic] = discovery_payload
            self._discovery_published += 1
            # Track entity type from discovery topic path
            parts = discovery_topic.split("/")
            if len(parts) >= 3:
                self._entity_types[parts[-3]] += 1

    def _on_message(self, client, userdata, msg):
        """MQTT Message Callback — delegates to process_message()."""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            self.process_message(topic, payload)
        except UnicodeDecodeError:
            logger.warning("Non-UTF-8 payload on topic %s, skipping", msg.topic)
        except json.JSONDecodeError as e:
            logger.warning("Invalid JSON on topic %s: %s", msg.topic, e)
        except (ValueError, KeyError) as e:
            logger.warning("Bad data on topic %s: %s", msg.topic, e)
        except Exception as e:
            logger.error("Unexpected error processing %s: %s", msg.topic, e, exc_info=True)

    def get_diagnostics(self) -> dict[str, object]:
        """Return bridge diagnostics as a dict (for monitoring / health checks)."""
        uptime = time.monotonic() - self._start_time
        return {
            "version": __version__,
            "uptime_s": round(uptime, 1),
            "messages_processed": self._messages_processed,
            "discovery_published": self._discovery_published,
            "entities_cached": len(self.published_configs),
            "entity_types": dict(self._entity_types),
            "auto_discovered_entities": self.generator.auto_discovered_count,
            "failed_writes": self._failed_writes,
            "last_error": self._last_error or "none",
        }

    def log_entity_summary(self):
        """Log a summary of discovered entity types."""
        if not self._entity_types:
            return
        parts = [f"{count} {etype}" for etype, count in sorted(self._entity_types.items())]
        logger.info("Entity summary: %s (total: %d)", ", ".join(parts), sum(self._entity_types.values()))

    def dump_entities(self):
        """Print all configured entities to stdout (no MQTT connection needed)."""
        datapoints = self.generator.datapoints.get("datapoints", {}) or {}
        type_counter: Counter = Counter()
        print(f"{'DID':<6} {'Type':<25} {'Name':<40} {'Device':<12} {'Subs'}")
        print("-" * 100)
        for did_str, dp in sorted(datapoints.items(), key=lambda x: int(x[0])):
            dp_type = dp.get("type", "?")
            name = self.generator.translate_name(dp.get("name", "?"))
            device = dp.get("device", "-")
            subs = dp.get("subs", {})
            sub_keys = ", ".join(subs.keys()) if subs else "(all)"
            # Determine HA entity type from type template
            template = self.generator.type_templates.get(dp_type, {})
            ha_type = template.get("component", dp_type)
            type_counter[ha_type] += 1
            print(f"{did_str:<6} {dp_type:<25} {name:<40} {device:<12} {sub_keys}")
        print("-" * 100)
        total = sum(type_counter.values())
        summary = ", ".join(f"{c} {t}" for t, c in sorted(type_counter.items()))
        print(f"Total: {total} entities ({summary})")

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        """MQTT Disconnect Callback (paho v2)"""
        if reason_code == 0:
            logger.info("Disconnected from MQTT broker")
        else:
            logger.warning("Unexpected disconnect from MQTT broker: %s", reason_code)

def main():
    parser = argparse.ArgumentParser(description="Open3E Home Assistant Bridge")
    parser.add_argument("--version", action="version", version=f"open3e-bridge {__version__}")
    parser.add_argument("--mqtt-host", default="localhost", help="MQTT broker host")
    parser.add_argument("--mqtt-port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--mqtt-user", help="MQTT username")
    parser.add_argument("--mqtt-password", help="MQTT password (or set MQTT_PASSWORD env var)")
    parser.add_argument("--language", default="de", choices=["de", "en"], help="Language for entity names")
    parser.add_argument("--config-dir", help="Path to config directory (default: bundled config)")
    parser.add_argument("--test", action="store_true", help="Test mode (publish to test/ topics)")
    parser.add_argument("--discovery-prefix", default=None, help="MQTT discovery prefix (default: homeassistant; with --test => test/homeassistant)")
    parser.add_argument("--no-test-prefix", action="store_true", help="Do not prepend 'test/' to discovery prefix even in simulation/test mode")
    parser.add_argument("--simulate", help="Simulate with MQTT messages from file")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup retained discovery for open3e entities")
    parser.add_argument("--validate-config", action="store_true", help="Validate datapoints/templates and exit")
    parser.add_argument("--dump-entities", action="store_true", help="Show configured entities and exit (no MQTT needed)")
    parser.add_argument("--no-auto-discover", action="store_true",
                        help="Disable heuristic auto-discovery for DIDs not in datapoints.yaml (auto-discover is ON by default)")
    parser.add_argument("--profile", default="auto", choices=["auto", "vitocal", "vitodens", "common"],
                        help="Device profile (default: auto). Determines which DIDs are configured.")
    parser.add_argument("--generator", default="homeassistant",
                        help="Generator type (default: homeassistant). Use 'open3e-bridge --list-generators' to see available types")
    parser.add_argument("--list-generators", action="store_true",
                        help="List available generator types and exit")
    parser.add_argument("--diagnostics-interval", type=int, default=0,
                        help="Publish diagnostics every N seconds to open3e/bridge/diagnostics (0=disabled)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Logging level (default: INFO)")

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # List generators mode
    if args.list_generators:
        from generators.registry import list_generators
        for name, desc in list_generators():
            print(f"  {name:<20} {desc}")
        raise SystemExit(0)

    # MQTT password: CLI arg takes precedence, then env var
    mqtt_password = args.mqtt_password or os.environ.get("MQTT_PASSWORD")

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
        mqtt_password=mqtt_password,
        language=args.language,
        test_mode=test_mode,
        discovery_prefix=discovery_prefix,
        add_test_prefix=not args.no_test_prefix,
        config_dir=args.config_dir,
        diagnostics_interval=args.diagnostics_interval,
        auto_discover=not args.no_auto_discover,
        generator_type=args.generator,
        profile=args.profile,
    )

    # Validate-only mode
    if args.validate_config:
        result = bridge.generator.validate()
        if result["errors"]:
            logger.error("Config validation FAILED:")
            for e in result["errors"]:
                logger.error("  %s", e)
            raise SystemExit(1)
        else:
            logger.info("Config validation OK.")
            raise SystemExit(0)

    # Dump entities mode (no MQTT needed)
    if args.dump_entities:
        bridge.dump_entities()
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
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Format: topic payload
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    topic, payload = parts
                    bridge.process_message(topic, payload)
                    time.sleep(0.1)  # Kurze Pause zwischen Messages
        # Let any pending publishes flush
        time.sleep(0.5)
        bridge.client.loop_stop()
        bridge.client.disconnect()
    except FileNotFoundError:
        logger.error("File not found: %s", filepath)
    except Exception as e:
        logger.error("Error in simulation: %s", e)

if __name__ == "__main__":  # pragma: no cover
    main()
