# systemd Setup Guide

Step-by-step installation of open3e-bridge as a systemd service.

## 1. Install open3e-bridge

```bash
# Create installation directory
sudo mkdir -p /opt/open3e-bridge
sudo chown $USER:$USER /opt/open3e-bridge

# Create virtual environment
python3 -m venv /opt/open3e-bridge/venv
/opt/open3e-bridge/venv/bin/pip install open3e-bridge
```

## 2. Test the connection

```bash
/opt/open3e-bridge/venv/bin/open3e-bridge \
  --mqtt-host mqtt.local \
  --mqtt-user mqtt \
  --mqtt-password yourpassword \
  --language de \
  --log-level DEBUG
```

Verify entities appear in Home Assistant before proceeding.

## 3. Install the service

```bash
sudo cp contrib/open3e-bridge.service /etc/systemd/system/
```

## 4. Configure credentials

Use a systemd override file to keep credentials separate from the service file:

```bash
sudo systemctl edit open3e-bridge
```

Add the following (adjust paths and credentials):

```ini
[Service]
ExecStart=
ExecStart=/opt/open3e-bridge/venv/bin/open3e-bridge \
  --mqtt-host mqtt.local \
  --mqtt-user mqtt \
  --mqtt-password yourpassword \
  --language de \
  --diagnostics-interval 300
```

Note: the first empty `ExecStart=` clears the default from the unit file.

Alternatively, use the MQTT_PASSWORD environment variable:

```ini
[Service]
Environment=MQTT_PASSWORD=yourpassword
ExecStart=
ExecStart=/opt/open3e-bridge/venv/bin/open3e-bridge \
  --mqtt-host mqtt.local \
  --mqtt-user mqtt \
  --language de
```

## 5. Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now open3e-bridge
```

## 6. Verify

```bash
# Check status
sudo systemctl status open3e-bridge

# Follow logs
journalctl -u open3e-bridge -f

# Check diagnostics via MQTT
mosquitto_sub -h mqtt.local -t "open3e/bridge/diagnostics" -C 1
```

## Debugging

### Bridge not starting

```bash
# Check for errors
journalctl -u open3e-bridge --no-pager -n 50

# Validate config
/opt/open3e-bridge/venv/bin/open3e-bridge --validate-config

# List configured entities
/opt/open3e-bridge/venv/bin/open3e-bridge --dump-entities
```

### USB CAN adapter power saving

Some USB-CAN adapters (e.g., USBtin) enter power saving mode. Disable USB autosuspend:

```bash
# Find your USB device
lsusb | grep -i can

# Disable autosuspend (replace XXXX:YYYY with vendor:product)
echo -1 | sudo tee /sys/bus/usb/devices/*/power/autosuspend_delay_ms
```

Or add a udev rule:

```bash
echo 'ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="XXXX", ATTR{idProduct}=="YYYY", ATTR{power/autosuspend_delay_ms}="-1"' | \
  sudo tee /etc/udev/rules.d/99-can-adapter.rules
```

### Updating

```bash
sudo systemctl stop open3e-bridge
/opt/open3e-bridge/venv/bin/pip install --upgrade open3e-bridge
sudo systemctl start open3e-bridge
```
