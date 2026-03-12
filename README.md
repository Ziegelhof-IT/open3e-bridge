# Open3E Home Assistant Bridge

Generates Home Assistant MQTT Discovery from Open3E MQTT topics. No manual HA YAML needed: entities appear automatically based on datapoint mappings in YAML.

## Is this for me?

This bridge is for you if:
- You have an **E3-based heating system** — Viessmann (Vitocal, Vitodens, Vx3, Vair) or Vaillant (aroTHERM, ecoTEC) with E3 controller
- You want to see temperatures, energy data, and control settings in **Home Assistant**
- You already have — or are willing to set up — **Open3E** on a Raspberry Pi or Linux PC

This bridge does **not** replace ViCare or myVAILLANT. It adds local control via Home Assistant, without cloud dependency.

**Compatibility note:** The bridge ships with profiles for different device types. Vitocal heat pumps have the most complete coverage. Vitodens gas boilers and Vaillant E3 systems work with the common profile and auto-discovery for unconfigured DIDs. Community contributions for additional profiles are welcome.

## Prerequisites

You need 3 things running before installing this bridge:

### 1. Open3E (reads data from your heat pump)

Open3E is a separate tool that connects to your heat pump via CAN bus or DoIP and publishes data to MQTT.

- **Install guide:** [github.com/open3e/open3e](https://github.com/open3e/open3e)
- Open3E must run with the `-m` (MQTT) flag: `open3e @args.txt -m`
- Typically runs on a Raspberry Pi near the heat pump

**Hardware:** You need a USB-CAN adapter (~20 EUR) plugged into the heat pump's internal CAN bus. Common models: USBtin, CANable, Waveshare USB-CAN-A. See [CAN Bus Guide](docs/CAN_BUS_GUIDE.md) for wiring and setup.

Alternatively, some Viessmann systems support **DoIP** (Diagnostics over IP) — no CAN adapter needed, but requires a compatible gateway.

### 2. MQTT Broker (message bus)

MQTT is the message system connecting open3e, this bridge, and Home Assistant.

- **Home Assistant OS:** Install the "Mosquitto broker" add-on (Settings > Add-ons > search "Mosquitto" > Install > Start)
- **Standalone Linux:** `sudo apt install mosquitto mosquitto-clients`
- The broker must be reachable from both the open3e device and Home Assistant

### 3. Home Assistant with MQTT Integration

- Go to **Settings > Devices & Services > Add Integration > MQTT**
- Enter your broker's IP (e.g., `192.168.1.100`) and port (`1883`)
- If using Mosquitto add-on on HAOS: use `core-mosquitto` as host

**How it all fits together:**
```
Heat Pump ──CAN/DoIP──> open3e ──MQTT──> Broker <──MQTT──> open3e-bridge ──Discovery──> Home Assistant
                        (RPi)            (HA/RPi)          (RPi/Server)                  (NUC/RPi)
```

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

### 3. Check generated entities (no MQTT needed)

```bash
# Show all configured entities before connecting
open3e-bridge --dump-entities

# Validate your configuration files
open3e-bridge --validate-config
```

### 4. Verify in Home Assistant

Check Home Assistant: new entities should appear under **Settings > Devices & Services > MQTT**.

A **Bridge Status** diagnostic entity (`binary_sensor.open3e_bridge_status`) shows connection state, message counts, and last errors — check this first if something seems wrong.

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
- Health entity: `binary_sensor.open3e_bridge_status` with diagnostic attributes
- Periodic diagnostics on `open3e/bridge/diagnostics`
- Generator plugin system: `--generator` flag for custom output formats

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

### Local Overlay (`config/local/`)

Add custom DIDs without modifying the shipped config — your changes survive `git pull`:

1. Copy `config/local/datapoints.example.yaml` to `config/local/datapoints.yaml`
2. Add your custom datapoints and devices
3. The bridge merges local config on top of the main config (local wins)

```yaml
# config/local/datapoints.yaml
devices:
  my_buffer:
    name: "Buffer Tank"
    model: "Custom Buffer"

datapoints:
  1234:
    type: "temperature_sensor"
    name: "Buffer Temperature"
    device: "my_buffer"
    subs:
      Actual: { suffix: "current" }
```

You can also add custom type templates in `config/local/types.yaml`.

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
  --generator TYPE        Generator type (default: homeassistant)
  --list-generators       List available generator types and exit
  --test                  Test mode (prefix discovery with test/)
  --simulate FILE         Read MQTT messages from file instead of broker
  --cleanup               Remove retained discovery messages and exit
  --validate-config       Validate configuration files and exit
  --dump-entities         Show configured entities and exit (no MQTT needed)
  --no-auto-discover      Disable auto-discovery (enabled by default)
  --profile PROFILE       Device profile: auto, vitocal, vitodens, common (default: auto)
  --diagnostics-interval N  Publish diagnostics every N seconds (0=disabled)
  --log-level LEVEL       DEBUG, INFO, WARNING, ERROR (default: INFO)
  --discovery-prefix PFX  Custom MQTT discovery prefix (default: homeassistant)
  --no-test-prefix        Don't add test/ prefix in test/simulate mode
  --version               Show version and exit
```

## Troubleshooting

### No entities appear in Home Assistant

1. **Is open3e publishing?**
   ```bash
   mosquitto_sub -h <broker-ip> -t "open3e/#" -v
   ```
   You should see messages like `open3e/680_268_FlowTemperatureSensor/Actual 42.5`.
   If nothing appears: check that open3e is running with the `-m` flag and pointing at the right broker.

2. **Is the bridge running?**
   ```bash
   journalctl -u open3e-bridge -f
   # Or if running manually:
   open3e-bridge --mqtt-host <broker-ip> --log-level DEBUG
   ```

3. **Is MQTT integration enabled in HA?**
   Go to Settings > Devices & Services > Integrations > MQTT. If not there, add it.

4. **Check discovery topics:**
   ```bash
   mosquitto_sub -h <broker-ip> -t "homeassistant/#" -v
   ```
   You should see JSON payloads being published. If not: the bridge is not matching your open3e topics against `datapoints.yaml`.

5. **Check your config:**
   ```bash
   open3e-bridge --dump-entities
   open3e-bridge --validate-config
   ```

### Entities appear but show "unavailable"

- The `open3e/LWT` topic must be `"online"` — check with `mosquitto_sub -h <broker-ip> -t "open3e/LWT" -v`
- Restart open3e to re-publish its LWT
- Check `binary_sensor.open3e_bridge_status` in HA for bridge health details

### Write commands don't work

- Check bridge logs for **"Write verification FAILED"** — this means the controller received the write but returned a different value. Common causes:
  - Value outside the allowed range (check `min`/`max` in `datapoints.yaml`)
  - Heat pump is in a mode that doesn't accept changes (e.g., holiday mode)
- Verify the DID supports writing in open3e docs
- Some DIDs require `write-raw` mode with hex encoding

### NRC errors in logs

NRC (Negative Response Code) means the heat pump's controller rejected a request:

| Code | Meaning | What to do |
|------|---------|------------|
| `NRC 0x22` | ConditionsNotCorrect | Heat pump rejected — wrong mode/state. Wait for the right conditions or change operating mode first |
| `NRC 0x31` | RequestOutOfRange | Value too high/low. Check allowed range for this DID |
| `NRC 0x33` | SecurityAccessDenied | Authentication required. Some DIDs need Service 0x77 |
| `NRC 0x14` | ResponseTooLong | Response data exceeds limit. Usually a firmware issue |

### MQTT connection fails

- **"bad username or password"** — check `--mqtt-user` and `--mqtt-password` (or `MQTT_PASSWORD` env var)
- **"not authorized"** — the MQTT broker ACL doesn't allow this user. Check your Mosquitto config
- **"server unavailable"** — broker not running or wrong host/port. Test with: `mosquitto_pub -h <broker-ip> -t test -m hello`
- **Connection keeps dropping** — the bridge uses exponential backoff (1s to 120s) and auto-reconnects. Check `journalctl` for disconnect reasons

### COP shows 0 or missing

- COP requires both DID 2488 (electrical power) and DID 2496 (thermal power) to be polled by open3e
- COP is not published when electrical power is 0 (compressor off)

### Bridge status entity

The `binary_sensor.open3e_bridge_status` entity provides:
- **State**: ON when connected
- **Attributes**: version, uptime, messages processed, entities cached, failed writes, last error

Check this entity first when diagnosing issues.

## Custom Generators

The bridge supports custom output generators via the `--generator` flag:

```bash
# List available generators
open3e-bridge --list-generators

# Use a specific generator
open3e-bridge --generator homeassistant --mqtt-host <broker-ip>
```

To create a custom generator, subclass `BaseGenerator` from `generators/base.py` and register it in `generators/registry.py`.

## Structure

```
bridge.py                  Main MQTT client, COP calc, write-verify, NRC handling
generators/
  base.py                  Topic parsing, config loading, translation, validation
  homeassistant.py         HA Discovery: sensor, number, select, binary, switch,
                           button, climate, water_heater
  heuristics.py            Auto-discovery pattern inference
  registry.py              Generator plugin registry
config/
  datapoints.yaml          DID definitions and entity mappings
  templates/types.yaml     Reusable entity type templates
  translations/de.yaml     German translations
  user/names.example.yaml  User name override template
  local/                   Local overlay (custom DIDs, survives updates)
contrib/
  open3e-bridge.service    systemd service unit
Dockerfile                 Container build file
```

## License

Apache-2.0
