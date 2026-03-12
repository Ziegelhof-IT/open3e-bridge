"""Tests for the generator registry (plugin system)."""
import pytest


def test_get_homeassistant_generator():
    """Default 'homeassistant' generator resolves correctly."""
    from generators.homeassistant import HomeAssistantGenerator
    from generators.registry import get_generator_class
    cls = get_generator_class("homeassistant")
    assert cls is HomeAssistantGenerator


def test_unknown_generator_raises():
    """Unknown generator type raises ValueError with available list."""
    from generators.registry import get_generator_class
    with pytest.raises(ValueError, match="Unknown generator type 'nonexistent'"):
        get_generator_class("nonexistent")


def test_list_generators():
    """list_generators returns at least the default entry."""
    from generators.registry import list_generators
    result = list_generators()
    names = [name for name, _ in result]
    assert "homeassistant" in names


def test_register_custom_generator():
    """Custom generators can be registered and resolved."""
    from generators.registry import _REGISTRY, get_generator_class, register_generator

    # Register a mock generator (use existing class as stand-in)
    register_generator(
        "test_custom",
        "generators.homeassistant",
        "HomeAssistantGenerator",
        "Test custom generator",
    )
    try:
        cls = get_generator_class("test_custom")
        from generators.homeassistant import HomeAssistantGenerator
        assert cls is HomeAssistantGenerator
    finally:
        # Clean up registry
        _REGISTRY.pop("test_custom", None)


def test_bridge_accepts_generator_type():
    """Bridge constructor accepts generator_type parameter."""
    from unittest.mock import MagicMock, patch
    with patch("bridge.mqtt.Client") as MockClient:
        MockClient.return_value = MagicMock()
        from bridge import Open3EBridge
        b = Open3EBridge(test_mode=True, add_test_prefix=False, generator_type="homeassistant")
        assert b.generator is not None


def test_bridge_rejects_unknown_generator():
    """Bridge raises ValueError for unknown generator type."""
    from unittest.mock import MagicMock, patch
    with patch("bridge.mqtt.Client") as MockClient:
        MockClient.return_value = MagicMock()
        from bridge import Open3EBridge
        with pytest.raises(ValueError, match="Unknown generator type"):
            Open3EBridge(test_mode=True, generator_type="nonexistent")


def test_list_generators_cli(tmp_path):
    """--list-generators flag works from CLI."""
    from unittest.mock import patch
    with patch("sys.argv", ["bridge", "--list-generators"]):
        from bridge import main
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
