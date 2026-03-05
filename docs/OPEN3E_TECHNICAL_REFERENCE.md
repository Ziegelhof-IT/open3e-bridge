# Open3E Technical Reference — Consolidated Community Knowledge

**Stand:** 2026-02-27
**Quellen:** open3e Wiki, GitHub Discussions (#54, #184, #207, #27, #123, #205, #285, #293, #298, #308), Viessmann Community Thread (78 Seiten, td-p/356066), Community Threads #8-34 (Viessmann, HA, OpenHAB, IP-Symcon, Solaranzeige)

---

## 1. ECU-Adressen (Vitocal 250-A System)

| ECU | Typ | Rolle | Besonderheiten |
|-----|-----|-------|----------------|
| 0x680 | HPMUMASTER | Hauptcontroller | Alle Standard-DIDs, Default-ECU |
| 0x684 | HMI | Display | User-Interface |
| 0x68c | VCMU | Kaeltekreis | Kompressor-Drehzahl (2630-2632) NUR hier, NRC 0x22 auf 0x680 |
| 0x6c3 | BACKENDGATEWAY | TCU300 Cloud | Internet-Modul |
| 0x6c5 | BACKENDGATEWAY | TCU201 | Alternativ-Gateway |
| 0x6cf | EHCU | Heizstab-Controller | Eigene ECU |
| 0x6a1 | EMCU (VX3) | PV/Batterie-Inverter | DID 1603 firmware-abhaengig (4 vs 12 Bytes) |

### Abweichende ECU-Adressen (andere Geraete-Typen)

| ECU | Geraete-Typ | Hinweise |
|-----|-------------|----------|
| 0x380 | Vitocal 150A | Haupt-WP, voellig anderes Adressschema als 250-A |
| 0x3a1 | VX3 (bei Vitocal 150A) | Wechselrichter/Speicher |

**Wichtig:** ECU-Adressen sind geraetetypabhaengig. `open3e_depictSystem` erkennt automatisch alle ECUs auf dem Bus und generiert passende `devices.json`. Der Parameter `-dev vx3` ist **DEPRECATED** und nutzt alte hardcoded Datapoints statt des depictSystem-Scans.

### Geraete ohne Optolink (nur CAN)

Neuere E3-Geraete haben **keine Optolink-Schnittstelle** mehr. Zugriff nur via CAN-Bus/UDS:
- **Vitodens 200-W B2HF** — kein Optolink, kein EEBUS, Kommunikation verschluesselt zur Cloud (Thread #12)
- **Vitocal 250-A** — CAN-Bus (Stecker 91) + WLAN zur Cloud
- **Vitocal 262-a** — CAN-Buchsen vorhanden, Details unklar (Thread #9, keine Daten extrahiert)

## 2. CAN-Bus-Topologie

### Stecker und Busse

| Stecker | Bus | Beschreibung | Zugang |
|---------|-----|-------------|--------|
| **91** | Extern | User-zugaenglicher CAN-Anschluss | An IDU-Aussenseite, Standard-Anschluss fuer open3e |
| **72** | Intern | IDU↔ODU, Vitocal↔Vitocharge intern | Innerhalb der IDU, fuer depictSystem interner DIDs |
| **96** | Digital I/O | Externe Anforderung (ein/aus) | Nicht CAN, sondern Digitaleingang |

### Split-System Topologie (Vitocal 250-A)
```
Externer Bus (Stecker 91):
  IDU (0x680) ←→ HMI (0x684) ←→ TCU (0x6c3) ←→ VX3 (0x6a1) ←→ E380

Interner Bus (Stecker 72):
  IDU (0x680) ←→ ODU/VCMU (0x68c) ←→ EHCU (0x6cf)
```

### CAN-Verkabelung (Community-Erfahrungen)

- **Twisted-Pair ist KRITISCH**: Kabel >5m ohne TP verursacht Uebertragungsfehler
- Empfohlen: Geschirmtes CAT5e, ein TP fuer CAN-H/CAN-L, einzelne Ader fuer GND
- **GND muss verbunden sein** (3 Adern: CAN-H, CAN-L, GND)
- Abschlusswiderstand (120Ω) am letzten physischen Geraet
- USB-CAN Adapter: Galvanisch getrennt empfohlen (z.B. Innomaker USB2CAN-C)

### E380CA Energiezaehler CAN-Anschluss

- Verbindung zum VX3 via **JYSTY Klingelleitung** am ext. CAN-BUS (gelbe Stecker rechts oben an EMCU) (Thread #16)
- **Terminierung**: E380CA hat rote Bruecke (Abschlusswiderstand) auf einem Ausgang. VX3 hat zwei gelbe CAN-Stecker, einer mit Abschlusswiderstand — muss drin bleiben solange Kontakt nicht genutzt
- Zweiter E380CA moeglich: NODE-ID (CAN-Adresse) muss geaendert werden (Thread #16)

### Bekannte CAN-Fehler

| Fehler | Ursache | Loesung |
|--------|---------|---------|
| **F.764** | CAN-Adapter am E380 angeschlossen (Potentialprobleme) | USB-CAN-Adapter an Stecker 91 statt E380 anschliessen |
| **F.910** | Mehrere Fuehrungsgeraete auf CAN-Bus erkannt | Vitoair + Vitocal auf gleichem Bus: Master-Konflikt (Thread #20) |
| **F.1034** | Kommunikationsfehler externer CAN | GND-Verbindung pruefen, galvanisch getrennten Adapter verwenden |
| `XXX_ERR` dauerhaft | open3e stoppt MQTT bei CAN-Fehlern | `RestartSec=5` in systemd Service, USB-Energiesparmodus deaktivieren |

## 3. MQTT Topic-Struktur

Format: `open3e/{ecuAddr:03X}_{didNumber}_{didName}/{SubItem}`
Beispiel: `open3e/680_274_OutsideTemperatureSensor/Actual`

Command-Topic: `open3e/cmnd`
LWT: `open3e/LWT` (online/offline, qos=1, retain=True)

### Command-Modi (Listener)
```json
{"mode": "read",           "data": [274, 271]}
{"mode": "write",          "data": [[396, 47.5]]}
{"mode": "write-raw",      "data": [[396, "D601"]]}
{"mode": "write-raw-sid77","data": [[927, "02"]]}
{"mode": "read",           "addr": "0x68C", "data": [256]}
```

### HA Command Template Beispiel (DID 531, Thread #34)
```yaml
mode_command_template: >
  {% set values = { 'gas':'0101', 'off':'0000'} %}
  {% set cmd = {'mode': 'write-raw', 'data':[[531, values[value]]]} %}
  {{ cmd | to_json }}
```

## 3. Codec-Referenz

| Codec | Bytes | Default Scale | Hinweise |
|-------|-------|---------------|----------|
| O3EInt16 | 2 | **10.0** | 470 raw = 47.0°C, little-endian, signed moeglich |
| O3EInt32 | 4 | 1.0 | Power in Watt |
| O3EBool | 1 | - | Liefert `"on"`/`"off"` (Strings!) |
| O3EEnum | N | - | Liefert `{"ID": int, "Text": str}` |
| O3EComplexType | N | - | Dict von Sub-Items |
| O3EList | N | - | Count-Prefix + Array |

**Temperatur-Sensor Pattern (9 Bytes):**
```
O3EComplexType(9, [Actual/Min/Max/Avg (O3EInt16 scale=10 signed), Unknown (O3EByteVal)])
```

**Pressure: scale=100** (DID 322/325)

## 4. DID-Katalog nach Kategorie

### Temperaturen (ECU 0x680, alle read-only)
268 Flow, 269 Return, 271 DHW, 274 Outside, 284/286 Mixer1/2 Flow,
320 PrimaryHX, 321 CompressorInlet, 324 CompressorOutlet,
355 SecondaryHX, 1769 PrimaryInlet, 1772 CompressorOil,
2333 Economizer, 2334 EvaporatorVapor, 3016 HeatingBuffer

### Leistung/Geschwindigkeit (read-only)
2346 CompressorSpeedPercent, 2488 PowerConsumptionSystem (W),
2496 ThermalCapacitySystem (W), 2569 CompressorSpeedRps (scale=10)

### Energie (je 6 Zeitperioden: Today/7d/Month/PastMonth/Year/PastYear)
- Elektrisch: 548 Heizung, 565 WW, 566 Kuehlung, 2517 Heizstab-WW, 2526 Heizstab-Heizung
- Thermisch: 1211 Heizung, 1391 WW, 2529 Kuehlung
- COP: 2622 Heizung, 2623 Kuehlung, 2624 WW, 2625 Gesamt (Actual/Generated/Consumed)

### Pumpen/Ventile (read-only)
381 CentralHeatingPump (State/Target/Actual/Unknown),
389/391 EEV1/2 Position (%),
1775/1776 Fan1/Fan2 (%),
2735 4-Wege-Ventil (0=Heating, 1=Defrost, 2=DHW, 3=Cooling)

### Schreibbare DIDs

| DID | Name | Format | Hinweise |
|-----|------|--------|----------|
| 396 | DHW-Temperatur | write, float | 10-60°C |
| 395 | Heizungs-Sollwert | write, float | °C |
| 424/426 | Raum-Sollwert HK1/2 | write, Complex | Comfort/Standard/Reduced/Increased/Duration |
| 531 | DHW-Betriebsart (Vitodens) | write-raw | `"0101"`=gas, `"0000"`=off (Thread #34) |
| 880/881 | Heizkurve HK1/2 | write sub | `.Gradient`(scale=10), `.Level`(signed), `.BasePoint`(signed, scale=10) |
| 1100-1103 | HK1 Reduced/Normal/Comfort/MinMax | write | °C |
| 1415-1418 | Betriebsart HK1-4 | write-raw | `"0000"`=off, `"0102"`=heat, `"0510"`=cool |
| 691-697 | WW-Zeitplan Mo-So | write JSON | Volle Struktur mit Count + Schedules |
| 761-837 | HK-Zeitplaene | write JSON | 7 Tage x 8 Kreise |
| 1006 | QuickMode (WW-Einmal) | write-raw | `"02010000"`=on, `"00000000"`=off, braucht OpMode=2 |
| 3029 | DHW Eco/Comfort | write | 0=Eco, 2=Comfort |
| 3070 | Buffer Heat/Cool | write-raw | `"00"`=heating, `"01"`=cooling |

### Zusaetzliche Status-DIDs (Community-Thread)

| DID | Name | Hinweise |
|-----|------|----------|
| 256 | DeviceIdentification | Enthaelt VIN (Geraete-Identifikation) |
| 2352 | AdditionalElectricHeater | Sub-Item `/PowerState` fuer Heizstab-Status |
| 2852 | FanDuctHeater | Ventilatorringheizung — Zubehoer, nicht serienmässig, Nachruestung moeglich (Thread #29) |
| 354 | PrimaryHeatExchangerBaseHeater | Kondensatwannenheizung — zeigt teils konstant 0 waehrend Abtauung |

### GEFAEHRLICHE DIDs

| DID | Risiko | Sichere Werte |
|-----|--------|---------------|
| **2626** MaxPowerElectricalHeater | **Kompressor-Ausfall bei 1-3999W** | Nur 0, 4000, 5400, 8000 W |
| 875 LegionellenZeit | MQTT-Write crasht Bridge ~10s | CLI-Write funktioniert |
| 1791 | NRC 0x22 bei Write (Vorbedingung nicht erfuellt) | Brenner muss aus sein fuer 3-Wege-Ventil-Umstellung |
| 3336/3337 Hysterese HK2/3 | Write-Timeout (kein NRC) | Nur 3335 (HK1) funktioniert |
| 1415-1422 MixerOperationState | Write-Crash bei gemischter alter/neuer Objektstruktur | Nach Codec-Update tree-Objekte loeschen und neu lesen |

## 5. Empfohlene Poll-Intervalle

| Intervall | DIDs | Kategorie |
|-----------|------|-----------|
| 10s | 2488, 2496, 2346, 381, 1603 | Power, Kompressor, Pumpe |
| 30s | 268, 269, 271, 274, 1415, 396 | Temperaturen, Betriebsarten |
| 300s | 880, 881, 761-767, 691-697 | Heizkurven, Zeitplaene |
| 3600s | 548, 565, 566, 2517, 2526, 2622-2625 | Energiezaehler, COP |

## 6. HA Entity-Mapping

| DID-Typ | HA Entity | device_class | state_class |
|---------|-----------|-------------|-------------|
| Temperatur (268, 269, ...) | sensor | temperature | measurement |
| Druck (322, 325) | sensor | pressure | measurement |
| Leistung (2488, 2496) | sensor | power | measurement |
| Energie (548, 565, ...) | sensor | energy | total_increasing |
| Pumpe State (381) | binary_sensor | - | - |
| DHW-Sollwert (396) | number | temperature | - |
| Betriebsart (1415) | climate | - | - |
| QuickMode (1006) | switch | - | - |
| Ventil (2735) | sensor (enum) | - | - |

## 7. Bekannte Bugs in open3e

1. **Write-Rueckgabewerte nach /dev/null** in Listener-Mode (#293)
2. **DID 2626 Firmware-Bug**: Werte 1-3999W → Kompressor-Ausfall (#205)
3. **DID 875 MQTT-Write crasht Bridge** ~10s (#298)
4. **DID 1415 Enum falsch**: Wert 6 = EnergySaving-Reduced, nicht "Antifreeze"
5. **JSON-Write Feld-Reihenfolge relevant**: `{"Mode":1,"State":0}` funktioniert, umgekehrt nicht
6. **DID 1603 (VX3)**: 4 Bytes alt vs 12 Bytes neu (Firmware-abhaengig)
7. **DID 2580**: War O3EInt8, korrekt O3EInt16 scale=10 (Fix in v0.5.x)

## 8. NRC (Negative Response Codes)

| NRC | Bedeutung | Typische Ursache |
|-----|-----------|------------------|
| 0x22 | Conditions not correct | Vorbedingung nicht erfuellt (z.B. Brenner muss aus sein) |
| 0x31 | Request out of range | Wert ausserhalb des erlaubten Bereichs |
| 0x33 | Security access denied | Seed&Key erforderlich (geschuetzte DIDs) |

**Seed&Key**: Viessmann-Sicherheitsmechanismus der kritische Parameter schuetzt. Wird von open3e nicht implementiert.

## 9. Alternative Tools und Koexistenz

| Tool | Plattform | Protokoll | Besonderheiten |
|------|-----------|-----------|----------------|
| **open3e** | Linux/Raspi | UDS (aktives Polling) | Standard-Tool, MQTT, CLI |
| **ioBroker.e3oncan** | ioBroker | CAN passiv + UDS | Ersetzt open3e komplett, "Collect"-Funktion, liest E380 |
| **Cannelloni light** | ESP32 | CAN-to-WiFi | Arduino IDE noetig, WiFi-Config eincompiliert |
| **ViCare API** | Cloud | Internet | Parallel zu open3e nutzbar, weniger Datenpunkte |

**Wichtig:** open3e und ViCare koennen parallel betrieben werden ohne Konflikte.

**E380 Energiezaehler**: Spricht kein UDS — muss mit e3oncan (passives CAN-Listening) gelesen werden, nicht mit open3e.

## 10. Service 0x77 (Experimental)


- Nur internes CAN, nicht DoIP
- ECU-Adresse = Target + 2 (z.B. 0x680 → 0x682)
- 100ms Sleep nach Write erforderlich
- Noetig fuer geschuetzte DIDs (z.B. 3336/3337)
- Modes: `write-sid77`, `write-raw-sid77`

## 11. SmartGrid-Funktion (PV-Ueberschuss)

### Aktivierung und Kontakte

- **Parameter 2560.0**: SmartGrid aktivieren (bei Inbetriebnahme oder nachtraeglich) (Thread #11)
- **Kontakte**: 143.4 (A) und 143.5 (B) an WP-Regelung, potentialfrei ueber Schuetz gegen 143.1

### 4 Modi

| Modus | Kontakte | Funktion |
|-------|----------|----------|
| Normal | keiner geschlossen | Normalbetrieb |
| EVU-Sperre | A geschlossen | Verdichter AUS, Durchlauferhitzer je nach Param 2544 |
| Sollwert-Anhebung | B geschlossen | Angepasste Sollwerte, Verdichter bei Bedarf, Zeitphase noetig |
| Max-Betrieb | A+B geschlossen | Max-Temperaturen, Verdichter sofort, keine Zeitphase noetig |

### Relevante Parameter (Thread #11)

| Parameter | Funktion |
|-----------|----------|
| 2543.0 | SmartGrid Sollwertanhebung Raumtemperatur |
| 2543.1 | SmartGrid Sollwertanhebung Raumkuehlung |
| 2543.2 | SmartGrid Sollwertanhebung Trinkwassererwaermung |
| 2543.3 | SmartGrid Sollwertanhebung Heizwasser-Pufferspeicher |
| 2543.4 | SmartGrid Sollwertabsenkung Kuehlbetrieb Pufferspeicher |
| 2544 | Freigabe Heizwasser-Durchlauferhitzer bei EVU-Sperre |
| 1192.1-1195.1 | Max. VL-Temperatur HK1-4 (fuer Modus 4) |
| 504.4 | Max. Warmwassertemperatur (fuer Modus 4) |
| 2409.0-2412.0 | Min. VL-Temperatur Kuehlung HK1-4 (fuer Modus 4) |

### PV-Ueberschuss-Steuerung ohne SmartGrid (Thread #28)

**Sollwert-Delta-Ansatz** (Software-Loesung via open3e/MQTT):
- Grosse Differenz Ist/Soll → hohe Verdichterleistung
- Kleine Differenz → niedrige Verdichterleistung
- Standardverfahren fuer PV-optimierte Steuerung ueber HA/Node-RED

**Untere Modulationsgrenze** (Vitocal 250-A):
- Datenblatt: 2.8 kW thermisch
- Praxis: Tatsaechliche Grenze ist **AT-abhaengig** und hoeher als angegeben (Thread #28)
- Bei ueberdimensionierter WP: Takten statt Modulieren
- **Risiko bei zu niedriger Drehzahl**: Weniger Schmierung → Kompressorschaden

## 12. Modbus/TCP (Wago Gateway)

### Uebersicht

- Offizielle Viessmann-Loesung: **Wago MB/TCP-Gateway** mit CAN-Karte 750-658 (Thread #26)
- Kosten: **600-1000+ EUR** vs. USB-CAN-Adapter ca. 35 EUR (Thread #15, #26)
- Viessmann supportet **keine DIY-Loesung** mit eigener Wago-Steuerung (Thread #15)
- Community-Konsens: CAN-Bus via open3e ist deutlich besser (mehr Datenpunkte, guenstiger)

### Bekannte Register

| Register | Funktion | Hinweis |
|----------|----------|---------|
| IN-30022 | Warmwasser-Isttemperatur | Kann nach FW-Update verschwinden (Thread #27) |

### Einschraenkungen (Thread #26, #27)

- Dokumentation mangelhaft (Datentypen, Registerlaenge fehlen)
- Nicht alle dokumentierten Register funktionieren
- **FW-Updates verschieben/entfernen Register** ohne Ankuendigung
- Fehlerwert 3276.8°C = 0x7FF8 (NaN/ungueltige Adresse)
- CAN-Bus/UDS-DIDs sind stabiler als Modbus-Register

## 13. Optolink-Geraete und OptolinkVs2-Switch

### OptolinkVs2-Switch (Thread #23)

Open-Source-Loesung fuer aeltere Viessmann-Geraete mit Optolink-Schnittstelle:
- **Parallelbetrieb** Vitoconnect + lokaler Zugriff (Garantieerhaltung)
- MQTT + TCP/IP Anbindung
- Python auf Raspberry Pi (ab Pi 2 ausreichend)
- Unterstuetzt VS2- und KW-Protokoll
- GitHub: philippoo66/optolink-splitter

### Vitoconnect Einschraenkungen (Thread #22, #24)

- **Kein lokaler Zugriff** auf Vitoconnect vorgesehen (offizielle Viessmann-Position)
- Kommunikation Vitoconnect ↔ Cloud ist verschluesselt
- Alternative: Vitogate (800-1000 EUR, Modbus/KNX)
- VX3 Hybrid-Wechselrichter: **Nur Cloud-Zugriff**, keine lokale Datenabfrage moeglich (Thread #33)
- PV-Solardaten via API **kostenpflichtig** (ca. 8 EUR/Monat) (Thread #21)

## 14. §14a StVE (Steuerbare Verbrauchseinrichtung)

- Ab 2025: Netzbetreiber kann steuerbare Verbrauchseinrichtungen dimmen (§14a EnWG) (Thread #30)
- **Vitocal 250 Pro** (Nachfolger): Erweiterte Elektronik fuer StVE angekuendigt
- Bestehende 250-A: Unklar ob FW-Update genuegt oder externe Hardware noetig
- DID 3358 `ElectricalActivePowerConsumptionLimit` (FW v2440): Moeglicherweise fuer StVE relevant
- Leistungssteuerung via CAN/open3e koennte StVE-Anforderungen abdecken

## 15. Firmware v2440 neue DIDs (vs v2417)

3358 ElectricalActivePowerConsumptionLimit (§14a),
2934 CurrentElectricalSystemPowerSetpoint,
2935 CurrentSystemState,
2575 RefrigerationCycleApplicationState,
2580 CompressorSetpointRps,
2850 InstalledHeater Flag,
3327-3328 EEBUS Heartbeat,
3362 PowerLimitFailsafe,
3366 PowerStatusReport
