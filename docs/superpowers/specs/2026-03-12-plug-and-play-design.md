# Open3E Bridge v1.1: Full Plug & Play Design

## Goal

Replace the ViCare app completely for Home Assistant users. Four layers:
1. Complete German translation (all entity names, modes, sub-items)
2. Writable entities for presets, heating curve, schedules, holiday mode
3. HA Blueprints with auto-import of device settings
4. HA Add-on for 1-click installation

## Layer 1: Complete German Translation

### Problem
~80% translated. Missing: climate modes (off/heat/cool/auto), water heater modes, sub-item names (Comfort/Standard/Reduced), bridge system entities, schedule display strings.

### Changes

**config/translations/de.yaml** — add:
```yaml
modes:
  "off": "Aus"
  "heat": "Heizen"
  "cool": "Kuehlen"
  "auto": "Automatik"
  "eco": "Eco"
  "performance": "Leistung"

sub_items:
  "Comfort": "Komfort"
  "Standard": "Standard"
  "Reduced": "Reduziert"
  "Increased": "Erhoet"
  "Duration": "Dauer"

suffixes:
  # existing suffixes stay, add:
  "setpoint": "Sollwert"
  "hours": "Stunden"
  "starts": "Starts"

value_templates:
  # existing 2335/2350 stay, add translations for error_list:
  257: >
    {% set data = value_json if value_json is mapping else {} %}
    {% set count = data.get('Count', 0) | int(0) %}
    {% if count == 0 %}Keine Fehler{% else %}{{ count }} aktiv{% endif %}
  265: >
    {% set data = value_json if value_json is mapping else {} %}
    {% set count = data.get('Count', 0) | int(0) %}
    {% if count == 0 %}Keine Fehler{% else %}{{ count }} aktiv{% endif %}

schedule_strings:
  "inactive": "Inaktiv"
```

**generators/base.py** — add methods:
- `translate_mode(mode_key: str) -> str` — look up `modes` section in translations
- `translate_sub_item(sub_item: str) -> str` — look up `sub_items` section

**generators/homeassistant.py** — modify:
- `_generate_typed_discovery()`: translate sub-item display names using `translate_sub_item()`
- `_build_entity_config()`: when `options` present in config, translate each option via `translate_mode()` for `language != "en"`
- Climate discovery: translate `modes` list via `translate_mode()`
- Water heater discovery: translate `modes` list via `translate_mode()`
- Mode state/command templates: adjust to use translated mode strings (critical: command templates must map translated names back to raw values)
- Schedule value_templates: use `schedule_strings` translations for "inactive"

**CRITICAL**: Command templates (select, climate, water_heater) must accept BOTH translated and English mode names for robustness. HA sends back whatever the options list contains.

### Tests (tests/test_translations_complete.py)
- All configured entity names have German translation
- Climate modes are German when language=de
- Water heater modes are German when language=de
- Select options are German when language=de
- Sub-items (Comfort/Standard/Reduced) are German when language=de
- Command templates with translated modes render correctly
- Error list value_templates use German strings

## Layer 2: Writable Entities

### 2a: Room Temperature Presets (DID 424/426)

Currently read-only `temperature_sensor` with subs Comfort/Standard/Reduced.

**Change in vitocal.yaml**: DID 424/426 type → `temperature_setpoint` (or keep `temperature_sensor` but make subs writable)

Better approach: Keep type as `temperature_sensor` but make each sub a writable `number` entity:

```yaml
424:
  type: "temperature_sensor"
  name: "Circuit 1 Room Setpoint"
  device: "mixer"
  subs:
    Comfort:
      entity_type: "number"
      writable: true
      min: 3
      max: 37
      step: 0.5
      unit_of_measurement: "°C"
      icon: "mdi:thermometer-plus"
      command_template: >
        {% set val = (value | float * 10) | int %}
        {% set com = '%02x' % (val % 256) + '%02x' % (val // 256) %}
        {% set sta_raw = states('sensor.open3e_680_424_standard') | float(19) * 10 | int %}
        {% set sta = '%02x' % (sta_raw % 256) + '%02x' % (sta_raw // 256) %}
        {% set red_raw = states('sensor.open3e_680_424_reduced') | float(17) * 10 | int %}
        {% set red = '%02x' % (red_raw % 256) + '%02x' % (red_raw // 256) %}
        {% set cmd = {'mode': 'write-raw', 'data': [[424, com + sta + red + '000000']]} %}
        {{ cmd | to_json }}
    Standard:
      entity_type: "number"
      writable: true
      min: 3
      max: 37
      step: 0.5
      unit_of_measurement: "°C"
      icon: "mdi:thermometer"
      command_template: >
        (similar pattern, reading Comfort+Reduced from state, encoding Standard)
    Reduced:
      entity_type: "number"
      writable: true
      min: 3
      max: 37
      step: 0.5
      unit_of_measurement: "°C"
      icon: "mdi:thermometer-minus"
      command_template: >
        (similar pattern, reading Comfort+Standard from state, encoding Reduced)
```

