"""
Home Assistant MQTT Discovery Generator
"""
import json
import logging
from typing import Any

from .base import BaseGenerator
from .heuristics import infer_entity_config

try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as pkg_version
    _SW_VERSION = pkg_version("open3e-bridge")
except (PackageNotFoundError, Exception):
    _SW_VERSION = "0.1.0-dev"

logger = logging.getLogger("open3e_bridge.generators.ha")

# Keys merged from type templates and dp_config overrides into entity config
_ENTITY_KEYS = (
    'device_class', 'unit_of_measurement', 'icon', 'state_class',
    'mode', 'payload_on', 'payload_off', 'state_on', 'state_off',
    'payload_press', 'value_template', 'command_template', 'options',
)

# Entity types that have no persistent state (no state_topic)
_STATELESS_ENTITY_TYPES = frozenset({"button"})


class HomeAssistantGenerator(BaseGenerator):
    def __init__(self, config_dir: str = "config", language: str = "en", discovery_prefix: str = "homeassistant", add_test_prefix: bool = True, auto_discover: bool = False):
        super().__init__(config_dir=config_dir, language=language)
        self.discovery_prefix = discovery_prefix
        self.add_test_prefix = add_test_prefix
        self.auto_discover = auto_discover
        self.auto_discovered_count = 0

    def generate_discovery_message(self, topic: str, value: str, test_mode: bool = True) -> list[tuple[str, str]]:
        """
        Generiert Home Assistant Discovery Messages für ein Open3E Topic

        Returns:
            List of (discovery_topic, discovery_payload) tuples
        """
        parsed = self.parse_open3e_topic(topic)
        if not parsed:
            return []

        did = parsed['did']
        ecu_addr = parsed['ecu_addr']

        # Prüfe ob DID ignoriert werden soll
        if self.is_ignored_did(did):
            return []

        # Aktualisiere Device-Info falls dieser DID Device-Identifikation enthält
        self.update_device_info(ecu_addr, did, value)

        # Hole Datenpunkt-Konfiguration
        dp_config = self.get_datapoint_config(did)
        if not dp_config:
            if not self.auto_discover:
                logger.debug("Skipping unknown DID %d (not configured)", did)
                return []
            # Tier 1: Heuristic auto-discovery fallback
            return self._generate_heuristic_discovery(parsed, test_mode)

        # Generiere Discovery Messages basierend auf Typ
        results = self._generate_typed_discovery(parsed, dp_config, value, test_mode)

        # Optionale Climate-Entität, wenn im Datapoint konfiguriert und passender Trigger (z. B. Mode/ID)
        climate_cfg = dp_config.get('climate')
        if climate_cfg and parsed.get('sub_item', '').lower().startswith(climate_cfg.get('trigger_sub', 'Mode/ID').lower()):
            climate_res = self._generate_climate_discovery(parsed, climate_cfg, test_mode)
            results.extend(climate_res)

        # Optionale water_heater-Entität (Multi-DID: Temp + Setpoint + Mode)
        wh_cfg = dp_config.get('water_heater')
        if wh_cfg and did == wh_cfg.get('trigger_did', did):
            wh_res = self._generate_water_heater_discovery(parsed, wh_cfg, test_mode)
            results.extend(wh_res)

        return results

    def _generate_typed_discovery(self, parsed: dict[str, Any], dp_config: dict[str, Any], value: str, test_mode: bool) -> list[tuple[str, str]]:
        """Generiert Discovery Messages basierend auf Datenpunkt-Typ"""
        type_name = dp_config.get('type')
        if not type_name:
            return []

        type_template = self.get_type_template(type_name)
        if not type_template:
            return []

        ecu_addr = parsed['ecu_addr']
        did = parsed['did']
        sub_item = parsed['sub_item']

        # Entity name from English canonical + translation + user override
        base_name = self.translate_name(dp_config.get('name', f'DID {did}'))
        base_name = self.resolve_name(did, None, base_name)

        results = []

        # Einfacher Sensor (ohne Sub-Items)
        if not sub_item or not dp_config.get('subs'):
            # trigger_sub: only publish discovery for the specified sub-item
            trigger_sub = dp_config.get('trigger_sub')
            if trigger_sub and sub_item and sub_item != trigger_sub:
                return results
            entity_type = type_template.get('entity_type', 'sensor')
            entity_id = self.generate_entity_id(ecu_addr, did)
            unique_id = self.generate_unique_id(ecu_addr, did)

            discovery_topic = self._build_discovery_topic(entity_type, entity_id, test_mode)
            config = self._build_entity_config(
                base_name, unique_id, entity_id, parsed['full_topic'],
                ecu_addr, type_template, dp_config, did, entity_type=entity_type
            )
            results.append((discovery_topic, json.dumps(config, ensure_ascii=False)))

        # Sensor mit Sub-Items
        else:
            subs_dict = dp_config.get('subs', {})
            if sub_item not in subs_dict:
                # Sub-Item not configured → skip silently
                return results
            sub_config = subs_dict[sub_item]
            if sub_config.get('enabled', True):  # Default: enabled
                # Sub-specific config: suffix for display name
                suffix_key = sub_config.get('suffix', sub_item)
                translated_suffix = self.translate_suffix(suffix_key)
                sub_name = f"{base_name} {translated_suffix}" if translated_suffix else base_name
                sub_name = self.resolve_name(did, sub_item, sub_name)

                entity_id = self.generate_entity_id(ecu_addr, did, sub_item)
                unique_id = self.generate_unique_id(ecu_addr, did, sub_item)

                # Bestimme Entity-Typ
                entity_type = sub_config.get('entity_type') or type_template.get('entity_type', 'sensor')

                # Merje Template-Konfiguration
                merged_template = self.merge_config(type_template, sub_config)

                discovery_topic = self._build_discovery_topic(entity_type, entity_id, test_mode)
                config = self._build_entity_config(
                    sub_name, unique_id, entity_id, parsed['full_topic'],
                    ecu_addr, merged_template, dp_config, did, entity_type=entity_type
                )
                results.append((discovery_topic, json.dumps(config, ensure_ascii=False)))

        return results

    def _generate_heuristic_discovery(self, parsed: dict[str, Any], test_mode: bool) -> list[tuple[str, str]]:
        """Tier 1: Generate discovery from heuristic inference for unknown DIDs."""
        ecu_addr = parsed['ecu_addr']
        did = parsed['did']
        sensor_name = parsed['sensor_name']
        sub_item = parsed.get('sub_item')

        hint = infer_entity_config(sensor_name, sub_item)
        entity_type = hint.entity_type

        entity_id = self.generate_entity_id(ecu_addr, did, sub_item)
        unique_id = self.generate_unique_id(ecu_addr, did, sub_item)

        # Name: "DID {did} {sensor_name}" (not translated, heuristic entity)
        name = f"DID {did} {sensor_name}"
        if sub_item:
            name = f"{name} {sub_item}"

        discovery_topic = self._build_discovery_topic(entity_type, entity_id, test_mode)

        config: dict[str, Any] = {
            "name": name,
            "unique_id": unique_id,
            "object_id": entity_id,
            "device": self.create_device_info(ecu_addr),
            "availability_topic": "open3e/LWT",
            "payload_available": "online",
            "payload_not_available": "offline",
        }

        if entity_type not in _STATELESS_ENTITY_TYPES:
            config["state_topic"] = parsed['full_topic']

        # Apply heuristic hints
        if hint.device_class:
            config["device_class"] = hint.device_class
        if hint.unit:
            config["unit_of_measurement"] = hint.unit
        if hint.state_class:
            config["state_class"] = hint.state_class
        if hint.icon:
            config["icon"] = hint.icon

        config["origin"] = {
            "name": "Open3E Bridge",
            "sw_version": _SW_VERSION,
            "support_url": "https://github.com/open3e/open3e-bridge",
        }

        self.auto_discovered_count += 1
        logger.info("Auto-discovered DID %d (%s) as %s", did, sensor_name, entity_type)

        return [(discovery_topic, json.dumps(config, ensure_ascii=False))]

    def _generate_climate_discovery(self, parsed: dict[str, Any], climate_cfg: dict[str, Any], test_mode: bool) -> list[tuple[str, str]]:
        ecu_addr = parsed['ecu_addr']
        did = parsed['did']
        sensor_name = parsed['sensor_name']

        # Resolve related DIDs and names for topics
        temp_did = climate_cfg.get('temperature_did')
        temp_did_name = climate_cfg.get('temperature_did_name', '')

        entity_id = self.generate_entity_id(ecu_addr, did, 'climate')
        unique_id = self.generate_unique_id(ecu_addr, did, 'climate')
        discovery_topic = self._build_discovery_topic('climate', entity_id, test_mode)

        name = self.translate_name(climate_cfg.get('name', 'Climate'))
        name = self.resolve_name(did, None, name)

        config: dict[str, Any] = {
            'name': name,
            'unique_id': unique_id,
            'object_id': entity_id,
            'device': self.create_device_info_for_did(ecu_addr, did),
            'availability_topic': 'open3e/LWT',
            'payload_available': 'online',
            'payload_not_available': 'offline',
        }

        # Origin information
        config['origin'] = {
            'name': 'Open3E Bridge',
            'sw_version': _SW_VERSION,
            'support_url': 'https://github.com/open3e/open3e-bridge',
        }

        # Mode topics/templates
        config['modes'] = climate_cfg.get('modes', ['off', 'auto'])
        config['mode_state_topic'] = f"open3e/{ecu_addr}_{did}_{sensor_name}/Mode/ID"
        config['mode_command_topic'] = 'open3e/cmnd'
        if 'mode_state_template' in climate_cfg:
            config['mode_state_template'] = climate_cfg['mode_state_template']
        if 'mode_command_template' in climate_cfg:
            config['mode_command_template'] = climate_cfg['mode_command_template']

        # Temperature topics/templates
        if temp_did and temp_did_name:
            config['temperature_state_topic'] = f"open3e/{ecu_addr}_{temp_did}_{temp_did_name}"
        config['temperature_command_topic'] = 'open3e/cmnd'
        if 'temperature_command_template' in climate_cfg:
            config['temperature_command_template'] = climate_cfg['temperature_command_template']

        # Ranges and units
        for key in ['min_temp', 'max_temp', 'precision', 'temperature_unit']:
            if key in climate_cfg:
                config[key] = climate_cfg[key]

        return [(discovery_topic, json.dumps(config, ensure_ascii=False))]

    def _generate_water_heater_discovery(self, parsed: dict[str, Any], wh_cfg: dict[str, Any], test_mode: bool) -> list[tuple[str, str]]:
        """Generate HA water_heater MQTT discovery for DHW (multi-DID pattern)."""
        ecu_addr = parsed['ecu_addr']
        did = parsed['did']

        entity_id = self.generate_entity_id(ecu_addr, did, 'water_heater')
        unique_id = self.generate_unique_id(ecu_addr, did, 'water_heater')
        discovery_topic = self._build_discovery_topic('water_heater', entity_id, test_mode)

        name = self.translate_name(wh_cfg.get('name', 'Hot Water'))
        name = self.resolve_name(did, None, name)

        config: dict[str, Any] = {
            'name': name,
            'unique_id': unique_id,
            'object_id': entity_id,
            'device': self.create_device_info_for_did(ecu_addr, did),
            'availability_topic': 'open3e/LWT',
            'payload_available': 'online',
            'payload_not_available': 'offline',
        }

        config['origin'] = {
            'name': 'Open3E Bridge',
            'sw_version': _SW_VERSION,
            'support_url': 'https://github.com/open3e/open3e-bridge',
        }

        # Current temperature (read-only sensor, e.g. DID 271)
        ct_did = wh_cfg.get('current_temperature_did')
        ct_name = wh_cfg.get('current_temperature_did_name', '')
        ct_sub = wh_cfg.get('current_temperature_sub', '')
        if ct_did and ct_name:
            topic_suffix = f"/{ct_sub}" if ct_sub else ""
            config['current_temperature_topic'] = f"open3e/{ecu_addr}_{ct_did}_{ct_name}{topic_suffix}"

        # Temperature setpoint (writable, e.g. DID 396)
        temp_did = wh_cfg.get('temperature_did')
        temp_did_name = wh_cfg.get('temperature_did_name', '')
        if temp_did and temp_did_name:
            config['temperature_state_topic'] = f"open3e/{ecu_addr}_{temp_did}_{temp_did_name}"
        config['temperature_command_topic'] = 'open3e/cmnd'
        if 'temperature_command_template' in wh_cfg:
            config['temperature_command_template'] = wh_cfg['temperature_command_template']

        # Mode (e.g. DID 531)
        config['modes'] = wh_cfg.get('modes', ['off', 'eco', 'performance'])
        sensor_name = parsed.get('sensor_name', '')
        config['mode_state_topic'] = f"open3e/{ecu_addr}_{did}_{sensor_name}"
        config['mode_command_topic'] = 'open3e/cmnd'
        if 'mode_state_template' in wh_cfg:
            config['mode_state_template'] = wh_cfg['mode_state_template']
        if 'mode_command_template' in wh_cfg:
            config['mode_command_template'] = wh_cfg['mode_command_template']

        # Temperature ranges
        for key in ['min_temp', 'max_temp', 'precision', 'temperature_unit']:
            if key in wh_cfg:
                config[key] = wh_cfg[key]

        return [(discovery_topic, json.dumps(config, ensure_ascii=False))]

    def _build_discovery_topic(self, entity_type: str, entity_id: str, test_mode: bool) -> str:
        """Baut Discovery Topic zusammen"""
        # Allow overriding via discovery_prefix; prepend test/ if test_mode is enabled
        prefix = self.discovery_prefix or "homeassistant"
        if self.add_test_prefix and test_mode and not prefix.startswith("test/"):
            prefix = f"test/{prefix}"
        return f"{prefix}/{entity_type}/{entity_id}/config"

    def _build_entity_config(self, name: str, unique_id: str, entity_id: str, state_topic: str,
                           ecu_addr: str, template: dict[str, Any], dp_config: dict[str, Any],
                           did: int, entity_type: str = "sensor") -> dict[str, Any]:
        """Baut Entity-Konfiguration zusammen"""
        config = {
            "name": name,
            "unique_id": unique_id,
            "object_id": entity_id,
            "device": self.create_device_info_for_did(ecu_addr, did),
            # Basic availability (expects open3e to publish LWT)
            "availability_topic": "open3e/LWT",
            "payload_available": "online",
            "payload_not_available": "offline",
        }

        # Stateless entity types (e.g. button) have no state_topic
        if entity_type not in _STATELESS_ENTITY_TYPES:
            config["state_topic"] = state_topic

        # Template-Eigenschaften übernehmen
        for key in _ENTITY_KEYS:
            if key in template:
                config[key] = template[key]

        # dp_config overrides (payloads, icons, custom value/command templates)
        for key in _ENTITY_KEYS:
            if key in dp_config:
                config[key] = dp_config[key]

        # Value template i18n overlay
        if 'value_template' in config:
            config['value_template'] = self.get_value_template(did, config['value_template'])

        # Origin information
        config["origin"] = {
            "name": "Open3E Bridge",
            "sw_version": _SW_VERSION,
            "support_url": "https://github.com/open3e/open3e-bridge",
        }

        # Schreibbare Entities (skip if write-blacklisted)
        if (dp_config.get('writable') or template.get('writable')) and not self.is_write_blacklisted(did):
            config["command_topic"] = "open3e/cmnd"

            # Min/Max/Step für Number-Entities
            for attr in ['min', 'max', 'step']:
                if attr in dp_config:
                    config[attr] = dp_config[attr]
                elif attr in template:
                    config[attr] = template[attr]

            # Command Template (auto-generated for number entities without explicit template)
            if template.get('entity_type') == 'number' and 'command_template' not in config:
                write_mode = dp_config.get('write_mode', 'write')
                config["command_template"] = f'{{"mode": "{write_mode}", "data": [[{did}, {{{{ value | float }}}}]]}}'

        return config

