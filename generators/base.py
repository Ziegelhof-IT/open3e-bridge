"""
Basis-Generator für MQTT Discovery Messages
"""
import logging
import yaml
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import re

logger = logging.getLogger("open3e_bridge.generators")

class BaseGenerator:
    def __init__(self, config_dir: str = "config", language: str = "de"):
        self.config_dir = Path(config_dir)
        self.language = language
        
        # Lade Konfigurationsdateien
        self.datapoints = self._load_yaml(self.config_dir / "datapoints.yaml")
        self.translations = self._load_yaml(self.config_dir / "translations" / f"{language}.yaml")
        self.type_templates = self._load_yaml(self.config_dir / "templates" / "types.yaml")
        
        # Device-Informationen Cache
        self.device_cache = {}

    def validate(self) -> Dict[str, Any]:
        """Validates datapoints and templates. Returns dict with errors/warnings."""
        errors: List[str] = []
        warnings: List[str] = []

        # Check type templates present
        available_types = set(k for k in self.type_templates.keys() if k != 'sub_type_templates')

        dps = self.datapoints.get('datapoints', {}) or {}
        for key, cfg in dps.items():
            # Key type
            try:
                int(key)
            except Exception:
                errors.append(f"Datapoint key '{key}' is not an integer")
                continue

            # Type presence
            tp = cfg.get('type')
            if not tp:
                errors.append(f"DID {key}: missing 'type'")
            elif tp not in available_types and tp not in {'device_info'}:
                errors.append(f"DID {key}: unknown type '{tp}'")

            # Numeric constraints
            for num_key in ['min', 'max', 'step']:
                if num_key in cfg and not isinstance(cfg[num_key], (int, float)):
                    errors.append(f"DID {key}: '{num_key}' must be number")

            # name_key against translations
            name_key = cfg.get('name_key')
            if name_key and name_key not in self.translations:
                warnings.append(f"DID {key}: name_key '{name_key}' missing in {self.language} translations")

            # Options type
            if 'options' in cfg and not isinstance(cfg['options'], list):
                errors.append(f"DID {key}: 'options' must be a list")

            # Subs validation (lightweight)
            subs = cfg.get('subs', {}) or {}
            if subs and not isinstance(subs, dict):
                errors.append(f"DID {key}: 'subs' must be a mapping")
            for subname, scfg in subs.items():
                if not isinstance(scfg, dict):
                    errors.append(f"DID {key} sub '{subname}': must be a mapping")
                for num_key in ['min', 'max', 'step']:
                    if num_key in scfg and not isinstance(scfg[num_key], (int, float)):
                        errors.append(f"DID {key} sub '{subname}': '{num_key}' must be number")
                if 'options' in scfg and not isinstance(scfg['options'], list):
                    errors.append(f"DID {key} sub '{subname}': 'options' must be a list")

        # ROB-04: Jinja2 template syntax validation
        self._validate_jinja_templates(dps, errors)

        return {"errors": errors, "warnings": warnings}

    @staticmethod
    def _validate_jinja_templates(dps: Dict, errors: List[str]):
        """Validate Jinja2 syntax in all templates found in datapoints config."""
        try:
            from jinja2 import Environment, TemplateSyntaxError
        except ImportError:
            return  # jinja2 is a dev dependency, skip if not installed

        env = Environment()
        template_keys = ('value_template', 'command_template',
                         'mode_state_template', 'mode_command_template',
                         'temperature_command_template')

        def _check(did_key: str, context: str, value: str):
            try:
                env.parse(value)
            except TemplateSyntaxError as e:
                errors.append(f"DID {did_key} {context}: Jinja2 syntax error: {e}")

        for key, cfg in dps.items():
            for tk in template_keys:
                if tk in cfg and isinstance(cfg[tk], str):
                    _check(key, tk, cfg[tk])
            for subname, scfg in (cfg.get('subs') or {}).items():
                if not isinstance(scfg, dict):
                    continue
                for tk in template_keys:
                    if tk in scfg and isinstance(scfg[tk], str):
                        _check(key, f"sub '{subname}' {tk}", scfg[tk])
            climate = cfg.get('climate')
            if isinstance(climate, dict):
                for tk in template_keys:
                    if tk in climate and isinstance(climate[tk], str):
                        _check(key, f"climate {tk}", climate[tk])

    def _load_yaml(self, filepath: Path) -> Dict[str, Any]:
        """Lädt YAML-Datei"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning("Config file not found: %s", filepath)
            return {}
    
    def translate(self, key: str) -> str:
        """Übersetzt einen Schlüssel"""
        return self.translations.get(key, key)
    
    def get_datapoint_config(self, did: int) -> Optional[Dict[str, Any]]:
        """Holt Konfiguration für einen Datenpunkt"""
        return self.datapoints.get("datapoints", {}).get(did)
    
    def get_type_template(self, type_name: str) -> Dict[str, Any]:
        """Holt Template für einen Typ"""
        return self.type_templates.get(type_name, {})
    
    def is_ignored_did(self, did: int) -> bool:
        """Prüft ob DID ignoriert werden soll"""
        return did in self.datapoints.get("ignored_dids", [])
    
    def parse_open3e_topic(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Parst Open3E MQTT Topic
        Format: open3e/680_268_FlowTemperatureSensor/Actual
        """
        try:
            parts = topic.split('/')
            if len(parts) < 2 or parts[0] != 'open3e':
                return None
                
            # Parse Hauptteil: 680_268_FlowTemperatureSensor
            main_part = parts[1]
            if '_' not in main_part:
                return None
                
            # Split bei ersten beiden Underscores
            parts_main = main_part.split('_', 2)
            if len(parts_main) < 3:
                return None
                
            ecu_addr = parts_main[0]
            did = int(parts_main[1])
            sensor_name = parts_main[2]
            
            # Sub-Item (falls vorhanden). Unterstützt auch tiefere Pfade (z.B. "Mode/ID").
            sub_item = "/".join(parts[2:]) if len(parts) > 2 else None
            
            return {
                'ecu_addr': ecu_addr,
                'did': did,
                'sensor_name': sensor_name,
                'sub_item': sub_item,
                'full_topic': topic
            }
        except (ValueError, IndexError):
            return None
    
    def generate_entity_id(self, ecu_addr: str, did: int, sub_item: str = None) -> str:
        """Generiert Entity ID"""
        base_id = f"open3e_{ecu_addr}_{did}"
        if sub_item and sub_item.lower() != 'unknown':
            # Sanitize sub_item for use in MQTT topic/entity_id (no slashes/spaces)
            cleaned = re.sub(r"[^a-z0-9_]+", "_", sub_item.lower())
            cleaned = cleaned.replace("/", "_")
            base_id += f"_{cleaned}"
        return base_id
    
    def generate_unique_id(self, ecu_addr: str, did: int, sub_item: str = None) -> str:
        """Generiert Unique ID für Home Assistant"""
        return self.generate_entity_id(ecu_addr, did, sub_item)
    
    def update_device_info(self, ecu_addr: str, did: int, value: str):
        """Aktualisiert Device-Informationen basierend auf MQTT-Nachrichten"""
        device_id_dids = self.datapoints.get("device_identification_dids", {})
        
        # Prüfe ob dieser DID Device-Info enthält
        if did in device_id_dids:
            logger.debug("Found device info in DID %d: %s", did, value)
            
            # Extrahiere Geräte-Info aus dem Wert
            device_info = self._extract_device_info(value)

            # ggf. Seriennummer aus bestimmten DIDs übernehmen (z. B. IdentNumber 377)
            try:
                if int(did) == 377 or device_id_dids.get(did, {}).get('extract_serial'):
                    device_info['serial'] = str(value).strip()
            except Exception:
                pass
            
            # Cache für diesen ECU
            if ecu_addr not in self.device_cache:
                self.device_cache[ecu_addr] = {}
            
            self.device_cache[ecu_addr].update(device_info)
    
    def _extract_device_info(self, value: str) -> Dict[str, str]:
        """Extrahiert Geräte-Informationen aus einem Wert"""
        device_patterns = self.datapoints.get("device_patterns", [])
        
        # Versuche Pattern zu matchen
        for pattern_config in device_patterns:
            pattern = pattern_config.get("pattern", "")
            if re.search(pattern, value, re.IGNORECASE):
                return {
                    "name": pattern_config.get("name", value),
                    "model": pattern_config.get("model", pattern)
                }
        
        # Fallback: Verwende den Wert direkt (bereinigt)
        clean_value = re.sub(r'[^a-zA-Z0-9\-\s]', '', value).strip()
        return {
            "name": clean_value or "Open3E System",
            "model": clean_value or "E3 Controller"
        }
    
    def create_device_info(self, ecu_addr: str, device_name: str = None) -> Dict[str, Any]:
        """Erstellt Device-Informationen"""
        # Verwende gecachte Device-Info falls verfügbar
        cached_info = self.device_cache.get(ecu_addr, {})
        
        if not device_name:
            device_name = cached_info.get("name")
            
        if not device_name:
            # Fallback aus Konfiguration
            default_device = self.datapoints.get("default_device", {})
            device_name = default_device.get("name", "Open3E System")
            model = default_device.get("model", "E3 Controller")
        else:
            model = cached_info.get("model", device_name)
        
        identifiers = [f"open3e_{ecu_addr}"]
        serial = cached_info.get('serial')
        if serial:
            identifiers.insert(0, f"open3e_{serial}")

        info = {
            "identifiers": identifiers,
            "name": device_name,
            "manufacturer": "Viessmann",
            "model": model,
            "suggested_area": self.translate("suggested_area")
        }

        # Optional: SW-Version falls vorhanden
        if cached_info.get('sw_version'):
            info['sw_version'] = cached_info['sw_version']

        return info
    
    def merge_config(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merged Konfigurationen zusammen"""
        result = base_config.copy()
        for key, value in override_config.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self.merge_config(result[key], value)
            else:
                result[key] = value
        return result
