"""
Base generator for MQTT Discovery Messages
"""
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger("open3e_bridge.generators")

# English suffix map (canonical, no file needed)
_EN_SUFFIXES = {
    "current": "Current", "min": "Minimum", "max": "Maximum",
    "avg": "Average", "unknown": "Unknown", "error": "Error",
}


class BaseGenerator:
    def __init__(self, config_dir: str = "config", language: str = "en"):
        self.config_dir = Path(config_dir)
        self.language = language

        # Load config files
        self.datapoints = self._load_yaml(self.config_dir / "datapoints.yaml")
        self.type_templates = self._load_yaml(self.config_dir / "templates" / "types.yaml")

        # Load translations only for non-English languages
        if language != "en":
            self.translations = self._load_yaml(
                self.config_dir / "translations" / f"{language}.yaml"
            )
        else:
            self.translations = {}

        # Device info cache
        self.device_cache = {}

    # ------------------------------------------------------------------
    # Translation methods
    # ------------------------------------------------------------------

    def translate_name(self, english_name: str) -> str:
        """Translate entity name. EN: passthrough, other: overlay with EN fallback."""
        if self.language == "en":
            return english_name
        return self.translations.get("names", {}).get(english_name, english_name)

    def translate_suffix(self, suffix_key: str) -> str:
        """Translate sub-item suffix. EN: known map, other: overlay with fallback."""
        if self.language == "en":
            return _EN_SUFFIXES.get(suffix_key, suffix_key)
        return self.translations.get("suffixes", {}).get(
            suffix_key, _EN_SUFFIXES.get(suffix_key, suffix_key))

    def translate_string(self, key: str, fallback: str = None) -> str:
        """Translate misc strings (suggested_area). EN: fallback, other: overlay."""
        if self.language == "en":
            return fallback or key
        return self.translations.get("strings", {}).get(key, fallback or key)

    def get_value_template(self, did: int, default_template: str) -> str:
        """Get value_template: overlay has priority, else English default from datapoints."""
        vt = self.translations.get("value_templates", {})
        overlay = vt.get(did) or vt.get(str(did))
        if overlay:
            return overlay
        return default_template

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> Dict[str, Any]:
        """Validates datapoints and templates. Returns dict with errors/warnings."""
        errors: List[str] = []
        warnings: List[str] = []

        # Validate write_blacklisted_dids
        wbl = self.datapoints.get('write_blacklisted_dids')
        if wbl is not None:
            if not isinstance(wbl, list):
                errors.append("write_blacklisted_dids must be a list")
            else:
                for item in wbl:
                    if not isinstance(item, int):
                        errors.append(f"write_blacklisted_dids: '{item}' is not an integer")

        # Check type templates present
        available_types = set(self.type_templates.keys())

        dps = self.datapoints.get('datapoints', {}) or {}
        for key, cfg in dps.items():
            # Key type
            try:
                int(key)
            except (ValueError, TypeError):
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

            # name field (required, non-empty string)
            name = cfg.get('name')
            if not name and tp != 'device_info':
                warnings.append(f"DID {key}: missing 'name' field")
            elif name and self.language != "en":
                names_dict = self.translations.get("names", {})
                if name not in names_dict:
                    warnings.append(
                        f"DID {key}: name '{name}' missing in {self.language} translations"
                    )

            # Options type
            if 'options' in cfg and not isinstance(cfg['options'], list):
                errors.append(f"DID {key}: 'options' must be a list")

            # Subs validation (lightweight)
            subs = cfg.get('subs', {}) or {}
            if subs and not isinstance(subs, dict):
                errors.append(f"DID {key}: 'subs' must be a mapping")
                subs = {}
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
            subs_raw = cfg.get('subs') or {}
            if not isinstance(subs_raw, dict):
                continue
            for subname, scfg in subs_raw.items():
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
        """Load YAML file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning("Config file not found: %s", filepath)
            return {}

    def get_datapoint_config(self, did: int) -> Optional[Dict[str, Any]]:
        """Get config for a datapoint"""
        return self.datapoints.get("datapoints", {}).get(did)

    def get_type_template(self, type_name: str) -> Dict[str, Any]:
        """Get template for a type"""
        return self.type_templates.get(type_name, {})

    def is_ignored_did(self, did: int) -> bool:
        """Check if DID should be ignored"""
        return did in self.datapoints.get("ignored_dids", [])

    def is_write_blacklisted(self, did: int) -> bool:
        """Check if DID is write-blacklisted (read allowed, write blocked)."""
        return did in self.datapoints.get("write_blacklisted_dids", [])

    def parse_open3e_topic(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Parse Open3E MQTT Topic
        Format: open3e/680_268_FlowTemperatureSensor/Actual
        """
        try:
            parts = topic.split('/')
            if len(parts) < 2 or parts[0] != 'open3e':
                return None

            # Parse main part: 680_268_FlowTemperatureSensor
            main_part = parts[1]
            if '_' not in main_part:
                return None

            # Split at first two underscores
            parts_main = main_part.split('_', 2)
            if len(parts_main) < 3:
                return None

            ecu_addr = parts_main[0]
            did = int(parts_main[1])
            sensor_name = parts_main[2]

            # Sub-Item (if present). Supports deep paths (e.g. "Mode/ID").
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
        """Generate Entity ID"""
        base_id = f"open3e_{ecu_addr}_{did}"
        if sub_item and sub_item.lower() != 'unknown':
            # Sanitize sub_item for use in MQTT topic/entity_id (no slashes/spaces)
            cleaned = re.sub(r"[^a-z0-9_]+", "_", sub_item.lower())
            base_id += f"_{cleaned}"
        return base_id

    def generate_unique_id(self, ecu_addr: str, did: int, sub_item: str = None) -> str:
        """Generate Unique ID for Home Assistant"""
        return self.generate_entity_id(ecu_addr, did, sub_item)

    def update_device_info(self, ecu_addr: str, did: int, value: str):
        """Update device info based on MQTT messages"""
        device_id_dids = self.datapoints.get("device_identification_dids", {})

        # Check if this DID contains device info
        if did in device_id_dids:
            logger.debug("Found device info in DID %d: %s", did, value)

            # Extract device info from value
            device_info = self._extract_device_info(value)

            # Extract serial from specific DIDs (e.g. IdentNumber 377)
            try:
                if int(did) == 377 or device_id_dids.get(did, {}).get('extract_serial'):
                    device_info['serial'] = str(value).strip()
            except Exception:
                pass

            # Cache for this ECU
            if ecu_addr not in self.device_cache:
                self.device_cache[ecu_addr] = {}

            self.device_cache[ecu_addr].update(device_info)

    def _extract_device_info(self, value: str) -> Dict[str, str]:
        """Extract device info from a value"""
        device_patterns = self.datapoints.get("device_patterns", [])

        # Try to match patterns
        for pattern_config in device_patterns:
            pattern = pattern_config.get("pattern", "")
            if re.search(pattern, value, re.IGNORECASE):
                return {
                    "name": pattern_config.get("name", value),
                    "model": pattern_config.get("model", pattern)
                }

        # Fallback: use value directly (cleaned)
        clean_value = re.sub(r'[^a-zA-Z0-9\-\s]', '', value).strip()
        return {
            "name": clean_value or "Open3E System",
            "model": clean_value or "E3 Controller"
        }

    def create_device_info(self, ecu_addr: str, device_name: str = None) -> Dict[str, Any]:
        """Create device info"""
        # Use cached device info if available
        cached_info = self.device_cache.get(ecu_addr, {})

        if not device_name:
            device_name = cached_info.get("name")

        if not device_name:
            # Fallback from config
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
            "suggested_area": self.translate_string("suggested_area", "Heating")
        }

        # Optional: SW version if available
        if cached_info.get('sw_version'):
            info['sw_version'] = cached_info['sw_version']

        return info

    def merge_config(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge configs together"""
        result = base_config.copy()
        for key, value in override_config.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self.merge_config(result[key], value)
            else:
                result[key] = value
        return result
