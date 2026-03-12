# CAN Bus Connection Guide

## Overview

Open3E communicates with Viessmann E3 controllers via CAN bus (250 kbit/s). This guide covers physical connection for Vitocal 250/252, Vitodens, and VX3 systems.

## Connector Locations

### Vitocal 250/252

| Connector | Location | Notes |
|-----------|----------|-------|
| X3 (Stecker 91) | Indoor unit PCB | Direct CAN-H/CAN-L, preferred |
| E3 (Stecker 72) | Display unit | Alternative, easier access |

### Vitodens

| Connector | Location | Notes |
|-----------|----------|-------|
| X3 | Main PCB | Behind front cover |

## Wiring

CAN bus requires exactly 2 wires:

```
USB-CAN Adapter          Viessmann Controller
┌──────────┐             ┌──────────────┐
│ CAN-H ───┼─────────────┼── CAN-H      │
│ CAN-L ───┼─────────────┼── CAN-L      │
│ GND ─────┼─────────────┼── GND        │  (recommended)
└──────────┘             └──────────────┘
```

**Important:**
- Use **twisted pair** cable for CAN-H / CAN-L (reduces EMI)
- Connect **GND** between adapter and controller for a common reference
- Maximum cable length: ~40m (with proper termination)
- CAN bus bitrate: **250000** bps

## Termination

The E3 controller has built-in 120 Ohm termination. If your USB-CAN adapter also has termination, the bus will have 60 Ohm — this is fine for short distances (<2m).

For longer cables, ensure exactly 2x 120 Ohm terminators (one at each end).

## USB-CAN Adapters

### Tested adapters

| Adapter | Interface | Notes |
|---------|-----------|-------|
| USBtin | slcan (serial) | Low-cost, works well |
| PEAK PCAN-USB | socketcan (peak_usb) | Professional grade |
| Waveshare USB-CAN-A | socketcan (gs_usb) | Good Linux support |
| MCP2515 SPI | socketcan (mcp251x) | Raspberry Pi HAT |

### Linux setup

```bash
# Load kernel module for your adapter
sudo modprobe can
sudo modprobe can-raw

# For socketcan adapters (e.g., Waveshare, PEAK)
sudo ip link set can0 up type can bitrate 250000

# For serial/slcan adapters (e.g., USBtin)
sudo slcand -o -c -s5 /dev/ttyACM0 slcan0
sudo ip link set slcan0 up
```

### Virtual CAN (for testing)

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set vcan0 up
```

## Common Errors

### F.764 / F.1034 (communication error)

These Viessmann error codes indicate CAN bus communication problems.

**Causes:**
- Wrong bitrate (must be 250000)
- Loose/broken wiring
- Missing GND connection
- Excessive cable length without proper termination
- USB adapter power saving (see below)

**USB power saving fix:**

```bash
# Disable USB autosuspend for your adapter
echo -1 | sudo tee /sys/bus/usb/devices/*/power/autosuspend_delay_ms

# Make permanent via udev rule
echo 'ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="XXXX", ATTR{power/autosuspend_delay_ms}="-1"' | \
  sudo tee /etc/udev/rules.d/99-can-adapter.rules
```

### No data received

1. Verify CAN interface is up: `ip -details link show can0`
2. Check for any traffic: `candump can0`
3. Verify bitrate: must be 250000
4. Try the other connector (X3 vs E3)

### Intermittent disconnects

- Check cable quality (use twisted pair)
- Verify GND connection
- Check for power supply issues on the USB adapter
- Consider a powered USB hub for Raspberry Pi setups