Same pattern for DID 426 (Circuit 2).

**O3EComplexType encoding**: 9 bytes = Comfort(Int16 scale=10) + Standard(Int16 scale=10) + Reduced(Int16 scale=10) + Increased(Int16) + Duration(1 byte). We write all 9 bytes, keeping Increased=0x0000 and Duration=0x00 as-is.

### 2b: Heating Curve Eco Limits (DID 2426/2427)

Currently read-only `temperature_sensor`. Make writable.

O3EComplexType(6): State(Bool,1) + OutsideTemperatureLimit(Int16,2) + Unknown(ByteVal,1) + RoomTemperatureLimit(Int16,2)

```yaml
2426:
  type: "temperature_sensor"
  name: "Eco Heating Limit"
  device: "indoor"
  subs:
    OutsideTemperatureLimit:
      entity_type: "number"
      writable: true
      min: -20
      max: 40
      step: 1
      unit_of_measurement: "°C"
      icon: "mdi:thermometer-low"
      command_template: >
        {% set state = 1 %}
        {% set outside = (value | float * 10) | int %}
        {% set room_raw = states('sensor.open3e_680_2426_roomtemperaturelimit') | float(20) * 10 | int %}
        {% set cmddata = '%02x' % state + '%02x' % (outside % 256) + '%02x' % (outside // 256) + '00' + '%02x' % (room_raw % 256) + '%02x' % (room_raw // 256) %}
        {% set cmd = {'mode': 'write-raw', 'data': [[2426, cmddata]]} %}
        {{ cmd | to_json }}
    RoomTemperatureLimit:
      entity_type: "number"
      writable: true
      min: 10
      max: 35
      step: 0.5
      unit_of_measurement: "°C"
      icon: "mdi:thermometer-high"
      command_template: >
        (similar, reading OutsideTemperatureLimit from state)
```

Same for DID 2427 (Cooling).

### 2c: Schedule Writing via Bridge MQTT Topic

Schedules (DIDs 691-697 WW, 761-767 HK1) are O3EList with 8 schedule entries max per day.

**New bridge feature**: Subscribe to `open3e/bridge/schedule/write` topic.

Payload format:
```json
{
  "did": 691,
  "schedules": [
    {"start": "06:00", "stop": "22:00", "mode": 1},
    {"start": "23:00", "stop": "23:30", "mode": 1}
  ]
}
```

Bridge converts to open3e write command:
```json
{"mode": "write", "data": [[691, {"Count": 2, "Schedules": [{"Start": "06:00", "Stop": "22:00", "Unknown": "0000", "Mode": 1}, ...]}]]}
```

**bridge.py changes**:
- Subscribe to `open3e/bridge/schedule/write` in `_on_connect()`
- New method `_handle_schedule_write(payload)` — validates, converts, publishes to `open3e/cmnd`
- Validation: HH:MM format, max 8 schedules, valid DID range

### 2d: Holiday Mode (DID 511/512)

RawCodec(8) — 8 bytes. Structure likely: Year(1)+Month(1)+Day(1)+Year(1)+Month(1)+Day(1)+Unknown(2).

**New bridge feature**: Subscribe to `open3e/bridge/holiday/write` topic.

Payload format:
```json
{
  "did": 511,
  "start": "2026-03-20",
  "end": "2026-04-03"
}
```

Bridge encodes dates as bytes and writes via write-raw.

**Known limitation**: Byte structure is reverse-engineered, not officially documented. If encoding proves wrong, the bridge logs a warning and doesn't write.

### Tests for Layer 2

**tests/test_discovery_presets.py**:
- DID 424 Comfort sub generates number entity
- DID 424 Standard/Reduced likewise
- Each has command_topic, command_template, min/max/step
- German names (Komfort/Standard/Reduziert) in de mode
- DID 426 same pattern

**tests/test_discovery_heating_curve.py**:
- DID 2426 OutsideTemperatureLimit generates writable number
- DID 2426 RoomTemperatureLimit likewise
- DID 2427 same

**tests/test_command_templates.py** (extend):
- DID 424 Comfort=21.0 → correct hex (d200 for 210 LE)
- DID 2426 OutsideTemperatureLimit=15 → correct hex

