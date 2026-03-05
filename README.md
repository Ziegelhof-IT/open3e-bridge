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
```

### 3. Verify

Check Home Assistant: new entities should appear under **Settings > Devices & Services > MQTT**.

### Prerequisites

- **Open3E** running and publishing to MQTT (`open3e @args.txt` with `-m` flag)
- **MQTT broker** (e.g., Mosquitto) reachable from both open3e and HA
- **Home Assistant** with MQTT integration configured

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

```bash
# Copy service file and adjust ExecStart path + MQTT credentials
sudo cp contrib/open3e-bridge.service /etc/systemd/system/

# Create override for credentials
sudo systemctl edit open3e-bridge
# Add:
# [Service]
# ExecStart=
# ExecStart=/opt/open3e-bridge/venv/bin/open3e-bridge --mqtt-host mqtt.local --mqtt-user mqtt --mqtt-password secret --language de

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

### Poll Interval Recommendations

Configure open3e polling intervals in your `args.txt`:

- **30s** (default): Temperature sensors, pump status, operation modes
- **60s**: Energy counters, statistics, compressor hours/starts
- **300s**: Device identification (DID 377), rarely-changing settings

### Type Templates (`config/templates/types.yaml`)

Reusable templates for entity types (sensor, number, binary_sensor, select, climate). Each defines `device_class`, `unit_of_measurement`, `state_class`, etc.

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
  --mqtt-password PASS    MQTT password
  --language {de,en}      Entity name language (default: de)
  --test                  Test mode (prefix discovery with test/)
  --simulate FILE         Read MQTT messages from file instead of broker
  --cleanup               Remove retained discovery messages and exit
  --validate-config       Validate configuration files and exit
  --dump-entities         Show configured entities and exit (no MQTT needed)
  --log-level LEVEL       DEBUG, INFO, WARNING, ERROR (default: INFO)
  --discovery-prefix PFX  Custom MQTT discovery prefix (default: homeassistant)
  --no-test-prefix        Don't add test/ prefix in test/simulate mode
```

## Structure

```
bridge.py                  Main MQTT client and entry point
generators/
  base.py                  Topic parsing, config loading, translation
  homeassistant.py         HA MQTT Discovery payload generation
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
