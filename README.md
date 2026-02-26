# Open3E Home Assistant Bridge

> **⚠ Not production ready** — work in progress, expect breaking changes.

Generates Home Assistant MQTT Discovery from Open3E MQTT topics. No manual HA YAML needed: entities appear automatically based on datapoint mappings in YAML.

## Quick Start
- Test mode (prints and publishes to `test/homeassistant/...`):
  - `python bridge.py --test`
- Simulate messages from file:
  - `python bridge.py --test --simulate test_device.txt`
- Real broker with default discovery prefix:
  - `python bridge.py --mqtt-host 127.0.0.1`
- Custom discovery prefix (e.g., for multiple instances):
  - `python bridge.py --discovery-prefix ha_discovery`
 - Validate configuration files and exit:
   - `python bridge.py --validate-config`
 - Cleanup retained discovery for open3e entities:
   - `python bridge.py --cleanup`

## Structure
- `config/datapoints.yaml`: Maps DIDs and sub-items to HA entity types, writeability, and templates.
- `config/templates/types.yaml`: Reusable type templates (sensor/number/select/binary_sensor).
- `config/translations/{de,en}.yaml`: Localized names.
- `generators/`: Message parsing and discovery builders.
- `bridge.py`: MQTT client loop and publishing with retain.

## Examples
- Flow temperature (268) with sub-items: `open3e/680_268_FlowTemperatureSensor/Actual` → Sensor entity.
- HK1 mode select (1415 `Mode/ID`): creates a Select with options off/auto and Jinja `command_template`.
- HK1/2 pump setpoints (1102/1103): Number entities with min/max/step and write-raw templates.

## Notes
- Discovery includes availability: `open3e/LWT` (online/offline).
- Bridge republishes discovery only when the payload changes (reduced churn).
- To extend, add more DIDs to `datapoints.yaml` and, if needed, small templates in `types.yaml`.
- Device identifiers: if a serial is seen on DID 377 (IdentNumber), it is used as primary device identifier (along with ECU address) so entities group under the same device in Home Assistant.

## Migration Checklist
- Identify topics: capture `open3e/<ECU>_<DID>_<Name>[/Sub]` from your system.
- Map DIDs: add entries in `config/datapoints.yaml` with a suitable `type` from `templates/types.yaml`.
- Sub-items: for values like `/Actual`, `/Minimum`, `/Mode/ID`, define under `subs:` with `entity_type` if needed.
- Writable values: set `writable: true` and a `command_template` (Jinja) that emits an Open3E JSON command to `open3e/cmnd`.
- Naming: add `name_key` and provide translations in `config/translations/de.yaml` and `en.yaml`.
- Validate: `python bridge.py --validate-config` to catch mistakes early.
- Simulate: `python bridge.py --test --simulate test_device.txt` and inspect generated discovery topics.
- Cleanup and retest: `python bridge.py --cleanup` to clear old retained configs before re-simulating.
