"""Tests for user name overrides (config/user/names.yaml)."""
import json
from pathlib import Path

import pytest
import yaml

from generators.homeassistant import HomeAssistantGenerator

CONFIG_DIR = str(Path(__file__).resolve().parents[1] / "config")
USER_DIR = Path(CONFIG_DIR) / "user"

# A DID known to have subs (268 = FlowTemperatureSensor with Actual/Minimum/Maximum)
SUB_DID = 268
SUB_TOPIC = "open3e/680_268_FlowTemperatureSensor/Actual"
SUB_VALUE = "47.5"

# A simple DID (396 = DHWSetpointAdjust, single value)
SIMPLE_DID = 396
SIMPLE_TOPIC = "open3e/680_396_DHWSetpointAdjust"
SIMPLE_VALUE = "50"


def _write_user_names(names: dict):
    """Write a names.yaml into config/user/."""
    USER_DIR.mkdir(parents=True, exist_ok=True)
    with open(USER_DIR / "names.yaml", "w") as f:
        yaml.dump({"names": names}, f)


def _cleanup():
    names_file = USER_DIR / "names.yaml"
    if names_file.exists():
        names_file.unlink()


@pytest.fixture(autouse=True)
def clean_user_names():
    """Ensure no leftover names.yaml before/after each test."""
    _cleanup()
    yield
    _cleanup()


def _make_gen(**kwargs):
    return HomeAssistantGenerator(
        config_dir=CONFIG_DIR,
        discovery_prefix="homeassistant",
        add_test_prefix=False,
        **kwargs,
    )


def _get_name(gen, topic, value):
    """Generate discovery and return the entity name from payload."""
    results = gen.generate_discovery_message(topic, value, test_mode=False)
    assert results, f"No discovery generated for {topic}"
    payload = json.loads(results[0][1])
    return payload["name"]


class TestUserNameOverrides:
    def test_no_override_file(self):
        """Without names.yaml, normal translation applies."""
        gen = _make_gen(language="en")
        assert gen.user_names == {}
        name = _get_name(gen, SIMPLE_TOPIC, SIMPLE_VALUE)
        # Should be the English canonical name, not overridden
        assert name  # non-empty

    def test_string_override_simple(self):
        """String override replaces full name for simple DID."""
        _write_user_names({SIMPLE_DID: "WW Soll"})
        gen = _make_gen(language="en")
        name = _get_name(gen, SIMPLE_TOPIC, SIMPLE_VALUE)
        assert name == "WW Soll"

    def test_string_override_sub(self):
        """String override on a sub-DID replaces base_name, suffix still appended
        only if no sub-specific override — but resolve_name at sub level
        uses the string as full name."""
        _write_user_names({SUB_DID: "Vorlauf"})
        gen = _make_gen(language="en")
        # base_name becomes "Vorlauf", sub_name = "Vorlauf Actual"
        # Then resolve_name(268, "Actual", "Vorlauf Actual") → string override → "Vorlauf"
        name = _get_name(gen, SUB_TOPIC, SUB_VALUE)
        assert name == "Vorlauf"

    def test_dict_override_per_sub(self):
        """Dict override replaces only matched sub-items."""
        _write_user_names({SUB_DID: {"Actual": "Vorlauf Ist"}})
        gen = _make_gen(language="en")
        name = _get_name(gen, SUB_TOPIC, SUB_VALUE)
        assert name == "Vorlauf Ist"

    def test_override_beats_translation(self):
        """User override takes precedence over German translation."""
        _write_user_names({SIMPLE_DID: "Mein WW"})
        gen = _make_gen(language="de")
        name = _get_name(gen, SIMPLE_TOPIC, SIMPLE_VALUE)
        assert name == "Mein WW"

    def test_unknown_did_ignored(self):
        """Override for a DID not in datapoints causes no error."""
        _write_user_names({99999: "Phantom"})
        gen = _make_gen(language="en")
        # Should load without error
        assert gen.user_names[99999] == "Phantom"
        # Normal DID still works
        name = _get_name(gen, SIMPLE_TOPIC, SIMPLE_VALUE)
        assert name  # non-empty, not "Phantom"

    def test_empty_string_ignored(self):
        """Empty string override falls back to computed name."""
        _write_user_names({SIMPLE_DID: ""})
        gen = _make_gen(language="en")
        name = _get_name(gen, SIMPLE_TOPIC, SIMPLE_VALUE)
        # Should NOT be empty — fallback to computed name
        assert name
        assert name != ""
