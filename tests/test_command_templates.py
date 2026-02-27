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


def _render_raw(template_str: str, **kwargs) -> str:
    """Render template and return raw stripped string (for empty-output tests)."""
    tmpl = _env().from_string(template_str)
    return tmpl.render(**kwargs).strip()


# ── DID 2626: MaxPowerElectricalHeater ────────────────────────────
class TestDID2626:
    @pytest.fixture(autouse=True)
    def _load(self):
        self.tmpl = _load_datapoints()[2626]["command_template"]

    def test_value_0(self):
        result = _render(self.tmpl, value=0)
        assert result["mode"] == "write-raw"
        assert result["data"] == [[2626, "00000000"]]

    def test_value_4000(self):
        result = _render(self.tmpl, value=4000)
        assert result["mode"] == "write-raw"
        # 4000%256=160=0xa0, 4000//256=15=0x0f
        assert result["data"] == [[2626, "a00f0000"]]

    def test_value_8000(self):
        result = _render(self.tmpl, value=8000)
        # 8000%256=64=0x40, 8000//256=31=0x1f
        assert result["data"] == [[2626, "401f0000"]]

    def test_small_safe_hex_format(self):
        """Values >= 4000 must produce two-digit hex (FIX-05 regression)."""
        result = _render(self.tmpl, value=5400)
        cmddata = result["data"][0][1]
        # 5400%256=24=0x18, 5400//256=21=0x15
        assert cmddata == "18150000"
        assert len(cmddata) == 8  # always 8 hex chars


# ── SAFE-01: DID 2626 dangerous value rejection ──────────────────
class TestDID2626Safe01:
    """SAFE-01: Values 1-3999W cause compressor failure (Viessmann FW bug).

    The Jinja guard must produce empty output for dangerous values,
    preventing HA from sending the command to the heat pump.
    """

    @pytest.fixture(autouse=True)
    def _load(self):
        self.tmpl = _load_datapoints()[2626]["command_template"]

    @pytest.mark.parametrize("value", [1, 100, 500, 2000, 3999])
    def test_rejects_dangerous_values(self, value):
        raw = _render_raw(self.tmpl, value=value)
        assert raw == "", f"Value {value}W must be rejected (empty output), got: {raw!r}"

    def test_allows_zero(self):
        result = _render(self.tmpl, value=0)
        assert result["mode"] == "write-raw"
        assert result["data"] == [[2626, "00000000"]]

    @pytest.mark.parametrize("value", [4000, 5400, 8000])
    def test_allows_safe_values(self, value):
        result = _render(self.tmpl, value=value)
        assert result["mode"] == "write-raw"
        assert result["data"][0][0] == 2626


# ── DID 2335: FourWayValve value_template ─────────────────────────
class TestDID2335:
    @pytest.fixture(autouse=True)
    def _load(self):
        self.tmpl = _load_datapoints()[2335]["value_template"]

    @pytest.mark.parametrize("value,expected", [
        (0, "Heizen"),
        (1, "Abtauen"),
        (2, "Warmwasser"),
        (3, "Kuehlen"),
        (99, "99"),
    ])
    def test_value_mapping(self, value, expected):
        tmpl = _env().from_string(self.tmpl)
        result = tmpl.render(value=value).strip()
        assert result == expected


# ── DID 1710: DomesticHotWaterOneTimeCharge Button ────────────────
class TestDID1710:
    @pytest.fixture(autouse=True)
    def _load(self):
        self.tmpl = _load_datapoints()[1710]["command_template"]

    def test_button_press(self):
        result = _render(self.tmpl, value="PRESS")
        assert result["mode"] == "write"
        assert result["data"] == [[1710, 1]]


# ── DID 1006: QuickMode Switch ────────────────────────────────────
class TestDID1006:
    @pytest.fixture(autouse=True)
    def _load(self):
        self.tmpl = _load_datapoints()[1006]["command_template"]

    def test_switch_on(self):
        result = _render(self.tmpl, value="ON")
        assert result["mode"] == "write"
        assert result["data"] == [[1006, "ON"]]

    def test_switch_off(self):
        result = _render(self.tmpl, value="OFF")
        assert result["mode"] == "write"
        assert result["data"] == [[1006, "OFF"]]


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
