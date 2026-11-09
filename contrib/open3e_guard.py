#!/usr/bin/env python3
"""open3e-guard — unabhaengige Rueckstellinstanz fuer die PV-Warmwasserladung.

Umsetzung von homelab/homeassistant/docs/plan-ww-pv-ladung.md, Abschnitt 3.3.

Rolle in der dreischichtigen Revert-Architektur: Schicht 3. Der Automat in
Home Assistant (Schicht 1) und dessen Failsafes (Schicht 2) teilen einen
Single Point of Failure — Home Assistant selbst. Dieser Guard laeuft auf
demselben Host wie der open3e-reader, also auf dem Schreibweg, und ueberlebt
HA-, EMHASS- und Automations-Ausfaelle vollstaendig.

Leitplanken (Plan 0.2), hier durch Konstruktion erzwungen:
  - Der Guard kennt genau zwei Schreibbefehle: die beiden Defaults.
    Es gibt keinen Codepfad, der einen anderen Wert oder einen anderen DID
    schreiben koennte.
  - Er ist zustandsarm: eine Uhr fuer die erste beobachtete Abweichung.
    Nach einem Guard-Neustart beginnt die Uhr neu — akzeptabel, weil
    Regel 1 den Nachtbereich hart deckelt.
  - Jede Intervention ist ein Befund und wird retained nach
    open3e/guard/alarm publiziert.

Zwei statische Regeln:
  1. Abweichung ausserhalb 09:00-20:00           -> sofort Defaults schreiben
  2. Abweichung laenger als GUARD_MAX_STUNDEN    -> Defaults schreiben
     (laenger dauert kein legitimer Zyklus, auch nicht mit Stufe 2)
"""

import datetime
import os
import json
import logging
import sys
import time

import paho.mqtt.client as mqtt

# --- Anlagen-Defaults. Die einzigen Werte, die dieser Dienst je schreibt. ---
DEFAULT_SOLL = 52.0
DEFAULT_SWITCHON = 10.0

# --- Regelparameter --------------------------------------------------------
FENSTER_VON = 9         # Regel 1: ausserhalb 09:00-20:00 sofort zurueckstellen
FENSTER_BIS = 20
# Regel 2: Abweichung im Fenster laenger als 4 h. Ueber die Umgebungsvariable
# uebersteuerbar, damit der Trockentest V11 dieselbe Codebasis prueft wie der
# Dauerbetrieb, statt eine veraenderte Kopie.
GUARD_MAX_STUNDEN = float(os.environ.get("OPEN3E_GUARD_MAX_STUNDEN", "4"))
TOLERANZ = 0.05         # Float-Vergleich der Rueckgelesenen
PRUEFTAKT = 60          # Sekunden

MQTT_HOST = "mqtt.ziegelhof"
MQTT_PORT = 1883
MQTT_ARGS = "/etc/open3e/mqtt.args"   # 600, gleiche Credentials wie der Reader

T_SOLL = "open3e/680_396_DomesticHotWaterTemperatureSetpoint"
T_SWITCHON = "open3e/680_1085_DomesticHotWaterHysteresis/SetpointSwitchOn"
T_CMND = "open3e/cmnd"
T_ALARM = "open3e/guard/alarm"

log = logging.getLogger("open3e-guard")


def lies_credentials(pfad: str) -> tuple:
    """Holt user/pass aus der Reader-Argumentdatei. Nichts wird geloggt."""
    felder = open(pfad).read().split()
    return felder[felder.index("--mqttuser") + 1].split(":", 1)


class Guard:
    def __init__(self, client: mqtt.Client):
        self.client = client
        self.werte = {}
        self.abweichung_seit = None

    # --- MQTT ------------------------------------------------------------
    def on_connect(self, client, userdata, flags, rc):
        log.info("Broker verbunden (rc=%s), abonniere Rueckleseweg", rc)
        client.subscribe(T_SOLL)
        client.subscribe(T_SWITCHON)

    def on_message(self, client, userdata, msg):
        try:
            self.werte[msg.topic] = float(msg.payload.decode())
        except (ValueError, UnicodeDecodeError):
            log.warning("Unlesbare Nutzlast auf %s", msg.topic)

    # --- Bewertung -------------------------------------------------------
    def abweichungen(self) -> list:
        """Liste der Abweichungen von den Defaults. Leer = alles in Ordnung.

        Fehlende Werte gelten NICHT als Abweichung: kurz nach dem Start hat
        der Guard noch nichts gesehen, und ein stummer Reader ist kein Grund,
        blind zu schreiben.
        """
        befunde = []
        soll = self.werte.get(T_SOLL)
        switchon = self.werte.get(T_SWITCHON)
        if soll is not None and soll > DEFAULT_SOLL + TOLERANZ:
            befunde.append(f"396={soll}")
        if switchon is not None and switchon < DEFAULT_SWITCHON - TOLERANZ:
            befunde.append(f"SwitchOn={switchon}")
        return befunde

    def regel_greift(self, jetzt: datetime.datetime) -> str:
        """Gibt den Interventionsgrund zurueck, oder '' wenn nichts zu tun ist."""
        befunde = self.abweichungen()
        if not befunde:
            self.abweichung_seit = None
            return ""

        if self.abweichung_seit is None:
            self.abweichung_seit = jetzt
            log.info("Abweichung beobachtet: %s", ", ".join(befunde))

        if not (FENSTER_VON <= jetzt.hour < FENSTER_BIS):
            return (f"Regel 1 (ausserhalb {FENSTER_VON}:00-{FENSTER_BIS}:00): "
                    + ", ".join(befunde))

        dauer = (jetzt - self.abweichung_seit).total_seconds() / 3600
        if dauer >= GUARD_MAX_STUNDEN:
            return (f"Regel 2 (Abweichung seit {dauer:.1f} h): "
                    + ", ".join(befunde))
        return ""

    # --- Intervention ----------------------------------------------------
    def stelle_zurueck(self, grund: str):
        log.warning("INTERVENTION: %s", grund)
        self.client.publish(T_CMND, json.dumps(
            {"mode": "write", "data": [["1085.SetpointSwitchOn", DEFAULT_SWITCHON]]}))
        time.sleep(0.5)
        self.client.publish(T_CMND, json.dumps(
            {"mode": "write", "data": [[396, DEFAULT_SOLL]]}))
        self.client.publish(T_ALARM, json.dumps({
            "grund": grund,
            "zeit": datetime.datetime.now().isoformat(timespec="seconds"),
            "geschrieben": {"396": DEFAULT_SOLL, "SwitchOn": DEFAULT_SWITCHON},
        }), retain=True)
        # Uhr zuruecksetzen: die naechste Abweichung ist ein neuer Befund.
        self.abweichung_seit = None

    def lauf(self):
        while True:
            time.sleep(PRUEFTAKT)
            grund = self.regel_greift(datetime.datetime.now())
            if grund:
                self.stelle_zurueck(grund)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stderr,
    )
    user, passwort = lies_credentials(MQTT_ARGS)
    client = mqtt.Client()
    client.username_pw_set(user, passwort)
    guard = Guard(client)
    client.on_connect = guard.on_connect
    client.on_message = guard.on_message
    client.connect(MQTT_HOST, MQTT_PORT, 30)
    client.loop_start()
    log.info("open3e-guard laeuft. Defaults: 396=%s, SwitchOn=%s",
             DEFAULT_SOLL, DEFAULT_SWITCHON)
    try:
        guard.lauf()
    finally:
        client.loop_stop()


if __name__ == "__main__":
    main()
