# Configuration Reference

## datapoints.yaml

The main configuration file maps Open3E DIDs to Home Assistant entities.

### Top-level keys

| Key | Type | Description |
|-----|------|-------------|
| `schema_version` | int | Schema version (currently 1) |
| `devices` | dict | Device definitions for HA device grouping |
| `datapoints` | dict | DID-to-entity mappings |
| `device_identification_dids` | dict | DIDs used for device auto-detection |
| `device_patterns` | list | Regex patterns for model identification |
| `default_device` | dict | Fallback device info |
| `write_blacklisted_dids` | list | DIDs that must not be written |
| `ignored_dids` | list | DIDs to skip entirely |

### Device definition

```yaml
devices:
  indoor:                              # Device key (referenced by datapoints)
    name: "Vitocal 252-A Indoor Unit"  # Display name in HA
    model: "Vitocal 252-A"             # Model shown in HA device info
```

### Datapoint definition

```yaml
datapoints:
  268:                                 # DID number
    type: "temperature_sensor"         # Type template name from types.yaml
    name: "Flow Temperature"           # English canonical name
    device: "indoor"                   # Device key from devices section
    icon: "mdi:thermometer"            # Optional icon override
    subs:                              # Sub-item filter
      Actual: { suffix: "current" }    # Only create entity for this sub-item
```

### Sub-item configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `suffix` | str | sub name | Display suffix (translated) |
| `enabled` | bool | true | Disable entity for this sub |
| `entity_type` | str | from template | Override entity type |
| `writable` | bool | false | Enable write commands |
| `min` / `max` / `step` | number | - | Range for number entities |
| `unit_of_measurement` | str | from template | Unit override |
| `icon` | str | from template | Icon override |
| `command_template` | str (Jinja2) | auto | Write command template |

### Writable entities

```yaml
  396:
    type: "temperature_setpoint"
    name: "DHW Setpoint"
    device: "tank"
    min: 10                    # Minimum value for slider
    max: 65                    # Maximum value
    step: 0.5                  # Step size
    writable: true             # Enables command_topic in discovery
    write_mode: "write"        # "write" (JSON value) or "write-raw" (hex)
```

Auto-generated command template for number entities:
```json
{"mode": "write", "data": [[396, {{ value | float }}]]}
```

### Custom command templates (Jinja2)

For raw writes or complex commands:

```yaml
    command_template: >
      {% set intvalue = value | int %}
      {% set cmddata = '%02x' % (intvalue % 256) + '%02x' % (intvalue // 256) %}
      {% set cmd = {'mode': 'write-raw', 'data': [[1102, cmddata]]} %}
      {{ cmd | to_json }}
```

Available Jinja2 variables: `value` (the value to write).

### Value templates (state mapping)

Map numeric values to human-readable strings:

```yaml
    value_template: >
      {% set state = value | int %}
      {% if state == 0 %}Heating
      {% elif state == 1 %}Defrost
      {% elif state == 2 %}DHW
      {% else %}{{ value }}{% endif %}
```

### Climate entities

Heating circuit climate control (multi-DID):

```yaml
  1415:
    type: "select_mode"
    climate:
      name: "Heating Circuit 1"
      trigger_sub: "Mode/ID"           # Sub-item that triggers climate discovery
      modes: ["off", "auto"]
      temperature_did: 1643            # DID for temperature setpoint
      temperature_did_name: "MixerOneCircuitCurrentTemperatureSetpoint"
      min_temp: 3
      max_temp: 37
      precision: 1.0
      temperature_unit: "C"
      mode_state_template: "..."       # Jinja2 template for mode state
      mode_command_template: "..."     # Jinja2 template for mode command
      temperature_command_template: "..." # Jinja2 template for temp command
```

### Water heater entities

DHW water heater control (multi-DID, experimental):

```yaml
  531:
    type: "generic_sensor"
    water_heater:
      name: "Hot Water"
      trigger_did: 531                     # DID that triggers water_heater discovery
      current_temperature_did: 271         # DID for current temperature
      current_temperature_did_name: "DomesticHotWaterSensor"
      current_temperature_sub: "Actual"    # Sub-item for current temp
      temperature_did: 396                 # DID for temperature setpoint
      temperature_did_name: "DomesticHotWaterTemperatureSetpoint"
      modes: ["off", "eco", "performance"]
      min_temp: 10
      max_temp: 60
      precision: 0.5
      temperature_unit: "C"
```

## types.yaml

Reusable entity type templates. Each defines HA discovery fields:

| Template | HA Type | device_class | unit | state_class |
|----------|---------|-------------|------|-------------|
| `temperature_sensor` | sensor | temperature | degC | measurement |
| `pressure_sensor` | sensor | pressure | bar | measurement |
| `power_sensor` | sensor | power | W | measurement |
| `energy_sensor` | sensor | energy | kWh | total_increasing |
| `pump_sensor` | sensor | power_factor | % | measurement |
| `generic_sensor` | sensor | - | - | - |
| `temperature_setpoint` | number | temperature | degC | - |
| `select_mode` | select | - | - | - |
| `binary_onoff` | binary_sensor | power | - | - |
| `switch_toggle` | switch | - | - | - |
| `button_action` | button | - | - | - |
| `water_heater` | water_heater | - | degC | - |

## translations/de.yaml

German translation overlay. Sections:

| Section | Purpose |
|---------|---------|
| `names` | Entity name translations (EN -> DE) |
| `suffixes` | Sub-item suffix translations (current, min, max, ...) |
| `devices` | Device name translations |
| `strings` | Misc strings (suggested_area) |
| `value_templates` | Per-DID state value translations (Jinja2) |
