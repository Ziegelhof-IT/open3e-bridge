# Open3E Home Assistant Bridge

Generates Home Assistant MQTT Discovery from Open3E MQTT topics. No manual HA YAML needed: entities appear automatically based on datapoint mappings in YAML.

## Quick Start

### 1. Install

```bash
# In a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install open3e-bridge
```

Or install from source:

```bash
git clone https://github.com/open3e/open3e-bridge.git
cd open3e-bridge
pip install .
```

### 2. Run

```bash
# Connect to your MQTT broker (where open3e publishes)
open3e-bridge --mqtt-host <broker-ip> --language de

# With authentication
open3e-bridge --mqtt-host <broker-ip> --mqtt-user mqtt --mqtt-password secret --language de

# Or use MQTT_PASSWORD env var (not visible in process listing)
export MQTT_PASSWORD=secret
open3e-bridge --mqtt-host <broker-ip> --mqtt-user mqtt --language de
```

### 3. Verify

Check Home Assistant: new entities should appear under **Settings > Devices & Services > MQTT**.

### Prerequisites

- **Open3E** running and publishing to MQTT (`open3e @args.txt` with `-m` flag)
- **MQTT broker** (e.g., Mosquitto) reachable from both open3e and HA
- **Home Assistant** with MQTT integration configured

## Architecture

```
 open3e (CAN/DoIP)        MQTT Broker         open3e-bridge          Home Assistant
 ┌──────────────┐        ┌───────────┐        ┌──────────────┐       ┌──────────────┐
 │ Read DIDs    │──pub──>│ open3e/+  │──sub──>│ Parse topics │       │              │
 │ Write DIDs   │<──sub──│ open3e/   │        │ Match config │       │              │
 │              │        │ cmnd      │<──pub──│ Generate     │──pub──│ MQTT         │
 │              │        │           │        │ discovery    │──────>│ Discovery    │
 └──────────────┘        └───────────┘        └──────────────┘       └──────────────┘
                                                     │
                                              config/datapoints.yaml
                                              config/templates/types.yaml
                                              config/translations/de.yaml
```

**Flow:**
1. open3e reads DIDs from the heat pump and publishes values to `open3e/{ecu}_{did}_{name}/{sub}`
2. open3e-bridge subscribes to `open3e/+/+` and `open3e/+`
3. For each message, the bridge matches the DID against `datapoints.yaml`
4. If configured, it generates an HA MQTT Discovery payload and publishes to `homeassistant/{type}/{entity_id}/config`
5. Home Assistant auto-discovers the entity

**Key features:**
- Write verification: after write commands, automatic read-back to verify
- COP calculation: live coefficient of performance from power DIDs
- NRC handling: negative response codes from the controller are logged with human-readable names
- Periodic diagnostics on `open3e/bridge/diagnostics`

## Entity Types

| Type | HA Platform | Example |
|------|-------------|---------|
| `temperature_sensor` | sensor | Flow/Return/Outside temperature |
| `pressure_sensor` | sensor | Water pressure |
| `power_sensor` | sensor | Electrical/thermal power |
| `energy_sensor` | sensor | Energy counters (kWh, total_increasing) |
| `pump_sensor` | sensor | Pump speed (%) |
| `generic_sensor` | sensor | Compressor stats, PV status |
| `temperature_setpoint` | number | DHW setpoint, flow temp limits |
| `select_mode` | select | Operation modes (off/auto) |
| `binary_onoff` | binary_sensor | Frost protection, pump/compressor status |
| `switch_toggle` | switch | Quick mode |
| `button_action` | button | DHW one-time charge |
| `water_heater` | water_heater | DHW control (temp + mode) |
| climate | climate | Heating circuit control |

## Docker

```bash
# Build
docker build -t open3e-bridge .

# Run
docker run --name open3e-bridge \
  open3e-bridge \
  --mqtt-host <broker-ip> --mqtt-user mqtt --mqtt-password secret --language de
```

Docker Compose example:

```yaml
services:
  open3e-bridge:
    build: .
    restart: unless-stopped
    command:
      - --mqtt-host
      - mqtt.local
      - --mqtt-user
      - mqtt
      - --mqtt-password
      - secret
      - --language
      - de
```

## systemd Service

See [docs/SYSTEMD_SETUP.md](docs/SYSTEMD_SETUP.md) for a complete step-by-step guide.

Quick version:

```bash
sudo cp contrib/open3e-bridge.service /etc/systemd/system/
sudo systemctl edit open3e-bridge
# Add ExecStart override with your MQTT credentials
sudo systemctl enable --now open3e-bridge
```

