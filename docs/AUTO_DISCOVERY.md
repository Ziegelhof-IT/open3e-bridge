# Auto-Discovery

The Open3E Bridge can automatically create Home Assistant entities for DIDs (Data Identifiers) that are not explicitly configured in `datapoints.yaml`.

## How It Works

The bridge uses a 2-tier discovery system:

1. **Tier 2 (YAML)** — DIDs configured in `datapoints.yaml` always get precise entity configuration with correct units, device classes, and write support. This is the default and most accurate path.

2. **Tier 1 (Heuristic)** — When `--auto-discover` is enabled, unknown DIDs are analyzed by a pattern-matching engine that infers entity type, unit, and device class from the DID name in the MQTT topic.

YAML configuration always takes precedence over heuristic inference.

## Enabling Auto-Discovery

```bash
# Enable heuristic auto-discovery
open3e-bridge --auto-discover --mqtt-host mqtt.local

# Combine with other options
open3e-bridge --auto-discover --language de --mqtt-host mqtt.local
```

## What Gets Inferred

The heuristic engine matches DID names against known patterns:

| DID Name Pattern | Entity Type | Unit | Device Class |
|-----------------|-------------|------|-------------|
| `*Temperature*` | sensor | degC | temperature |
| `*Pressure*` | sensor | bar | pressure |
| `*Power*` | sensor | W | power |
| `*Energy*` | sensor | kWh | energy |
| `*Pump*Status*` | binary_sensor | — | power |
| `*Pump*` | sensor | % | power_factor |
| `*Setpoint*` | number | — | — |
| `*Mode*` | sensor | — | — |
| `*Speed*` | sensor | rpm | — |
| (unrecognized) | sensor | — | — |

## Entity Naming

Auto-discovered entities use the format: `DID {number} {name}` (e.g., "DID 1234 FlowTemperatureSensor Actual"). These names are not translated.

## Limitations

- **Read-only**: Heuristic entities cannot determine writability, so no `command_topic` is generated. Use `datapoints.yaml` for writable entities.
- **No command templates**: Write commands require explicit YAML configuration.
- **Approximate accuracy**: Pattern matching infers ~48% of entity types and ~30% of units correctly. For critical sensors, add them to `datapoints.yaml`.
- **No sub-item structure**: Each MQTT topic becomes one flat entity.

## Monitoring

Auto-discovered entity count is included in bridge diagnostics:

```bash
# Enable diagnostics publishing
open3e-bridge --auto-discover --diagnostics-interval 60
```

The `open3e/bridge/diagnostics` MQTT topic includes:

```json
{
  "auto_discovered_entities": 15,
  "discovery_published": 42,
  ...
}
```

## Recommended Workflow

1. Start with `--auto-discover` to see all available DIDs as entities in Home Assistant
2. Identify which entities are useful
3. Add those DIDs to `datapoints.yaml` with proper configuration (unit, device class, write support)
4. Optionally disable `--auto-discover` once all needed DIDs are configured
