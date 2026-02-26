"""Shared test fixtures for open3e-bridge."""
import pytest
from pathlib import Path

from generators.homeassistant import HomeAssistantGenerator


CONFIG_DIR = str(Path(__file__).resolve().parents[1] / "config")


@pytest.fixture
def generator_de():
    """German HomeAssistantGenerator with test prefix disabled."""
    return HomeAssistantGenerator(
        config_dir=CONFIG_DIR,
        language="de",
        discovery_prefix="homeassistant",
        add_test_prefix=False,
    )


@pytest.fixture
def generator_en():
    """English HomeAssistantGenerator with test prefix disabled."""
    return HomeAssistantGenerator(
        config_dir=CONFIG_DIR,
        language="en",
        discovery_prefix="homeassistant",
        add_test_prefix=False,
    )


@pytest.fixture
def config_dir():
    """Path to config directory."""
    return CONFIG_DIR
