"""Device registry — manages multiple E3 devices with per-device generators.

Each device has an ECU address and a profile. The registry routes incoming
MQTT messages to the correct generator based on the ECU address extracted
from the topic.

Single-device mode (backward compat): when no devices.yaml is provided,
the registry creates one device from CLI arguments.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .registry import get_generator_class

logger = logging.getLogger("open3e_bridge.generators.devices")


def normalize_ecu(ecu: str) -> str:
    """Normalize an ECU address to its canonical topic form.

    The Open3E reader formats addresses with ``{ecuAddr:03X}`` — uppercase hex,
    e.g. ``6CF``. Config files are written by hand and routinely use lowercase
    (``6cf``) or an ``0x`` prefix, which would silently miss the registry lookup
    and route messages to the fallback generator.
    """
    ecu = str(ecu).strip()
    if ecu.lower().startswith("0x"):
        ecu = ecu[2:]
    return ecu.upper()


@dataclass
class DeviceConfig:
    """Configuration for a single E3 device."""
    name: str
    ecu: str  # canonical uppercase hex string, e.g. "680" / "6CF"
    profile: str = "auto"
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.ecu = normalize_ecu(self.ecu)


class DeviceRegistry:
    """Manages multiple E3 devices, each with its own generator instance."""

    def __init__(
        self,
        devices: list[DeviceConfig],
        generator_type: str = "homeassistant",
        config_dir: str = "config",
        language: str = "en",
        discovery_prefix: str = "homeassistant",
        add_test_prefix: bool = True,
        auto_discover: bool = True,
    ):
        self._devices = {d.ecu: d for d in devices}
        self._generators: dict[str, Any] = {}  # ecu → generator instance

        generator_cls = get_generator_class(generator_type)

        for dev in devices:
            gen = generator_cls(
                config_dir,
                language,
                discovery_prefix=discovery_prefix,
                add_test_prefix=add_test_prefix,
                auto_discover=auto_discover,
                profile=dev.profile,
            )
            self._generators[dev.ecu] = gen
            logger.info(
                "Registered device '%s' (ECU %s, profile=%s)",
                dev.name, dev.ecu, dev.profile,
            )

    @property
    def devices(self) -> dict[str, DeviceConfig]:
        """Map of ecu_addr → DeviceConfig."""
        return dict(self._devices)

    @property
    def generators(self) -> dict[str, Any]:
        """Map of ecu_addr → generator instance."""
        return dict(self._generators)

    def get_generator(self, ecu_addr: str) -> Any | None:
        """Get the generator for a specific ECU address (case-insensitive)."""
        return self._generators.get(normalize_ecu(ecu_addr))

    def get_default_generator(self) -> Any:
        """Return the first (or only) generator. Used for single-device compat."""
        return next(iter(self._generators.values()))

    @property
    def ecu_addresses(self) -> list[str]:
        """List of registered ECU addresses."""
        return list(self._devices.keys())

    @classmethod
    def from_single_device(
        cls,
        generator_type: str = "homeassistant",
        config_dir: str = "config",
        language: str = "en",
        discovery_prefix: str = "homeassistant",
        add_test_prefix: bool = True,
        auto_discover: bool = True,
        profile: str = "auto",
        ecu_addr: str = "680",
    ) -> DeviceRegistry:
        """Create a single-device registry (backward compatible mode)."""
        device = DeviceConfig(name="default", ecu=ecu_addr, profile=profile)
        return cls(
            devices=[device],
            generator_type=generator_type,
            config_dir=config_dir,
            language=language,
            discovery_prefix=discovery_prefix,
            add_test_prefix=add_test_prefix,
            auto_discover=auto_discover,
        )

    @classmethod
    def from_yaml(
        cls,
        devices_path: str | Path,
        generator_type: str = "homeassistant",
        config_dir: str = "config",
        language: str = "en",
        discovery_prefix: str = "homeassistant",
        add_test_prefix: bool = True,
        auto_discover: bool = True,
    ) -> DeviceRegistry:
        """Load device definitions from a YAML file.

        Expected format:
            devices:
              - name: vitocal
                ecu: "680"
                profile: vitocal
              - name: vitodens
                ecu: "690"
                profile: vitodens
        """
        path = Path(devices_path)
        try:
            with open(path, encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Devices config not found: {path}") from None

        raw_devices = raw.get("devices")
        if not raw_devices or not isinstance(raw_devices, list):
            raise ValueError(
                f"Invalid devices config: 'devices' must be a non-empty list in {path}"
            )

        devices: list[DeviceConfig] = []
        seen_ecus: set[str] = set()
        seen_names: set[str] = set()

        for i, entry in enumerate(raw_devices):
            if not isinstance(entry, dict):
                raise ValueError(f"Device entry {i} must be a mapping, got {type(entry).__name__}")

            name = entry.get("name")
            ecu = str(entry.get("ecu", ""))
            profile = entry.get("profile", "auto")

            if not name:
                raise ValueError(f"Device entry {i}: 'name' is required")
            if not ecu:
                raise ValueError(f"Device '{name}': 'ecu' is required")

            # Normalize ECU to the canonical topic form (uppercase, no 0x)
            ecu = normalize_ecu(ecu)

            if ecu in seen_ecus:
                raise ValueError(f"Duplicate ECU address '{ecu}' in devices config")
            if name in seen_names:
                raise ValueError(f"Duplicate device name '{name}' in devices config")

            seen_ecus.add(ecu)
            seen_names.add(name)

            extra = {k: v for k, v in entry.items() if k not in ("name", "ecu", "profile")}
            devices.append(DeviceConfig(name=name, ecu=ecu, profile=profile, extra=extra))

        logger.info("Loaded %d devices from %s", len(devices), path)

        return cls(
            devices=devices,
            generator_type=generator_type,
            config_dir=config_dir,
            language=language,
            discovery_prefix=discovery_prefix,
            add_test_prefix=add_test_prefix,
            auto_discover=auto_discover,
        )
