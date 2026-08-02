"""Command-template Tests fuer die Profil-Konfiguration (config/profiles/).

Bestehende command_template-Tests laden ausschliesslich die Legacy-Datei
config/datapoints.yaml. Die wird von BaseGenerator._load_config() aber ignoriert,
sobald profiles/common.yaml existiert — die schreibbaren Profil-Datenpunkte
(880/881 Heizkurve, 424/426 Raumsollwerte, Zeitprogramme) waren damit ungetestet.

Regression: in config/profiles/vitocal.yaml referenzierten die command_templates
von DID 881 die Entitaet number.open3e_681_881_* (ECU 681 statt 680). Da die
Entitaet nicht existiert, griffen die Jinja-Defaults: Schreiben des Gradient
setzte Level auf 0, Schreiben des Level setzte Gradient auf 0.8 — stillschweigend
und auf dem aktiven Heizkreis.
"""

import json
import re
from pathlib import Path

import jinja2
import pytest
import yaml

PROFILES_DIR = Path(__file__).resolve().parent.parent / "config" / "profiles"

# states('number.open3e_<ecu>_<did>_<suffix>')
SELF_REF = re.compile(r"open3e_([0-9a-fA-F]+)_(\d+)_([a-z_]+)")


def _profiles():
    return sorted(PROFILES_DIR.glob("*.yaml"))


def _datapoints(path):
    data = yaml.safe_load(path.read_text()) or {}
    return data.get("datapoints", {}) or {}


def _templates(dp):
    """Liefert (kontext, template_string) fuer alle command_templates eines Datenpunkts."""
    if isinstance(dp, dict):
        if isinstance(dp.get("command_template"), str):
            yield "top-level", dp["command_template"]
        for subname, sub in (dp.get("subs") or {}).items():
            if isinstance(sub, dict) and isinstance(sub.get("command_template"), str):
                yield f"sub {subname}", sub["command_template"]


def _env():
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    env.filters["to_json"] = json.dumps
    return env


def _render(template_str, states_map, **kwargs):
    env = _env()
    env.globals["states"] = lambda eid: states_map[eid]
    return json.loads(env.from_string(template_str).render(**kwargs).strip())


class TestSelfReferenceIntegrity:
    """Querverweise in command_templates muessen auf den eigenen Datenpunkt zeigen.

    Komplexe Datenpunkte schreiben immer alle Sub-Werte gemeinsam. Ein Template
    liest die Geschwister-Subs daher ueber states() zurueck. Zeigt so ein Verweis
    auf eine falsche DID oder ECU, existiert die Entitaet nicht und der Jinja-Default
    ueberschreibt den echten Wert — ohne Fehlermeldung.
    """

    @pytest.mark.parametrize("path", _profiles(), ids=lambda p: p.name)
    def test_self_reference_did_matches_enclosing_did(self, path):
        for did, dp in _datapoints(path).items():
            for ctx, tmpl in _templates(dp):
                for ecu, ref_did, suffix in SELF_REF.findall(tmpl):
                    assert int(ref_did) == int(did), (
                        f"{path.name} DID {did} ({ctx}) verweist auf DID {ref_did} "
                        f"(open3e_{ecu}_{ref_did}_{suffix}). Querverweise muessen auf "
                        f"den eigenen Datenpunkt zeigen."
                    )

    @pytest.mark.parametrize("path", _profiles(), ids=lambda p: p.name)
    def test_self_reference_ecu_is_consistent(self, path):
        seen = {}
        for did, dp in _datapoints(path).items():
            for ctx, tmpl in _templates(dp):
                for ecu, ref_did, _suffix in SELF_REF.findall(tmpl):
                    seen.setdefault(ecu.lower(), []).append(f"DID {did} ({ctx})")
        assert len(seen) <= 1, (
            f"{path.name} referenziert mehrere ECU-Adressen in command_templates: "
            + "; ".join(f"{ecu}: {', '.join(where)}" for ecu, where in sorted(seen.items()))
        )


class TestHeatingCurveRoundtrip:
    """DID 880/881: Schreiben eines Sub-Werts darf den anderen nicht veraendern."""

    @pytest.fixture
    def vitocal(self):
        return _datapoints(PROFILES_DIR / "vitocal.yaml")

    @pytest.mark.parametrize("did,ecu", [(880, "680"), (881, "680")])
    def test_gradient_write_preserves_level(self, vitocal, did, ecu):
        tmpl = vitocal[did]["subs"]["Gradient"]["command_template"]
        states = {f"number.open3e_{ecu}_{did}_level": "2.0"}
        result = _render(tmpl, states, value=0.5)
        assert result["mode"] == "write-raw"
        # grad=5 (0.5*10), level=2 muss erhalten bleiben
        assert result["data"] == [[did, "05020000"]]

    @pytest.mark.parametrize("did,ecu", [(880, "680"), (881, "680")])
    def test_level_write_preserves_gradient(self, vitocal, did, ecu):
        tmpl = vitocal[did]["subs"]["Level"]["command_template"]
        states = {f"number.open3e_{ecu}_{did}_gradient": "0.4"}
        result = _render(tmpl, states, value=3)
        assert result["mode"] == "write-raw"
        # level=3, gradient=4 (0.4*10) muss erhalten bleiben
        assert result["data"] == [[did, "04030000"]]

    @pytest.mark.parametrize("did,ecu", [(880, "680"), (881, "680")])
    def test_negative_level_uses_twos_complement(self, vitocal, did, ecu):
        tmpl = vitocal[did]["subs"]["Level"]["command_template"]
        states = {f"number.open3e_{ecu}_{did}_gradient": "0.4"}
        result = _render(tmpl, states, value=-5)
        assert result["data"] == [[did, "04fb0000"]]


class TestInvalidMarkerSuppression:
    """DID 284 lieferte -3276.8 °C — den Rohwert -32768 eines abgeschalteten
    Heizkreises. Der Filter sitzt am Typ-Template temperature_sensor und muss
    physikalisch unmoegliche Werte zu none machen, ohne gueltige zu verbiegen."""

    @pytest.fixture(scope="class")
    def tmpl(self):
        types_path = Path(__file__).resolve().parent.parent / "config" / "templates" / "types.yaml"
        types = yaml.safe_load(types_path.read_text()) or {}
        t = types["temperature_sensor"].get("value_template")
        assert t, "temperature_sensor braucht ein value_template gegen den -32768-Marker"
        return t

    def _render_raw(self, tmpl, value):
        return _env().from_string(tmpl).render(value=value).strip()

    def test_invalid_marker_becomes_none(self, tmpl):
        assert self._render_raw(tmpl, "-3276.8") == "None"

    @pytest.mark.parametrize("value", ["-20.5", "0", "21.6", "52.0", "-273.0"])
    def test_valid_temperatures_pass_through(self, tmpl, value):
        assert self._render_raw(tmpl, value) == value

    def test_non_numeric_payload_passes_through(self, tmpl):
        """Nicht-numerische Payloads duerfen nicht am float-Default haengenbleiben."""
        assert self._render_raw(tmpl, "unavailable") == "unavailable"
