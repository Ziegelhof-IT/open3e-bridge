# Auto-Discovery Design

## Overview

2-tier auto-discovery system: Tier 1 (heuristic) infers entity configuration from DID topic names, Tier 2 (YAML enrichment) provides curated configuration from datapoints.yaml.

## Architecture

```
MQTT Topic: open3e/{ecu}_{did}_{name}/{sub}
                            │
                 ┌──────────┴──────────┐
                 │ datapoints.yaml     │
                 │ lookup by DID       │
                 └──────────┬──────────┘
                     found? │
               ┌────────────┴────────────┐
               │ YES                     │ NO
               │ Use YAML config         │ --auto-discover?
               │ (Tier 2)               │     │
               │                         │  ┌──┴──┐
               │                         │  │ OFF │ → Skip
               │                         │  │ ON  │ → Heuristic (Tier 1)
               │                         │  └─────┘
               └────────────┬────────────┘
                            │
                    Discovery Payload
```

## Tier 1: Heuristic Engine

`generators/heuristics.py` — `infer_entity_config(did_name, sub_item) -> EntityHint`

**Input:** DID name from MQTT topic (e.g., "FlowTemperatureSensor", "CompressorSpeedRPS")
**Output:** EntityHint with entity_type, unit, state_class, device_class, icon

### Pattern Rules (priority order)

| Pattern | entity_type | unit | state_class | device_class |
|---------|-------------|------|-------------|-------------|
| *Temperature* | sensor | degC | measurement | temperature |
| *Pressure* | sensor | bar | measurement | pressure |
| *Power* | sensor | W | measurement | power |
| *Energy* | sensor | kWh | total_increasing | energy |
| *Pump* + *Status*/*State* | binary_sensor | - | - | power |
| *Pump* | sensor | % | measurement | power_factor |
| *Fan* | sensor | % | measurement | - |
| *Valve* + *Position* | sensor | % | measurement | - |
| *Setpoint* | number | (infer) | - | - |
| *Mode* | select | - | - | - |
| *Speed* | sensor | rpm | measurement | - |
| *Status*/*State* | sensor | - | - | - |
| Default | sensor | - | - | - |

### Limitations

- Topic-name-based only — no access to codec data or raw byte interpretation
- Cannot distinguish writable from read-only DIDs
- Cannot infer command_templates
- Accuracy ~48% for type inference, ~30% for unit inference

## Tier 2: YAML Enrichment

Existing `datapoints.yaml` configuration. YAML always wins over heuristic.

## ECU Device Inference

`generators/heuristics.py` — `infer_device(ecu_addr) -> DeviceHint`

Maps known ECU addresses to device info:

| ECU | Device | Role |
|-----|--------|------|
| 0x680 | HPMU/Main Controller | Primary heat pump controller |
| 0x684 | HMI/Display | User interface |
| 0x68C | VCMU/Outdoor | Refrigerant circuit management |
| 0x68F | BMCU/Battery | Battery management (VX3) |
| 0x6C2 | Inverter | PV/Grid inverter (VX3) |
| 0x6CF | EHCU/Aux Heater | Electric auxiliary heater |
| 0x6C3/0x6C5 | Gateway | Viessmann cloud backend |

Fallback: "Unknown ECU {addr:03X}"

## API Contracts

### EntityHint (dataclass)

```python
@dataclass
class EntityHint:
    entity_type: str          # sensor, number, binary_sensor, select
    device_class: str | None  # HA device_class
    unit: str | None          # unit_of_measurement
    state_class: str | None   # measurement, total_increasing
    icon: str | None          # mdi:icon-name

@dataclass
class DeviceHint:
    name: str                 # Device display name
    model: str | None         # Model identifier
    role: str | None          # Functional role description
```

### Integration Points

- `HomeAssistantGenerator.generate_discovery_message()` — calls heuristic fallback when DID not in YAML and --auto-discover is active
- `BaseGenerator.get_datapoint_config()` — returns None for unknown DIDs (triggers heuristic path)
- `Open3EBridge.__init__()` — accepts `auto_discover: bool` flag

## CLI

`--auto-discover` flag (default: OFF)

When enabled:
- All open3e MQTT topics generate entities
- Heuristic names: "DID {did} {name}" (not translated)
- Diagnostics includes `auto_discovered_entities` counter
