"""Regeltests fuer contrib/open3e_guard.py (Plan-Abschnitt 3.3).

Der Guard ist die letzte Schicht der Revert-Architektur: er schreibt, wenn
sonst niemand mehr schreibt. Zwei Fehlerbilder waeren teuer und werden hier
festgenagelt:
  - er greift NICHT, obwohl ein erhoehter Sollwert haengt (Regeln 1/2),
  - er greift, obwohl alles in Ordnung ist (stummer Reader, tiefer Sollwert
    von Hand am Geraet) — das waere ein Dienst, der gegen den Bediener regelt.

Der Guard laeuft auf pi-hwr und wird dort ohne paho-Broker nicht importierbar;
die MQTT-Anbindung wird deshalb gestubbt. Getestet wird ausschliesslich die
Entscheidungslogik, nicht der Schreibweg.
"""

import datetime
import importlib.util
import sys
import types
from pathlib import Path

import pytest

GUARD_PFAD = Path(__file__).resolve().parent.parent / "contrib" / "open3e_guard.py"


@pytest.fixture(scope="module")
def modul():
    """Laedt den Guard mit gestubbtem paho-mqtt."""
    for name in ("paho", "paho.mqtt", "paho.mqtt.client"):
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)
    sys.modules["paho.mqtt.client"].Client = object

    spec = importlib.util.spec_from_file_location("open3e_guard", GUARD_PFAD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def guard(modul):
    return modul.Guard(client=None)


NACHTS = datetime.datetime(2026, 8, 21, 3, 0)
ABENDS = datetime.datetime(2026, 8, 21, 21, 0)
MITTAGS = datetime.datetime(2026, 8, 21, 11, 0)


def test_defaults_loesen_nie_aus(guard, modul):
    guard.werte = {modul.T_SOLL: 52.0, modul.T_SWITCHON: 10.0}
    assert guard.regel_greift(NACHTS) == ""


def test_stummer_reader_ist_kein_schreibgrund(guard):
    """Ohne je einen Wert gesehen zu haben darf der Guard nicht schreiben."""
    assert guard.regel_greift(NACHTS) == ""


def test_regel1_erhoehter_soll_nachts(guard, modul):
    guard.werte = {modul.T_SOLL: 56.0, modul.T_SWITCHON: 10.0}
    assert guard.regel_greift(NACHTS).startswith("Regel 1")


def test_regel1_abgesenkter_switchon_abends(guard, modul):
    guard.werte = {modul.T_SOLL: 52.0, modul.T_SWITCHON: 0.0}
    assert guard.regel_greift(ABENDS).startswith("Regel 1")


def test_regel2_erst_nach_vier_stunden(guard, modul):
    """Im Tagesfenster darf ein legitimer Zyklus (inkl. Stufe 2) durchlaufen."""
    guard.werte = {modul.T_SOLL: 56.0, modul.T_SWITCHON: 10.0}
    assert guard.regel_greift(MITTAGS) == ""
    assert guard.regel_greift(MITTAGS + datetime.timedelta(hours=3)) == ""
    spaet = guard.regel_greift(MITTAGS + datetime.timedelta(hours=4))
    assert spaet.startswith("Regel 2")


def test_rueckkehr_auf_defaults_setzt_uhr_zurueck(guard, modul):
    guard.werte = {modul.T_SOLL: 56.0, modul.T_SWITCHON: 10.0}
    guard.regel_greift(MITTAGS)
    guard.werte[modul.T_SOLL] = 52.0
    assert guard.regel_greift(MITTAGS + datetime.timedelta(hours=1)) == ""
    assert guard.abweichung_seit is None


def test_niedrigerer_soll_ist_keine_abweichung(guard, modul):
    """Senkt jemand den Sollwert am Geraet, ist das keine haengende Anhebung.

    Der Guard kennt nur eine Gefahrenrichtung: zu warm bzw. zu leicht
    ausloesend. Gegen einen tieferen Sollwert regelt er nicht an.
    """
    guard.werte = {modul.T_SOLL: 48.0, modul.T_SWITCHON: 10.0}
    assert guard.regel_greift(NACHTS) == ""


def test_beide_abweichungen_werden_gemeldet(guard, modul):
    guard.werte = {modul.T_SOLL: 60.0, modul.T_SWITCHON: 0.0}
    grund = guard.regel_greift(NACHTS)
    assert "396=60.0" in grund and "SwitchOn=0.0" in grund
