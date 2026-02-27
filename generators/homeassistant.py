"""
Home Assistant MQTT Discovery Generator
"""
import json
import logging
from typing import Any, Dict, List, Tuple

from .base import BaseGenerator

logger = logging.getLogger("open3e_bridge.generators.ha")

# Keys merged from type templates and dp_config overrides into entity config
_ENTITY_KEYS = (
    'device_class', 'unit_of_measurement', 'icon', 'state_class',
    'mode', 'payload_on', 'payload_off', 'state_on', 'state_off',
    'value_template', 'command_template', 'options',
)


class HomeAssistantGenerator(BaseGenerator):
    def __init__(self, config_dir: str = "config", language: str = "de", discovery_prefix: str = "homeassistant", add_test_prefix: bool = True):
        super().__init__(config_dir=config_dir, language=language)
        self.discovery_prefix = discovery_prefix
        self.add_test_prefix = add_test_prefix

    def generate_discovery_message(self, topic: str, value: str, test_mode: bool = True) -> List[Tuple[str, str]]:
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
            # KEINE Fallback Discovery für unbekannte DIDs
            logger.debug("Skipping unknown DID %d (not configured)", did)
            return []

        # Generiere Discovery Messages basierend auf Typ
        results = self._generate_typed_discovery(parsed, dp_config, value, test_mode)

        # Optionale Climate-Entität, wenn im Datapoint konfiguriert und passender Trigger (z. B. Mode/ID)
        climate_cfg = dp_config.get('climate')
        if climate_cfg and parsed.get('sub_item', '').lower().startswith(climate_cfg.get('trigger_sub', 'Mode/ID').lower()):
            climate_res = self._generate_climate_discovery(parsed, climate_cfg, test_mode)
            results.extend(climate_res)

        return results

    def _generate_typed_discovery(self, parsed: Dict[str, Any], dp_config: Dict[str, Any], value: str, test_mode: bool) -> List[Tuple[str, str]]:
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

        # Basis-Name aus Übersetzung
        name_key = dp_config.get('name_key', f'did_{did}')
        base_name = self.translate(name_key)

        results = []

        # Einfacher Sensor (ohne Sub-Items)
        if not sub_item or not dp_config.get('subs'):
            entity_type = type_template.get('entity_type', 'sensor')
            entity_id = self.generate_entity_id(ecu_addr, did)
            unique_id = self.generate_unique_id(ecu_addr, did)

            discovery_topic = self._build_discovery_topic(entity_type, entity_id, test_mode)
            config = self._build_entity_config(
                base_name, unique_id, entity_id, parsed['full_topic'],
                ecu_addr, type_template, dp_config, did
            )
            results.append((discovery_topic, json.dumps(config, ensure_ascii=False)))

        # Sensor mit Sub-Items
        else:
            sub_config = dp_config.get('subs', {}).get(sub_item, {})
            if sub_config.get('enabled', True):  # Default: enabled
                # Sub-spezifische Konfiguration
                sub_type = sub_config.get('type', sub_item)
                sub_name = f"{base_name} {self.translate(sub_type)}"

                entity_id = self.generate_entity_id(ecu_addr, did, sub_item)
                unique_id = self.generate_unique_id(ecu_addr, did, sub_item)

                # Bestimme Entity-Typ
                entity_type = sub_config.get('entity_type') or type_template.get('entity_type', 'sensor')

                # Merje Template-Konfiguration
                merged_template = self.merge_config(type_template, sub_config)

                discovery_topic = self._build_discovery_topic(entity_type, entity_id, test_mode)
                config = self._build_entity_config(
                    sub_name, unique_id, entity_id, parsed['full_topic'],
                    ecu_addr, merged_template, dp_config, did
                )
                results.append((discovery_topic, json.dumps(config, ensure_ascii=False)))

        return results

    def _generate_climate_discovery(self, parsed: Dict[str, Any], climate_cfg: Dict[str, Any], test_mode: bool) -> List[Tuple[str, str]]:
        ecu_addr = parsed['ecu_addr']
        did = parsed['did']
        sensor_name = parsed['sensor_name']

        # Resolve related DIDs and names for topics
        temp_did = climate_cfg.get('temperature_did')
        temp_did_name = climate_cfg.get('temperature_did_name', '')

        entity_id = self.generate_entity_id(ecu_addr, did, 'climate')
        unique_id = self.generate_unique_id(ecu_addr, did, 'climate')
        discovery_topic = self._build_discovery_topic('climate', entity_id, test_mode)

        name = climate_cfg.get('name') or self.translate(climate_cfg.get('name_key', 'climate'))

        config: Dict[str, Any] = {
            'name': name,
            'unique_id': unique_id,
            'default_entity_id': entity_id,
            'device': self.create_device_info(ecu_addr),
            'availability_topic': 'open3e/LWT',
            'payload_available': 'online',
            'payload_not_available': 'offline',
        }

        # Origin information
        config['origin'] = {
            'name': 'Open3E Bridge',
            'sw_version': '0.1.0',
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

    def _build_discovery_topic(self, entity_type: str, entity_id: str, test_mode: bool) -> str:
        """Baut Discovery Topic zusammen"""
        # Allow overriding via discovery_prefix; prepend test/ if test_mode is enabled
        prefix = self.discovery_prefix or "homeassistant"
        if self.add_test_prefix and test_mode and not prefix.startswith("test/"):
            prefix = f"test/{prefix}"
        return f"{prefix}/{entity_type}/{entity_id}/config"

    def _build_entity_config(self, name: str, unique_id: str, entity_id: str, state_topic: str,
                           ecu_addr: str, template: Dict[str, Any], dp_config: Dict[str, Any], did: int) -> Dict[str, Any]:
        """Baut Entity-Konfiguration zusammen"""
        config = {
            "name": name,
            "unique_id": unique_id,
            "default_entity_id": entity_id,
            "state_topic": state_topic,
            "device": self.create_device_info(ecu_addr),
            # Basic availability (expects open3e to publish LWT)
            "availability_topic": "open3e/LWT",
            "payload_available": "online",
            "payload_not_available": "offline",
        }

        # Template-Eigenschaften übernehmen
        for key in _ENTITY_KEYS:
            if key in template:
                config[key] = template[key]

        # dp_config-Overrides (z.B. payloads, icons, custom value/command templates)
        for key in _ENTITY_KEYS:
            if key in dp_config:
                config[key] = dp_config[key]

        # Origin information
        config["origin"] = {
            "name": "Open3E Bridge",
            "sw_version": "0.1.0",
            "support_url": "https://github.com/open3e/open3e-bridge",
        }

        # Schreibbare Entities
        if dp_config.get('writable') or template.get('writable'):
            config["command_topic"] = "open3e/cmnd"

            # Min/Max/Step für Number-Entities
            for attr in ['min', 'max', 'step']:
                if attr in dp_config:
                    config[attr] = dp_config[attr]
                elif attr in template:
                    config[attr] = template[attr]

            # Command Template (vereinfacht für Test)
            if template.get('entity_type') == 'number' and 'command_template' not in config:
                write_mode = dp_config.get('write_mode', 'write')
                config["command_template"] = f'{{"mode": "{write_mode}", "data": [[{did}, "{{{{ value }}}}"]]}}'

        return config

