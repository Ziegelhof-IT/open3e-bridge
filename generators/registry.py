"""Generator registry — plugin system for discovery generators.

Register custom generators by adding them to _REGISTRY.
Use --generator <name> on the CLI to select a generator at runtime.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("open3e_bridge.generators.registry")

# Lazy registry: maps name → (module_path, class_name, description)
_REGISTRY: dict[str, tuple[str, str, str]] = {
    "homeassistant": (
        "generators.homeassistant",
        "HomeAssistantGenerator",
        "Home Assistant MQTT Discovery (default)",
    ),
}


def register_generator(name: str, module_path: str, class_name: str, description: str = "") -> None:
    """Register a custom generator type."""
    _REGISTRY[name] = (module_path, class_name, description)


def get_generator_class(name: str) -> type[Any]:
    """Get generator class by registry name. Raises ValueError for unknown names."""
    entry = _REGISTRY.get(name)
    if entry is None:
        available = ", ".join(sorted(_REGISTRY.keys()))
        raise ValueError(
            f"Unknown generator type '{name}'. Available: {available}"
        )
    module_path, class_name, _desc = entry
    import importlib
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls


def list_generators() -> list[tuple[str, str]]:
    """Return list of (name, description) for all registered generators."""
    return [(name, entry[2]) for name, entry in sorted(_REGISTRY.items())]
