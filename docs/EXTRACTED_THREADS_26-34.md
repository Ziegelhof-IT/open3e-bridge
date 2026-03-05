# Extrahierte Threads #26-34 — 2026-02-27

Vollstaendige Extraktion der mittleren Relevanz Viessmann Community Threads (#26-30)
und aller externen Forum-Threads (#31-34).

---

## Thread #26: Modbus Interface

**URL**: https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/Modbus-Interface/td-p/333200
**Posts**: 25 | **Thema**: Modbus als Alternative zu CAN fuer E3-Geraete

### Zusammenfassung

- Vitocal 250-SH HAWB-M-AC 252.B10 hat kein OPTO2, nur WLAN-Modul
- **Wago MB/TCP-Gateway** ist die offizielle Modbus-Loesung fuer E3-Geraete
- Viessmann bestaetigt: Wago-Gateway funktioniert mit neuer WP-Generation
- **Kritik**: Modbus-Dokumentation mangelhaft (Datentypen, Registerlaenge fehlen)
- **Nicht alle Register funktionieren** trotz Dokumentation
- Community empfiehlt stattdessen CAN-Bus via open3e (deutlich mehr Datenpunkte)
- Wago-Gateway Kosten: ca. 600-800 EUR vs. USB-CAN-Adapter ca. 35 EUR
- ioBroker und Home Assistant Integration diskutiert
- Verweis auf CAN-Bus Home Automation Thread als bessere Loesung

### Technische Details

- Modbus Register IN-30022: Warmwassertemperatur
- E3-Regelung unterstuetzt Modbus/TCP ueber Wago-Gateway
- CAN-Bus bietet Zugriff auf deutlich mehr Parameter als Modbus
- open3e Projekt als kostenguenstige Alternative etabliert

---

## Thread #27: Modbus Datenpunkt verschwunden

**URL**: https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/Modbus-Datenpunkt-zu-Vitocal-250-A-verschwunden/td-p/424925
**Posts**: 3 | **Thema**: Modbus-Register nach Stromausfall nicht mehr verfuegbar

### Zusammenfassung

- Wago Modbus/TCP Gateway zu Vitocal 250-A
- Register IN-30022 (Warmwassertemperatur) lieferte nach Stromausfall 3276.8 Grad C
- Gateway-Scan findet Register nicht mehr
- **Ursache**: FW-Update der WP hat Modbus-Register verschoben/entfernt
- 3276.8 Grad = typischer Fehler-Wert (0x7FF8 = NaN als Float, oder 32768/10)
- Problem: Viessmann kann Register nach FW-Updates aendern ohne Ankuendigung

### Technische Details

- Modbus Register IN-30022 = Warmwasser-Isttemperatur
- Fehlerwert 3276.8 deutet auf falsche Adresse oder ungueltige Daten
- FW-Updates koennen Modbus-Registerzuordnung aendern
- CAN-Bus/UDS-DIDs sind stabiler als Modbus-Register

---

## Thread #28: Modulation Vitocal 250-A

**URL**: https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/Modulation-Vitocal-250-A/td-p/354259
**Posts**: 20 | **Thema**: Kompressor-Leistungsregelung und Modulationsbereich

### Zusammenfassung

- Frage: Kann WP-Leistung extern gesteuert werden (PV-Ueberschuss)?
- Weder API noch Wago-Gateway bieten direkten Leistungs-Datenpunkt
- **Workaround**: Indirekte Modulation ueber Sollwert-Anpassung
  - Grosse Differenz Ist/Soll → hohe Verdichterleistung
  - Kleine Differenz → niedrige Verdichterleistung
- KNX-Gateway bei Vitocal 200-A: Steuerung ueber VL-Sollwert und WW-Sollwert
- **Untere Modulationsgrenze** der 250-A problematisch:
  - Datenblatt: 2.8 kW thermisch untere Grenze
  - Praxis: Tatsaechliche untere Grenze AT-abhaengig und hoeher als angegeben
  - Bei ueberdimensionierter WP: Takten statt Modulieren
- Spreizung VL/RL bestimmt Verdichterleistung
- Sekundaerkreispumpe bei WW-Bereitung bereits 100%
- **Risiko bei zu niedriger Verdichterdrehzahl**: Weniger Schmierung, Kompressorschaden
- Mindest-Drehzahl kann theoretisch via Service-Parameter geaendert werden (nicht empfohlen)

### Technische Details

- DID 2626: Leistungsvorgabe (bereits als gefaehrlich bekannt, 1-3999W → Kompressor-Ausfall)
- Modulation ueber Sollwert-Delta: Standardverfahren fuer PV-Nutzung
- JAZ ca. 4.4: Bei 4 kW thermisch ≈ 900 W elektrisch
- Verdichterdrehzahl ist AT-abhaengig (nicht linear zur therm. Leistung)
- Planungsanleitungen zeigen reale Modulationskurven (AT-abhaengig)

---

## Thread #29: Ventilatorheizung Vitocal 250-A

**URL**: https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/Ventilatorheizung-fuer-Vitocal-250-A/td-p/509356
**Posts**: 6 | **Thema**: DID 2852 Ventilatorringheizung, Vereisungsprobleme

### Zusammenfassung

- Vitocal 250-A: Aussenrahmen des Ventilators vereist bei tiefen Temperaturen
- Ventilatorringheizung ist Zubehoer (nicht serienmässig), muss nachgeruestet werden
- **Kritik**: Viessmann liefert Geraete ohne noetige Heizung aus, obwohl Vereisungsgefahr bekannt
- SCOP-Angaben in Datenblaettern beruecksichtigen Zusatzheizung nicht transparent
- Viessmann-Antwort: Frostschutz "allgemein" ausreichend, Ringheizung nur bei "besonders frost-/schneegefaehrdeten Standorten"
- Region Schwaebische Alb: Vereisungsprobleme Ende Dezember 2024

### Technische Details

- DID 2852: Ventilatorringheizung (Steuerung/Status)
- Nachruestung moeglich aber kostenpflichtig
- Abtaufunktion der WP allein nicht ausreichend bei starkem Frost
- Relevant fuer Monitoring: Status der Ventilatorheizung ueber CAN auslesbar

---

## Thread #30: Steuerbare Verbrauchseinrichtung (StVE) §14a

**URL**: https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/Vitocal-250-A-in-2025-als-steuerbare-Verbrauchseinrichtung/td-p/453264
**Posts**: 2 | **Thema**: §14a EnWG steuerbare Verbrauchseinrichtung ab 2025

### Zusammenfassung

- Vitocal 250 Pro angekuendigt mit erweiterter Elektronik
- Frage: Wird bestehende 250-A per FW-Update StVE-faehig oder braucht man externe Hardware?
- "Dimmung" (Leistungsreduktion auf Netzbetreiber-Signal) gewuenscht
- Flexible Strompreise der Stromboerse nutzen
- **Keine Antwort von Viessmann** zu konkreter Umsetzung (Stand 07/2024)

### Technische Details

- §14a EnWG: Netzbetreiber kann steuerbare Verbrauchseinrichtungen dimmen
- Relevant fuer open3e: Leistungssteuerung via CAN koennte StVE-Anforderungen abdecken
- Vitocal 250 Pro: Nachfolger mit erweiterter Steuerbarkeit

---

## Thread #31: Viessmann Vitocharge Daten lokal auslesen (IP-Symcon)

**URL**: https://community.symcon.de/t/viessmann-vitocharge-daten-lokal-auslesen/133677
**Plattform**: IP-Symcon Community | **Thema**: Lokale PV-Datenabfrage

### Zusammenfassung

- Viessmann PV-Anlagendaten (Stromverbrauch, Produktion, Batteriestand) lokal auslesen
- Offizielle API kostenpflichtig (ca. 20 EUR/Monat ueber VitoConnect)
- **Loesung**: GitHub-Projekt "viessmann-gridbox-connector" (Benutzer unl0ck)
  - Authentifizierung ueber GridBox-Benutzerkonto
  - Lokale Datenabfrage ohne Cloud-Abhaengigkeit
  - Minutenweise Datenspeicherung in lokalen Dateien
  - Grafana-Visualisierung
- GridBox-Hardware notwendig
- Keine CAN-Bus oder Protokoll-Details im Thread

---

## Thread #32: Viessmann via USB-CAN Adapter (OpenHAB)

**URL**: https://community.openhab.org/t/viessmann-via-usb-can-adapter/150780
**Plattform**: OpenHAB Community | **Thema**: OpenHAB CAN-Bus Integration

### Zusammenfassung

- OpenHAB-Integration von Viessmann ueber USB-CAN-Adapter
- Verweis auf open3e Projekt (https://github.com/abnoname/open3e)
- USB-CAN-Adapter Kosten: ca. 35 EUR
- CAN-Format: 11-bit CAN Object ID, 8 Bytes Daten
- Serielle Bindung und zeilenbasierte Protokolle wurden versucht
- Verweis auf Viessmann Community CAN-Bus Thread
- Wenig technische Details im Thread selbst

---

## Thread #33: VX3 Hybrid Wechselrichter (Solaranzeige)

**URL**: https://solaranzeige.de/phpBB3/viewtopic.php?t=2376
**Plattform**: Solaranzeige Forum | **Thema**: VX3 Integration in Solaranzeige

### Zusammenfassung

- Viessmann VX3 Hybrid-Wechselrichter mit Batteriespeicher
- **Fundamentales Problem**: Daten nicht direkt vom Wechselrichter abrufbar
- Alle Daten laufen ueber Viessmann-Cloud-Server
- Viessmann API kostenpflichtig
- **Konflikt**: Solaranzeige ist lokales System, liest Daten direkt aus Geraet
- Cloud-zentrierte Architektur des VX3 verhindert lokale Integration
- Stand 07/2024: Keine Loesung fuer direkte lokale Anbindung bekannt
- Verweis auf Viessmann Developer Portal APIs

---

## Thread #34: MQTT Mode Command Template (Home Assistant)

**URL**: https://community.home-assistant.io/t/help-needed-for-mqtt-mode-command-template-configuration-for-water-heater/655013
**Plattform**: Home Assistant Community | **Thema**: HA Water Heater MQTT Templates

### Zusammenfassung

- Viessmann Vitodens Integration ueber open3e via MQTT in Home Assistant
- Problem: Template-Umwandlung von Modi "off"/"gas" in MQTT-Payload
- **Loesung**: Dictionary-Lookup im Jinja2 Template

### Technische Details — Direkt relevant fuer open3e-bridge

**DID 531**: Betriebsmodus (Vitodens)
- Modus "off" → `{"mode": "write-raw", "data":[[531,"0000"]]}`
- Modus "gas" → `{"mode": "write-raw", "data":[[531,"0101"]]}`

**DID 396**: Warmwasser-Solltemperatur (Write)

**Command Template Loesung**:
```yaml
mode_command_template: >
  {% set values = { 'gas':'0101', 'off':'0000'} %}
  {% set cmd = {'mode': 'write-raw', 'data':[[531, values[value]]]} %}
  {{ cmd | to_json }}
```

- `values[value]` als Dictionary-Lookup statt direkter Wertverwendung
- Water-Heater-Card-Integration und Service-Aufrufe funktionieren
- Temperatur-Lese/Schreibvorgaenge und Modusabfrage bestaetigt

---

## Statistik

| Thread | Posts | Chars | Plattform |
|--------|-------|-------|-----------|
| #26 Modbus Interface | 25 | 10677 | Viessmann |
| #27 Modbus verschwunden | 3 | 1756 | Viessmann |
| #28 Modulation 250-A | 20 | 19398 | Viessmann |
| #29 Ventilatorheizung | 6 | 4045 | Viessmann |
| #30 StVE §14a | 2 | 857 | Viessmann |
| #31 Vitocharge IP-Symcon | - | - | IP-Symcon |
| #32 USB-CAN OpenHAB | - | - | OpenHAB |
| #33 VX3 Solaranzeige | - | - | Solaranzeige |
| #34 MQTT Template HA | - | - | Home Assistant |
| **Gesamt** | **56+** | **36733+** | **5 Plattformen** |