**tests/test_schedule_write.py**:
- Bridge accepts schedule/write topic
- Converts to correct open3e command format
- Validates time format
- Rejects >8 schedules
- Rejects invalid DID

**tests/test_holiday_write.py**:
- Bridge accepts holiday/write topic
- Correct date→bytes encoding
- Validates date format
- Rejects past dates

## Layer 3: HA Blueprints + Auto-Import

### 3a: Schedule Sync Blueprint (blueprints/automation/schedule_sync.yaml)

```yaml
blueprint:
  name: "Open3E Zeitprogramm Synchronisation"
  description: "Synchronisiert einen Home Assistant Zeitplan-Helfer mit dem Zeitprogramm der Heizung"
  domain: automation
  input:
    schedule_helper:
      name: "Zeitplan-Helfer"
      description: "Der HA Schedule-Helfer der synchronisiert werden soll"
      selector:
        entity:
          domain: schedule
    target_circuit:
      name: "Ziel"
      description: "Welches Zeitprogramm soll geschrieben werden?"
      selector:
        select:
          options:
            - label: "Warmwasser (Mo-So)"
              value: "dhw"
            - label: "Heizkreis 1 (Mo-So)"
              value: "hk1"

trigger:
  - platform: state
    entity_id: !input schedule_helper

action:
  - service: mqtt.publish
    data:
      topic: "open3e/bridge/schedule/write"
      payload_template: >
        (converts HA schedule helper state to bridge format for each day)
```

### 3b: Holiday Mode Blueprint (blueprints/automation/holiday_mode.yaml)

Uses `input_datetime` helpers for start/end date. When today enters range → set heating to reduced + lower DHW temp. When range ends → restore.

### 3c: PV Surplus Blueprint (blueprints/automation/pv_surplus.yaml)

Uses PV power sensor. When above threshold → raise DHW temp. When below → restore.

### 3d: Auto-Import (--export-blueprints CLI)

New CLI command that:
1. Connects to MQTT, reads current schedule DID values
2. Generates HA package YAML with:
   - `schedule` helpers pre-filled with current device schedules
   - `input_datetime` helpers for holiday start/end
   - Blueprint automation instances referencing the helpers
3. Outputs to stdout or file

### Tests for Layer 3

**tests/test_blueprints.py**:
- Each blueprint YAML is valid HA Blueprint format
- Required fields present (blueprint.name, domain, input, trigger, action)
- German descriptions
- Input selectors are valid types

**tests/test_export_blueprints.py**:
- --export-blueprints generates valid YAML
- Schedule values from mock data correctly mapped
- Output is importable HA package format

## Layer 4: HA Add-on

### 4a: addon/config.yaml
```yaml
name: "Open3E Bridge"
version: "1.1.0"
slug: "open3e-bridge"
description: "Verbindet E3 Heizungssteuerungen (Viessmann, Vaillant) mit Home Assistant"
arch:
  - amd64
  - aarch64
  - armv7
startup: application
boot: auto
options:
  mqtt_host: "core-mosquitto"
  mqtt_port: 1883
  mqtt_user: ""
  mqtt_password: ""
  language: "de"
  profile: "auto"
  auto_discover: true
  log_level: "INFO"
schema:
  mqtt_host: str
  mqtt_port: port
  mqtt_user: str?
  mqtt_password: password?
  language: list(de|en)
  profile: list(auto|vitocal|vitodens|common)
  auto_discover: bool
  log_level: list(DEBUG|INFO|WARNING|ERROR)
map:
  - config:rw
```

### 4b: addon/Dockerfile
Multi-arch build, Python 3.12 base, installs open3e-bridge, healthcheck via --validate-config.

### 4c: addon/run.sh
Reads /data/options.json, constructs CLI args, exec open3e-bridge.

### Tests for Layer 4

**tests/test_addon_config.py**:
- config.yaml has all required HA Add-on fields
- Schema matches bridge CLI args
- All architectures listed

**tests/test_addon_run.py**:
- run.sh parses options.json correctly (mock test)
- Missing optional fields get defaults
- Password not logged

## Implementation Order

1. Layer 1: German translations + generator changes + tests
2. Layer 2a+2b: Preset + heating curve writable entities + tests
3. Layer 2c+2d: Schedule + holiday bridge topics + tests
4. Layer 3: Blueprints + auto-import + tests
5. Layer 4: HA Add-on + tests

Each layer: write tests FIRST (TDD), then implement, then verify green.

## Success Criteria

- All existing 415+ tests stay green
- New tests per layer (estimated ~80 new tests)
- pyright 0 errors on production code
- Each layer gets its own commit
- German translation 100% for all configured entities
- No breaking changes to existing entities
