# Contributing to Open3E Bridge

## Adding a new device or DID

Adding support for new devices or data points requires **only YAML changes** — no Python code needed.

### 1. Find the DID

Use open3e to scan your device:

```bash
open3e -c can0 -scan
```

Or read specific DIDs:

```bash
open3e -c can0 -r 268 -r 269 -r 274
```

### 2. Add the DID to datapoints.yaml

Edit `config/datapoints.yaml`:

```yaml
datapoints:
  YOUR_DID:
    type: "temperature_sensor"    # Choose from types.yaml
    name: "Your Sensor Name"      # English name
    device: "indoor"              # Device key (or add new device)
    subs:
      Actual: { suffix: "current" }
```

### 3. Add translation (optional)

Edit `config/translations/de.yaml`:

```yaml
names:
  "Your Sensor Name": "Ihr Sensorname"
```

### 4. Validate

```bash
open3e-bridge --validate-config
open3e-bridge --dump-entities
```

### 5. Test

```bash
# Run existing tests
make test

# Test with simulation
echo "open3e/680_YOUR_DID_YourSensorName/Actual 12.5" > test_messages.txt
open3e-bridge --simulate test_messages.txt --mqtt-host localhost
```

## Adding a new device type

If your device (e.g., Vitodens 300) uses different DIDs:

1. Add device entries to the `devices` section of `datapoints.yaml`
2. Add all relevant DIDs to the `datapoints` section
3. Add translations to `config/translations/de.yaml`
4. Submit a PR with your device's args.txt as documentation

## Available type templates

See `config/templates/types.yaml` for all available types:
- `temperature_sensor`, `pressure_sensor`, `power_sensor`, `energy_sensor`
- `pump_sensor`, `generic_sensor`, `valve_position`
- `temperature_setpoint`, `select_mode`
- `binary_onoff`, `switch_toggle`, `button_action`
- `water_heater`

## Development setup

```bash
git clone https://github.com/open3e/open3e-bridge.git
cd open3e-bridge
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run checks
make ci
```

## Pull request guidelines

- One feature or fix per PR
- Include tests for new functionality
- Run `make ci` before submitting (lint + typecheck + tests)
- Update `config/translations/de.yaml` if adding new entity names
- Use English for code and comments, German for user-visible strings

## Code structure

```
bridge.py              Entry point, MQTT client
generators/base.py     Config loading, topic parsing
generators/homeassistant.py  Discovery generation
config/                YAML configurations (edit these!)
tests/                 pytest test suite
```
