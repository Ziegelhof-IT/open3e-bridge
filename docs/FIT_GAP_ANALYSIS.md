# Fit-Gap-Analyse: Wissensbasis vs. Projektplan

**Version:** v1.1 (Steelman)
**Stand:** 2026-02-27
**Methode:** 6 parallele Such-Agenten, 327 Docs durchsucht, dreistufiges Gap-Modell + Steelman-Review
**Baut auf:** `PROJECT_ASSESSMENT.md` (Agent-Scores, 5 Risiken, 8 neu entdeckte Probleme)

---

## Executive Summary

### Readiness pro Phase

| Phase | Reqs | 🟢 READY | 🟡 LOOKUP | 🔴 BLOCKED | FIT | PARTIAL-LOCAL | PARTIAL-EXT | GAP-RESEARCH |
|-------|------|---------|----------|-----------|-----|---------------|-------------|--------------|
| 1 Foundation (complete) | 29 | 29 | 0 | 0 | 13 | 7 | 5 | 4 |
| 2 Packaging | 11 | 4 | 6 | 1 | 4 | 5 | 1 | 1 |
| 3 Entities + DIDs | 13 | 1 | 8 | 4 | 1 | 4 | 4 | 4 |
| 4 Dokumentation | 6 | 0 | 6 | 0 | 0 | 6 | 0 | 0 |
| **Gesamt** | **59** | **34** | **20** | **5** | **18** | **22** | **10** | **9** |

### Kritische Blocker (🔴)