## Configuration

### Datapoints (`config/datapoints.yaml`)

Maps Open3E DIDs to Home Assistant entities. Each entry defines:

```yaml
datapoints:
  268:                              # DID number
    type: "temperature_sensor"      # Type template from types.yaml
    name: "Flow Temperature"        # English name (translated via translations/)
    device: "indoor"                # Device grouping in HA
    subs:                           # Sub-items (open3e publishes e.g. /Actual, /Minimum)
      Actual: { suffix: "current" } # Only create entity for /Actual
```

Writable entities include `command_template` (Jinja2, rendered by HA):

```yaml
  396:
    type: "temperature_setpoint"
    name: "DHW Setpoint"
    device: "tank"
    min: 10
    max: 65
    step: 0.5
    writable: true
    write_mode: "write"
```

See [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for a complete configuration reference.

### Poll Interval Recommendations

Configure open3e polling intervals in your `args.txt`:

- **30s** (default): Temperature sensors, pump status, operation modes
- **60s**: Energy counters, statistics, compressor hours/starts
- **300s**: Device identification (DID 377), rarely-changing settings

### Type Templates (`config/templates/types.yaml`)

Reusable templates for entity types (sensor, number, binary_sensor, select, climate, water_heater). Each defines `device_class`, `unit_of_measurement`, `state_class`, etc.

### Translations (`config/translations/`)

Entity names are English in `datapoints.yaml`. Add a translation file (e.g., `de.yaml`) for localized names. The `--language` flag selects the active translation.

### User Overrides (`config/user/names.yaml`)

Custom entity names that survive updates. Copy `names.example.yaml` to `names.yaml` and edit.

## CLI Reference

```
open3e-bridge [OPTIONS]

Options:
  --mqtt-host HOST        MQTT broker hostname (default: localhost)
  --mqtt-port PORT        MQTT broker port (default: 1883)
  --mqtt-user USER        MQTT username
  --mqtt-password PASS    MQTT password (or set MQTT_PASSWORD env var)
  --language {de,en}      Entity name language (default: de)
  --config-dir PATH       Custom config directory (default: bundled)
  --test                  Test mode (prefix discovery with test/)
  --simulate FILE         Read MQTT messages from file instead of broker
  --cleanup               Remove retained discovery messages and exit
  --validate-config       Validate configuration files and exit
  --dump-entities         Show configured entities and exit (no MQTT needed)
  --diagnostics-interval N  Publish diagnostics every N seconds (0=disabled)
  --log-level LEVEL       DEBUG, INFO, WARNING, ERROR (default: INFO)
  --discovery-prefix PFX  Custom MQTT discovery prefix (default: homeassistant)
  --no-test-prefix        Don't add test/ prefix in test/simulate mode
  --version               Show version and exit
```

## Troubleshooting

**No entities appear in HA:**
1. Check open3e is publishing: `mosquitto_sub -h <broker> -t "open3e/#" -v`
2. Check bridge is running: `journalctl -u open3e-bridge -f`
3. Verify MQTT integration is enabled in HA (Settings > Integrations > MQTT)
4. Check discovery topics: `mosquitto_sub -h <broker> -t "homeassistant/#" -v`

**Entities appear but show "unavailable":**
- Check `open3e/LWT` topic — must be "online"
- Restart open3e to re-publish LWT

**Write commands don't work:**
- Check bridge logs for "Write verification FAILED" warnings
- Verify the DID supports writing (check open3e docs)
- Some DIDs require `write-raw` mode with hex encoding

**COP shows 0 or missing:**
- COP requires both DID 2488 (electrical) and DID 2496 (thermal) to be polled
- COP is not published when electrical power is 0

**NRC errors in logs:**
- `NRC 0x22` (ConditionsNotCorrect): device rejected the command (wrong mode/state)
- `NRC 0x31` (RequestOutOfRange): value outside allowed range

## Structure

```
bridge.py                  Main MQTT client, COP calc, write-verify, NRC handling
generators/
  base.py                  Topic parsing, config loading, translation, validation
  homeassistant.py         HA Discovery: sensor, number, select, binary, switch,
                           button, climate, water_heater
config/
  datapoints.yaml          DID definitions and entity mappings
  templates/types.yaml     Reusable entity type templates
  translations/de.yaml     German translations
  user/names.example.yaml  User name override template
contrib/
  open3e-bridge.service    systemd service unit
Dockerfile                 Container build file
```

## License

Apache-2.0
