# Vitocal 250/252 Example Configuration

This documents the complete entity setup for a Vitocal 250-A / 252-A heat pump system, as deployed and tested.

## System Overview

| Device | Model | ECU | Role |
|--------|-------|-----|------|
| Outdoor Unit | Vitocal 250-A | 0x680 | Compressor, fans, evaporator |
| Indoor Unit | Vitocal 252-A | 0x680 | Hydraulics, pumps, controller |
| Hot Water Tank | Vitocell 100-E | 0x680 | DHW storage |
| Heating Circuit Mixer | Vitocal 252-A | 0x680 | HK1/HK2 mixing valves |
| Auxiliary Heater | Vitocal 252-A | 0x680 | Electric backup heater |
| Energy Management | PV/Grid | 0x680 | SG Ready, PV integration |

All devices communicate via internal CAN bus at ECU address 0x680.

## Configured Entities (47 total)

### Temperature Sensors (12)

| DID | Name (DE) | Sub | Device |
|-----|-----------|-----|--------|
| 268 | Vorlauftemperatur | Actual | Indoor |
| 269 | Ruecklauftemperatur | Actual | Indoor |
| 274 | Aussentemperatur | Actual | Outdoor |
| 271 | Warmwasser | Actual | Tank |
| 284 | HK1 Vorlauftemperatur | Actual | Mixer |
| 286 | HK2 Vorlauftemperatur | Actual | Mixer |
| 354 | Primaer-Waermetauscher | Actual | Indoor |
| 1770 | Vorlauf Sekundaerkreis | Actual | Indoor |
| 1771 | Heizungsraum | Actual | Indoor |
| 2333 | Verfluessiger | Actual | Indoor |
| 2334 | Verdampfer | Actual | Outdoor |
| 3016 | Pufferspeicher | Actual | Tank |

### Binary Sensors (7)

| DID | Name (DE) | Trigger Sub | Device |
|-----|-----------|-------------|--------|
| 2442 | WP Frostschutz | - | Outdoor |
| 401 | HK1 Pumpe | PowerState | Mixer |
| 402 | HK2 Pumpe | PowerState | Mixer |
| 2351 | Verdichter | PowerState | Outdoor |
| 2352 | Zusatzheizung | PowerState | Heater |
| 2855 | HK1 Frostschutz | State | Mixer |
| 2856 | HK2 Frostschutz | State | Mixer |

### Power/Energy Sensors (5)

| DID | Name (DE) | Unit | Device |
|-----|-----------|------|--------|
| 2488 | Leistungsaufnahme System | W | Indoor |
| 2496 | Thermische Leistung | W | Indoor |
| 1603 | Netz Wirkleistung | W | Energy |
| 535 | Elektr. Energie Statistik | kWh | Indoor |
| 1834 | PV Stromerzeugung | W | Energy |

### Pump/Fan Sensors (6)

| DID | Name (DE) | Unit | Device |
|-----|-----------|------|--------|
| 381 | Interne Pumpe | % | Indoor |
| 1043 | Volumenstrom | l/h | Indoor |
| 1775 | Luefter 1 | % | Outdoor |
| 1776 | Luefter 2 | % | Outdoor |
| 2346 | Kompressor Drehzahl | % | Outdoor |
| 2569 | Kompressor rps | rps | Outdoor |

### Generic Sensors (5)

| DID | Name (DE) | Device |
|-----|-----------|--------|
| 2335 | 4-Wege-Ventil | Indoor |
| 2350 | SG Ready | Indoor |
| 875 | Legionellenschutz | Indoor |
| 1690 | PV Status | Energy |
| 2369/2370 | Verdichter/Heizer Statistik | Outdoor/Heater |

### Writable Entities

| DID | Name (DE) | Type | Range | Device |
|-----|-----------|------|-------|--------|
| 396 | WW Solltemperatur | number | 10-65 degC | Tank |
| 2626 | Max Leistung E-Heizung | number | 0/4000-8000 W | Heater |
| 1102 | HK1 Pumpe Sollwert | number | 20-100 % | Mixer |
| 1103 | HK2 Pumpe Sollwert | number | 20-100 % | Mixer |
| 1192 | HK1 Vorlauf Min/Max | number | 10-60 degC | Mixer |
| 1415 | HK1 Betriebsmodus | select | off/auto | Mixer |
| 1416 | HK2 Betriebsmodus | select | off/auto | Mixer |
| 1006 | Schnellmodus | switch | on/off | Indoor |
| 1710 | WW Einmalladung | button | - | Tank |

### Climate Entities (2)

| DID | Name (DE) | Modes | Temp Range |
|-----|-----------|-------|------------|
| 1415 | Heizkreis 1 | off/auto | 3-37 degC |
| 1416 | Heizkreis 2 | off/auto | 3-37 degC |

### Water Heater (1, experimental)

| DID | Name (DE) | Modes | Temp Range |
|-----|-----------|-------|------------|
| 531 | Warmwasser | off/eco/performance | 10-60 degC |

## open3e args.txt Example

```
# /opt/open3e/args.txt
# Vitocal 250/252 - open3e MQTT polling configuration
-c can0
-m mqtt.local
-muser mqtt
-mpass yourpassword
-r 268.Actual 269.Actual 274.Actual 271.Actual 318.Actual 381.Actual 1043.Actual -i 30
-r 2488 2496 1603.ActivePower 1834 -i 30
-r 401.PowerState 402.PowerState 2351.PowerState 2352.PowerState 2442 -i 30
-r 1415.Mode/ID 1416.Mode/ID 2350 2335 -i 30
-r 284.Actual 286.Actual 354.Actual 1770.Actual 1771.Actual 2333.Actual 2334.Actual 3016.Actual -i 30
-r 2346 2569 1775 1776 -i 30
-r 535.GridSuppliedEnergy 535.ProducedEnergy 535.GridFeedInEnergy -i 60
-r 2369.hours 2369.starts 2370.hours 2370.starts -i 60
-r 875 1690 -i 300
-l
```

## CAN Bus Connection

The Vitocal 250/252 internal CAN bus is accessible via:

- **Stecker 91** (X3 connector on the indoor unit PCB): direct CAN connection
- **Stecker 72** (E3 connector on the display): alternative access point

CAN parameters: 250 kbit/s, terminated (120 Ohm built-in).

See [CAN_BUS_GUIDE.md](CAN_BUS_GUIDE.md) for detailed wiring instructions.