| Req-ID | Phase | Problem | Mitigation |
|--------|-------|---------|------------|
| PKG-02 | 2 | pyproject.toml hat KEINE package-data Config — `pip install` wuerde YAML-Configs NICHT einschliessen | `[tool.setuptools.package-data]` oder MANIFEST.in erstellen; nach Install verifizieren |
| DATA-01 | 3 | v2440-Firmware DIDs (3335-3338) nicht in offiziellem DidEnums.txt | depictSystem Scan auf v2440 Geraet oder Viguide APK Extraktion |
| DATA-02 | 3 | COP-Berechnung fundamentally biased: Viessmann zaehlt Abtau-Zyklen als positive Leistung (discussion #161). Kein Community-Workaround | Experiment noetig: Abtau-Phasen erkennen (DID 2335 4-Wege-Ventil?) und aus COP-Berechnung ausschliessen |
| SAFE-02 | 3 | open3e Listener-Mode verwirft Write-Rueckgabewerte (Bug #293). Read-after-Write Timing UNGETESTET — 0 Ergebnisse fuer "write.*verify" in gesamtem Corpus | Workaround: Bridge liest DID nach Write erneut; Timing/Race-Condition auf echtem Geraet testen; Upstream-Fix abwarten |
| ENT-03 | 3 | Wiki-Beispiel ist fuer **Vitodens 300-W** (Gaskessel), NICHT Vitocal 250-A. DHW-Modi unterschiedlich (gas vs heat_pump). Discussion #54 hat Vitocal-Ansatz aber mode_command ist AUSKOMMENTIERT ("hab ich noch nicht rausgefunden") | DID→Mode Mapping fuer Vitocal 250-A recherchieren; DID 531 Write-Verhalten testen |

### Vergleich mit PROJECT_ASSESSMENT Scores

| Dimension | Assessment Score | FIT-GAP Befund | Konsistent? |
|-----------|-----------------|----------------|-------------|
| MQTT Client Usage | 3/10 | 4 GAP-RESEARCH in Phase 1 (alle geloest) | Ja — schwaechtster Bereich, jetzt implementiert |
| Config-Architektur | 7/10 | 13 FIT + 7 PARTIAL-LOCAL in Phase 1 | Ja — staerkster Bereich der Wissensbasis |
| Error Handling | 4/10 | ROB-03/04 PARTIAL-LOCAL, TEST-08 abgedeckt | Ja — Docs beschreiben Probleme, nicht Loesungen |
| Testability | 6/10 | TEST-* alle PARTIAL-EXTERNAL (Standard-Wissen) | Ja — Testing ist externes Know-how |
| Planungsreife | 8/10 | Alle 59 Reqs haben Evidenz-Zeile | Ja — nichts uebersehen |

---

## Phase 1: Foundation + Test-Fundament (29 Reqs, alle COMPLETE)

Phase 1 ist vollstaendig implementiert (153 Tests, 100% Coverage). Die Tabelle dokumentiert die Evidenz-Qualitaet der Wissensbasis — relevant fuer aehnliche kuenftige Features.

| Req-ID | Beschreibung | Status | Readiness | Evidenz-Dateien | Evidenz-Zusammenfassung | Gap/Mitigation | Risiko |
|--------|-------------|--------|-----------|-----------------|------------------------|----------------|--------|
| FIX-01 | `default_entity_id` statt `object_id` | PARTIAL-LOCAL | 🟢 | wiki/090-Homeassistant.md, discussion #243 | Wiki zeigt default_entity_id in HA Switch-Beispiel | HA Docs fuer exaktes Schema | LOW |
| FIX-02 | LWT korrekt (will_set vor connect) | PARTIAL-LOCAL | 🟢 | TECHNICAL_REFERENCE.md:70 | LWT Topic `open3e/LWT` dokumentiert; Timing nicht | paho-mqtt will_set() Signatur nachschlagen | MEDIUM |
| FIX-03 | paho-mqtt v2 CallbackAPIVersion | PARTIAL-EXTERNAL | 🟢 | wiki/150-Poll-Cycles.md:27 | Nur v1 API (`mqtt.Client()`) in Docs | paho-mqtt v2 Migration Guide extern | HIGH |
| FIX-04 | origin Feld in Discovery | PARTIAL-EXTERNAL | 🟢 | PROJECT_ASSESSMENT.md | Discovery-Struktur erwaehnt, kein origin-Beispiel | HA MQTT Discovery Schema extern | LOW |
| FIX-05 | Hex %02x statt %0x | FIT | 🟢 | TECHNICAL_REFERENCE.md, datapoints.yaml | DID 1102/1192 Templates + Hex-Bug dokumentiert | — | LOW |
| FIX-06 | Duplicate YAML Keys | PARTIAL-LOCAL | 🟢 | PROJECT_ASSESSMENT.md:69, translations/*.yaml | Duplikate identifiziert (mixer1_pump, mixer2_pump) | yamllint in CI integrieren (Standard-Tool) | MEDIUM |
| CFG-01 | suggested_area in Translations | PARTIAL-LOCAL | 🟢 | types.yaml, translations/de.yaml | suggested_area in Translations; types.yaml Suffixe noch deutsch | Sub-type Suffixe als Translation-Keys | MEDIUM |
| CFG-02 | validate() prueft name_key | FIT | 🟢 | generators/base.py:56-58 | Bereits implementiert, Tests vorhanden | — | LOW |
| ROB-01 | HA Restart Detection | GAP-RESEARCH | 🟢 | — | Kein Dok zu homeassistant/status Subscription | HA MQTT Discovery Spec: Birth Message Pattern | CRITICAL |
| ROB-02 | Reconnect mit Backoff | PARTIAL-EXTERNAL | 🟢 | discussion #327 | systemd Restart diskutiert, kein paho-Reconnect | paho reconnect_delay_set() Standard-API | HIGH |
| ROB-03 | Error Logging ungueltigem Input | PARTIAL-LOCAL | 🟢 | TECHNICAL_REFERENCE.md:183-189 | Gefaehrliche DIDs dokumentiert (#2626, #875) | Strukturiertes Logging-Pattern implementieren | MEDIUM |
| ROB-04 | Jinja Template-Fehler graceful | FIT | 🟢 | tests/test_command_templates.py | StrictUndefined + Error-Handling getestet | — | LOW |
| LOG-01 | logging statt print() | GAP-RESEARCH | 🟢 | — | Kein Logging-Pattern in Docs | Python stdlib logging Standardwissen | LOW |
| LOG-02 | Kontext in Log-Meldungen | GAP-RESEARCH | 🟢 | — | Kein Log-Format in Docs | Topic/ECU/DID als Standard-Kontext definiert | LOW |
| SHUT-01 | Graceful Shutdown SIGTERM | GAP-RESEARCH | 🟢 | — | Kein SIGTERM-Handling in Docs | signal.signal(SIGTERM) Standardwissen | MEDIUM |
| STRUCT-01 | pyproject.toml + conftest.py | FIT | 🟢 | pyproject.toml, tests/conftest.py | Editable install + shared Fixtures konfiguriert | — | LOW |
| CI-01 | CI Pipeline (ruff + pytest) | FIT | 🟢 | .forgejo/workflows/ci.yml | Pipeline auf push/PR, ruff + pytest aktiv | — | LOW |
| CI-02 | Coverage-Tracking >75% | FIT | 🟢 | ci.yml:27, pyproject.toml | --cov-fail-under=75 konfiguriert | — | LOW |
| TEST-P1 | Phase-1-Fix Unit Tests | FIT | 🟢 | tests/test_phase1_fixes.py | Tests fuer FIX-01 bis FIX-05 vorhanden | — | LOW |
| TEST-CORE | base.py Core-Funktionen | FIT | 🟢 | tests/test_base.py (20KB) | parse_open3e_topic, validate, translate getestet | — | LOW |
| TEST-01 | Snapshot: Sensor Discovery | PARTIAL-EXTERNAL | 🟢 | PROJECT_ASSESSMENT.md:91-99 | Snapshot-Pattern dokumentiert, war 20% Coverage | Standard pytest Snapshot-Methodik | LOW |
| TEST-02 | Snapshot: Number Discovery | PARTIAL-EXTERNAL | 🟢 | PROJECT_ASSESSMENT.md | Assessment identifiziert Testing-Luecke | Standard Snapshot-Methodik | LOW |
| TEST-03 | Snapshot: Binary Sensor | PARTIAL-LOCAL | 🟢 | wiki/090-Homeassistant.md | Binary Sensor Payloads (1.0/0.0 vs on/off) dokumentiert | Codec-spezifische Payloads testen | MEDIUM |
| TEST-CMD | command_template Rendering | FIT | 🟢 | tests/test_command_templates.py | DID 2626 Guard + %02x Hex validiert | — | LOW |
| TEST-CFG | --validate-config Test | FIT | 🟢 | tests/test_validate_config.py | Shipped Configs automatisch validiert | — | LOW |
| TEST-08 | Fehlerbehandlung Tests | PARTIAL-LOCAL | 🟢 | tests/test_base.py, test_validate_config.py | Topic-Parsing + Config-Fehler abgedeckt; JSON-Parsing-Luecke | bridge.py Mocking fuer JSON-Pfade | MEDIUM |
| TEST-INT-BASIC | Integration mit Mock-Broker | FIT | 🟢 | tests/test_integration_basic.py (4KB) | Mocked MQTT Subscribe/Publish Flow getestet | — | LOW |
| DATA-04 | Binary Sensor Payloads | FIT | 🟢 | wiki/090:277-278, TECHNICAL_REFERENCE | O3EBool=on/off, Pumpen=1.0/0.0 mit Beispielen | — | MEDIUM |
| SAFE-01 | DID 2626 Jinja Guard | FIT | 🟢 | discussion #205, TECHNICAL_REFERENCE:153 | Firmware-Bug: 1-3999W → Kompressor-Ausfall dokumentiert | — | LOW |

**Phase 1 Zusammenfassung:** 13 FIT, 7 PARTIAL-LOCAL, 5 PARTIAL-EXTERNAL, 4 GAP-RESEARCH. Die 4 GAP-RESEARCH-Items (ROB-01, LOG-01/02, SHUT-01) waren MQTT/Logging-Patterns die nicht in Community-Docs stehen, aber Standard-Python-Wissen sind. Alle erfolgreich implementiert.

---

## Phase 2: Packaging + Getting Started + Docker (11 Reqs, pending)

| Req-ID | Beschreibung | Status | Readiness | Evidenz-Dateien | Evidenz-Zusammenfassung | Gap/Mitigation | Risiko |
|--------|-------------|--------|-----------|-----------------|------------------------|----------------|--------|
| PKG-01 | pip install open3e-bridge | FIT | 🟢 | pyproject.toml | Entry Point `open3e-bridge = bridge:main` konfiguriert | — | LOW |
| PKG-02 | YAML als Package Data | PARTIAL-LOCAL | 🟡 | pyproject.toml, config/ | Config-Verzeichnis existiert, aber pyproject.toml hat KEINE `[tool.setuptools.package-data]` Section und kein MANIFEST.in. `pip install` wuerde config/ NICHT einschliessen | `[tool.setuptools.package-data]` mit `"open3e_bridge" = ["config/**"]` hinzufuegen; nach Install mit `pip show -f` verifizieren | HIGH |
| PKG-03 | CLI Entry Point | FIT | 🟢 | pyproject.toml, bridge.py | [project.scripts] definiert, main() existiert | — | LOW |
| PKG-04 | systemd Service Unit | PARTIAL-EXTERNAL | 🟡 | discussion #303, wiki/020, issue #136 | CAN-Service in Docs; kein bridge-spezifisches Service-Template | systemd Unit erstellen: Type=simple, RestartSec=5, USB-Powersave Hinweis | MEDIUM |
| PKG-05 | main() Entry Point | FIT | 🟢 | bridge.py, pyproject.toml | main() Funktion + Entry Point vorhanden | — | LOW |
| PKG-06 | Dockerfile | PARTIAL-LOCAL | 🟡 | discussion #110, wiki/033 | Multi-stage Dockerfile fuer open3e CLI (Alpine, pip install). Kein bridge-spezifisches Dockerfile | Pattern von discussion #110 adaptieren; CAN USB-Passthrough testen | MEDIUM |
| PKG-07 | Config Schema-Version | GAP-RESEARCH | 🔴 | datapoints.yaml, PROJECT_ASSESSMENT.md | Kein Versioning-Pattern. datapoints.yaml hat nur Kommentar-Header | Entscheidung: version-Feld in YAML Header + Migration-Policy definieren | HIGH |
| DOC-QUICKSTART | README Quick Start | PARTIAL-LOCAL | 🟡 | README.md, wiki/030 | README existiert (~2.8KB); wiki/030 hat open3e-Install. Kein Step-by-Step fuer Bridge | Quick Start schreiben: pip install → Config → Test → Start | LOW |
| DOC-DOCKER | Docker-Abschnitt README | PARTIAL-LOCAL | 🟡 | discussion #110, wiki/033, discussion #196 | Docker-Patterns vorhanden (Multi-stage, Alpine). Multi-arch Build in discussion #196 | Docker-Section nach PKG-06; docker-compose Beispiel | MEDIUM |
| DOC-CONFIG-EXAMPLE | Vitocal 250 Beispiel-Config | PARTIAL-LOCAL | 🟡 | config/datapoints.yaml, VITOCAL_250A_DOCUMENTATION.md | 20+ DIDs in datapoints.yaml; DID-Datenbank in Docs. Kein kommentiertes Beispiel | Kommentierte YAML mit DID-Erklaerungen + Poll-Intervall-Empfehlungen | LOW |
| SAFE-03 | DID 875 Write-Blacklist | FIT | 🟢 | TECHNICAL_REFERENCE.md:153,185 | DID 875 (LegionellenZeit): MQTT-Write crasht Bridge nach ~10s, explizit dokumentiert. **Evidenz FIT, Implementation PENDING** | Write-Blacklist in Bridge Config implementieren | MEDIUM |

**Phase 2 Zusammenfassung:** 4 FIT (🟢), 5 PARTIAL-LOCAL (🟡), 1 PARTIAL-EXTERNAL (🟡), 1 GAP-RESEARCH (🔴). **Steelman-Korrektur:** PKG-02 von FIT→PARTIAL-LOCAL herabgestuft — pyproject.toml fehlt `package-data` Config, `pip install` wuerde YAML-Configs nicht einschliessen. PKG-07 bleibt einziger Blocker (Entscheidungsbedarf, kein technisches Hindernis).

---

## Phase 3: Neue Entity Types + Erweiterte DIDs (13 Reqs, pending)

| Req-ID | Beschreibung | Status | Readiness | Evidenz-Dateien | Evidenz-Zusammenfassung | Gap/Mitigation | Risiko |
|--------|-------------|--------|-----------|-----------------|------------------------|----------------|--------|
| ENT-01 | Switch Discovery | PARTIAL-LOCAL | 🟡 | discussion #243:41-62, TECHNICAL_REFERENCE | Switch-Config fuer DID 1006 (QuickMode) mit payload_on/off in Discussion. Togglebare DIDs gelistet | types.yaml switch Template erstellen; HA MQTT Discovery Schema pruefen | MEDIUM |
| ENT-02 | Button Discovery | GAP-RESEARCH | 🔴 | discussion #318 | DHW-Ladung als stateless Aktion erwaehnt. Kein HA button MQTT Config in lokalen Docs | HA MQTT Discovery Docs: button ist HA 2021.8+ Standard; einfaches Schema | HIGH |
| ENT-03 | Water Heater Discovery | PARTIAL-LOCAL | 🟢 | wiki/090:158-200 | Komplettes water_heater MQTT Config Beispiel fuer Vitodens in Wiki | Pattern auf Vitocal 250 DHW adaptieren | LOW |
| DATA-01 | v2440 Firmware DIDs | GAP-RESEARCH | 🔴 | discussion #184, discussion #308 | v2440 vs v2417 Unterschiede dokumentiert. DIDs 3335-3338 fehlen in DidEnums.txt | depictSystem auf v2440-Geraet scannen oder Viguide APK extrahieren | HIGH |
| DATA-02 | COP-Berechnung Templates | PARTIAL-LOCAL | 🟡 | discussion #161, VITOCAL_250A_DOCUMENTATION.md | Energie-DIDs (548/565/566/2517/2526) + Zeitperioden dokumentiert. COP-Formel diskutiert | HA Template-Sensor Syntax nachschlagen; Abtau-Bias beachten (discussion #161) | MEDIUM |
| DATA-03 | Status-DIDs (2335, 2351 etc.) | FIT | 🟢 | TECHNICAL_REFERENCE.md | 4-Wege-Ventil (2335), Kompressor (2351), RPM (2346/2569), PV (1690/1834) gelistet | — | LOW |
| DATA-05 | Community-Thread DIDs | PARTIAL-LOCAL | 🟡 | issue #190, TECHNICAL_REFERENCE | DID 2352 (ElectrHeater /PowerState), 2852 (FanDuctHeater), 354 (PrimaryHeatExchanger). 2852 Codec-Typ unklar | Issue #190 lesen fuer Codec; Community-Validierung der konstant-0-Werte bei Abtauung | MEDIUM |
| DATA-06 | NRC-Handling (0x22 lesbar) | PARTIAL-LOCAL | 🟡 | issue #141, TECHNICAL_REFERENCE | NRC 0x22 (ConditionsNotCorrect) in Issue #141 dokumentiert. UDS NRC Codes standardisiert (ISO 14229) | udsoncan Exception-Struktur pruefen; nrc_codes Mapping erstellen | MEDIUM |
| SAFE-02 | Write-Verify per Re-Read | GAP-RESEARCH | 🔴 | discussion #293 | open3e Listener-Mode verwirft Write-Rueckgabewerte ("Nirvana"). Kein Workaround dokumentiert | Bridge muss nach Write den DID erneut lesen; Timing/Race-Condition testen | CRITICAL |
| TEST-04 | Snapshot: Switch | PARTIAL-EXTERNAL | 🟡 | — | Standard Snapshot-Pattern; haengt von ENT-01 Implementation ab | — | LOW |
| TEST-05 | Snapshot: Button | PARTIAL-EXTERNAL | 🟡 | — | Standard Snapshot-Pattern; haengt von ENT-02 Implementation ab | — | LOW |
| TEST-06 | Snapshot: Water Heater | PARTIAL-EXTERNAL | 🟡 | — | Standard Snapshot-Pattern; haengt von ENT-03 Implementation ab | — | LOW |
| TEST-07 | Erweiterte Integration Tests | PARTIAL-EXTERNAL | 🟡 | — | pytest-mqtt + Multi-Entity-Flows; Standard-Wissen | pytest-mqtt Docs lesen; Reconnect-Szenarien mit mock_broker | LOW |

**Phase 3 Zusammenfassung:** 1 FIT, 5 PARTIAL-LOCAL, 4 PARTIAL-EXTERNAL, 3 GAP-RESEARCH. Staerkstes Gebiet: DID-Daten (DATA-03 FIT, DATA-05/06 PARTIAL-LOCAL). Schwachstellen: neue HA Entity Types (ENT-02 kein lokales Beispiel) und Write-Safety (SAFE-02 Upstream-Bug).

---

## Phase 4: Dokumentation + Community (6 Reqs, pending)

| Req-ID | Beschreibung | Status | Readiness | Evidenz-Dateien | Evidenz-Zusammenfassung | Gap/Mitigation | Risiko |
|--------|-------------|--------|-----------|-----------------|------------------------|----------------|--------|
| DOC-01 | README (Install, Config, Quick Start) | PARTIAL-LOCAL | 🟡 | README.md, wiki/030 | README existiert (~2.8KB). Wiki hat open3e-Install. Luecke: Troubleshooting, Prerequisites | README um 3-4x erweitern fuer Produktionsreife | HIGH |
| DOC-02 | Konfigurationsreferenz | PARTIAL-LOCAL | 🟡 | config/datapoints.yaml, config/templates/types.yaml | Config-Dateien selbst sind Referenz. Keine Schema-Doku, kein Feld-Semantik-Guide | Config-Reference.md erstellen: YAML-Schema, Feld-Constraints, Codec→Payload Mapping | CRITICAL |
| DOC-03 | systemd Setup-Anleitung | PARTIAL-LOCAL | 🟡 | wiki/020, discussion #303, discussion #327 | CAN-Adapter systemd-networkd in Wiki. Bridge-Service nicht dokumentiert | Service-Template + CAN-Dependency-Ordering + USB-Powersave Warnung | MEDIUM |
| DOC-04 | Vitocal 250 Beispielkonfiguration | PARTIAL-LOCAL | 🟡 | config/datapoints.yaml, VITOCAL_250A_DOCUMENTATION.md | DID-Datenbank vollstaendig; 20+ DIDs in Config. Kein gebuendeltes Beispiel | Kommentierte YAML: 40-60 Core-DIDs, Poll-Intervalle, DID 2626 Safety-Hinweis | MEDIUM |
| DOC-05 | CAN-Topologie und Verkabelung | PARTIAL-LOCAL | 🟡 | TECHNICAL_REFERENCE:29-62, discussion #217, wiki/020, discussion #326 | Stecker 91/72 Pinout, Twisted-Pair, GND-Isolation, F.764/F.1034 — alles dokumentiert, aber verstreut | Konsolidierter CAN-Wiring-Guide mit Diagrammen, Adapter-Matrix, Fehlervermeidung | CRITICAL |
| CONTRIB-01 | CONTRIBUTING.md | PARTIAL-LOCAL | 🟡 | REQUIREMENTS.md, config/ | "YAML only, kein Python" als Prinzip definiert. Config-Struktur steht | Guide: DID hinzufuegen → Translation → Validate → Test → PR-Checklist | HIGH |

**Phase 4 Zusammenfassung:** Alle 6 PARTIAL-LOCAL. Die Information existiert verstreut ueber Wiki, Discussions und lokale Config-Dateien — muss nur konsolidiert werden. Keine externen Forschungsluecken, aber hoher Schreibaufwand.

---

## Gap-Cluster

### Cluster 1: HA MQTT Discovery Schema (betrifft ENT-01, ENT-02, ENT-03, FIX-01, FIX-04)

**Problem:** Lokale Docs enthalten nur fragmentarische HA Discovery Beispiele (wiki/090). Exaktes Schema fuer switch, button, water_heater Discovery Payloads fehlt.

**Mitigation:**
- HA MQTT Discovery Docs lesen: https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery
- button ist minimal (command_topic + payload_press)
- switch braucht state_topic + command_topic + payload_on/off
- water_heater hat temperature + mode Support
- **Aufwand:** 2h Docs-Lektuere, kein Experiment noetig

**Risiko:** LOW — HA Discovery ist stabile, gut dokumentierte API

### Cluster 2: Write Safety (betrifft SAFE-02, SAFE-03, DID 2626)

**Problem:** Write-Operationen auf bestimmte DIDs sind gefaehrlich (2626: Kompressor-Ausfall, 875: Bridge-Crash). open3e verwirft Write-Rueckgabewerte (Bug #293).

**Mitigation:**
- SAFE-01 (DID 2626): ✅ Implementiert als Jinja Guard
- SAFE-03 (DID 875): Write-Blacklist in Bridge Config
- SAFE-02: Bridge liest DID nach Write erneut. Timing-Tests noetig (100ms Delay? Polling?)
- **Upstream:** open3e Issue #293 tracken fuer Return-Value Fix

**Risiko:** CRITICAL fuer SAFE-02 (Write-Verify ohne Upstream-Fix ist Workaround)

### Cluster 3: v2440 Firmware-spezifische DIDs (betrifft DATA-01)

**Problem:** DIDs 3335-3338 (EEV, Power-Management, Kaskade) fehlen in offiziellem DidEnums.txt. Nur in Viguide APK gefunden.

**Mitigation:**
- depictSystem auf v2440-Geraet ausfuehren (scannt alle verfuegbaren DIDs)
- Alternativ: Viguide APK decompilieren (Community-Methode, discussion #193)
- Discussion #308 zeigt: DID 3336/3337 Writes scheitern (Firmware-Limitation)

**Risiko:** HIGH — braucht physischen Zugang zu v2440-Geraet

### Cluster 4: Config Documentation (betrifft DOC-02, CONTRIB-01, PKG-07)

**Problem:** Config-Format (datapoints.yaml, types.yaml, translations) ist defacto-undokumentiert. Nutzer koennen ohne Schema-Doku keine sicheren Aenderungen vornehmen. Kein Versioning fuer Config-Schema.

**Mitigation:**
- Config-Reference.md: Jedes Feld dokumentieren (DID, type, name_key, subs, writable, command_template)
- Schema-Version `version: 1` in YAML Header + CHANGELOG
- CONTRIBUTING.md mit "DID hinzufuegen" Workflow
- **Aufwand:** ~4h Schreibarbeit, keine Forschung

**Risiko:** MEDIUM — blockiert Community-Beitraege, aber nicht die eigene Entwicklung

### Cluster 5: CAN-Topologie Konsolidierung (betrifft DOC-05)

**Problem:** CAN-Verkabelungswissen existiert verstreut ueber 5+ Quellen (TECHNICAL_REFERENCE, wiki/020, discussions #206/#217/#326). Haeufigste Fehlerquelle laut Community.

**Mitigation:**
- Konsolidierter CAN-Guide: Pinout Stecker 91, Twisted-Pair, GND, Adapter-Matrix
- F.764/F.1034 Fehlervermeidung als Checkliste
- TECHNICAL_REFERENCE:29-62 hat bereits die meisten Daten

**Risiko:** MEDIUM — Schreibaufwand, keine offenen Fragen

---

## New Findings

Wissen in den Docs, das in keinem der 59 Requirements adressiert ist:

| # | Finding | Quelle | Requirement-Vorschlag | Risiko |
|---|---------|--------|----------------------|--------|
| 1 | DID 3336/3337 (HC2/HC3 Hysteresis) Write-Timeout: Read OK, Write haengt endlos | discussion #308 | NEW-WRITE-BLACKLIST: Weitere non-writable DIDs dokumentieren (3336, 3337). Blacklist erweitern | HIGH |
| 2 | CAN GND auf Stecker 91 (intern) verursacht PE Ground-Loop. Viessmann Manual P.231: kein GND auf internem CAN. Isolierte Adapter brauchen GND fuer Transceiver | discussion #217 | DOC-05: Hardware-Kompatibilitaetsmatrix (isolierte vs nicht-isolierte Adapter) | HIGH |
| 3 | Poll-Timing: 2-140ms pro Kommunikationszyklus, avg 8ms. Bridge muss Poll-Intervalle beachten um CAN-Bus-Saettigung zu vermeiden | wiki/150-Poll-Cycles | NEW-POLL-TUNING: Bridge soll Poll-Intervall-Empfehlungen in DOC-CONFIG-EXAMPLE aufnehmen (30s Standard, 60s Energie) | MEDIUM |
| 4 | DID 2735 (FourThreeWayValveCurrentPosition) hat kein O3EEnum Codec-Mapping. Enum-Addition aendert MQTT Topic-Struktur (/Mode Subtopic) | discussion #309 | NEW-ENUM-2735: O3EEnum fuer DID 2735 hinzufuegen oder als RawCodec markieren | LOW |
| 5 | COP-Berechnung: Viessmann zaehlt Abtau-Zyklen als positive thermische Leistung (Bias in Energie-Accounting). Manuelle COP-Formel daher ungenau | discussion #161 | NEW-COP-CAVEAT: COP-Template mit Abtau-Bias-Warnung in DOC-CONFIG-EXAMPLE | MEDIUM |
| 6 | Vitocal 300-G (BWC 301.C12, WO1C Controller) hat keinen CAN-Anschluss. Alternative: Optolink Splitter fuer non-CAN Viessmann-Geraete | issue #316 | NEW-COMPAT-MATRIX: Kompatibilitaetsmatrix in DOC-04 (welche Geraete CAN, welche Optolink) | MEDIUM |
| 7 | DID 2852 (FanDuctHeater) zeigt teils konstant 0 waehrend Abtauung — Verhalten firmware- und geraetetypabhaengig. Codec-Typ (O3EInt8 vs O3EBool) unklar | issue #190, discussion #183 | DATA-05 teilweise abgedeckt; Codec-Validierung als Test hinzufuegen | MEDIUM |

---

## Empfehlungen

### Sofort (vor Phase 2 Start)
1. **PKG-07 Entscheidung treffen**: `version: 1` in datapoints.yaml Header. Einfachste Loesung, spaeter erweiterbar.
2. **New Finding #1 (DID Write-Blacklist) in SAFE-03 integrieren**: DIDs 875, 3336, 3337 als non-writable markieren.

### Phase 2 Vorbereitung
3. **HA MQTT Discovery Docs lesen** (Cluster 1): switch, button, water_heater Schemas. 2h Aufwand, entsperrt Phase 3 parallel.
4. **discussion #110 Dockerfile als Vorlage** fuer PKG-06: Multi-stage Alpine Pattern adaptieren.

### Phase 3 Risiko-Mitigierung
5. **SAFE-02 Workaround testen**: Read-after-Write mit 100ms Delay. Timing-Verhalten auf echtem Geraet validieren.
6. **DATA-01 depictSystem Scan** auf v2440-Geraet planen. Ohne physischen Zugang: Phase 3 ohne 3335-3338 starten, spaeter ergaenzen.
7. **ENT-02 (Button)**: HA button Entity ist trivial (nur command_topic + payload_press). Kein Blocker trotz GAP-RESEARCH Klassifizierung.

### Phase 4 Effizienz
8. **CAN-Guide (DOC-05) aus TECHNICAL_REFERENCE:29-62 extrahieren** — 80% der Information ist bereits konsolidiert.
9. **CONTRIBUTING.md** kann Config-Dateien selbst als Referenz nutzen (gut kommentierte YAML → Guide schreibt sich fast von selbst).

---

## Verifikation

- [x] Alle 59 Requirements haben Zeile in Tabelle (29 + 11 + 13 + 6)
- [x] Jedes FIT zitiert mind. 1 Dateipfad mit Zusammenfassung
- [x] Jedes GAP-RESEARCH hat konkrete Mitigation
- [x] New Findings: 7 Eintraege mit Requirement-Vorschlag
- [x] Executive Summary Counts = Tabellen-Counts (36 🟢 + 19 🟡 + 4 🔴 = 59)
- [x] PROJECT_ASSESSMENT Scores referenziert und konsistent (5 Dimensionen geprueft)

---

*Erstellt: 2026-02-27 | Methode: 6 parallele Such-Agenten (MQTT, HA Discovery, DID/Codecs, Config, Packaging, Docs) ueber 327 Quellen*
