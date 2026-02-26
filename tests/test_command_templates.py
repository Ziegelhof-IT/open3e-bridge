"""TEST-CMD: Jinja2 command_template rendering tests, incl. FIX-05 regression."""

import json
from pathlib import Path

import jinja2
import pytest
import yaml

YAML_PATH = Path(__file__).resolve().parent.parent / "config" / "datapoints.yaml"


def _env():
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    env.filters["to_json"] = json.dumps
    return env


def _load_datapoints():
    with open(YAML_PATH) as f:
        return yaml.safe_load(f)["datapoints"]


def _render(template_str: str, **kwargs) -> dict:
    tmpl = _env().from_string(template_str)
    raw = tmpl.render(**kwargs).strip()
    return json.loads(raw)


# ── DID 2626: MaxPowerElectricalHeater ────────────────────────────
class TestDID2626:
    @pytest.fixture(autouse=True)
    def _load(self):
        self.tmpl = _load_datapoints()[2626]["command_template"]

    def test_value_500(self):
        result = _render(self.tmpl, value=500)
        assert result["mode"] == "write-raw"
        assert result["data"] == [[2626, "f4010000"]]

    def test_value_0(self):
        result = _render(self.tmpl, value=0)
        assert result["data"] == [[2626, "00000000"]]

    def test_value_256(self):
        result = _render(self.tmpl, value=256)
        # 256%256=0 -> '00', 256//256=1 -> '01'
        assert result["data"] == [[2626, "00010000"]]

    def test_small_value_two_digit_hex(self):
        """Values < 16 must produce two-digit hex (e.g. '05' not '5')."""
        result = _render(self.tmpl, value=5)
        cmddata = result["data"][0][1]
        assert cmddata == "05000000"
        assert len(cmddata) == 8  # always 8 hex chars


# ── DID 1102 Setpoint: FIX-05 regression ─────────────────────────
class TestDID1102Setpoint:
    @pytest.fixture(autouse=True)
    def _load(self):
        dp = _load_datapoints()[1102]
        self.tmpl = dp["subs"]["Setpoint"]["command_template"]

    def test_value_50(self):
        result = _render(self.tmpl, value=50)
        assert result["mode"] == "write-raw"
        # '14' + '%02x'%50='32' + '%02x'%50='32'
        assert result["data"] == [[1102, "143232"]]

    def test_value_5_two_digit_hex(self):
        """FIX-05 regression: value=5 must produce '05' not '5'."""
        result = _render(self.tmpl, value=5)
        cmddata = result["data"][0][1]
        assert cmddata == "140505"
        assert len(cmddata) == 6

    def test_value_20(self):
        result = _render(self.tmpl, value=20)
        # '14' + '%02x'%20='14' + '%02x'%20='14'
        assert result["data"] == [[1102, "141414"]]


# ── DID 1103 Setpoint: same %02x check ───────────────────────────
class TestDID1103Setpoint:
    @pytest.fixture(autouse=True)
    def _load(self):
        dp = _load_datapoints()[1103]
        self.tmpl = dp["subs"]["Setpoint"]["command_template"]

    def test_value_50(self):
        result = _render(self.tmpl, value=50)
        assert result["mode"] == "write-raw"
        # '1464' + '%02x'%50='32'
        assert result["data"] == [[1103, "146432"]]

    def test_value_5_two_digit_hex(self):
        """FIX-05 regression: value=5 must produce '146405' not '14645'."""
        result = _render(self.tmpl, value=5)
        cmddata = result["data"][0][1]
        assert cmddata == "146405"
        assert len(cmddata) == 6
