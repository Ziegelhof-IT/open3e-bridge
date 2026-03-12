"""Auto-discovery heuristic engine for inferring entity config from DID names."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class EntityHint:
    """Heuristic inference result for an unknown DID."""
    entity_type: str
    device_class: str | None = None
    unit: str | None = None
    state_class: str | None = None
    icon: str | None = None


@dataclass
class DeviceHint:
    """Heuristic device identification from ECU address."""
    name: str
    model: str | None = None
    role: str | None = None


# Pattern rules: (compiled regex on DID name, EntityHint)
# Order matters — first match wins
_PATTERNS: list[tuple[re.Pattern[str], EntityHint]] = [
    (re.compile(r"Temperature", re.IGNORECASE), EntityHint(
        entity_type="sensor", device_class="temperature",
        unit="°C", state_class="measurement", icon="mdi:thermometer")),
    (re.compile(r"Pressure", re.IGNORECASE), EntityHint(
        entity_type="sensor", device_class="pressure",
        unit="bar", state_class="measurement", icon="mdi:gauge")),
    (re.compile(r"Energy", re.IGNORECASE), EntityHint(
        entity_type="sensor", device_class="energy",
        unit="kWh", state_class="total_increasing", icon="mdi:lightning-bolt")),
    # Pump/Fan + Status/PowerState must be before generic Power pattern
    (re.compile(r"(Pump|Fan)[\w/]*(Status|State|PowerState)", re.IGNORECASE), EntityHint(
        entity_type="binary_sensor", device_class="power",
        icon="mdi:pump")),
    (re.compile(r"Power", re.IGNORECASE), EntityHint(
        entity_type="sensor", device_class="power",
        unit="W", state_class="measurement", icon="mdi:flash")),
    (re.compile(r"Pump", re.IGNORECASE), EntityHint(
        entity_type="sensor", device_class="power_factor",
        unit="%", state_class="measurement", icon="mdi:pump")),
    (re.compile(r"Fan", re.IGNORECASE), EntityHint(
        entity_type="sensor", unit="%",
        state_class="measurement", icon="mdi:fan")),
    (re.compile(r"Valve.*Position", re.IGNORECASE), EntityHint(
        entity_type="sensor", unit="%",
        state_class="measurement", icon="mdi:valve")),
    (re.compile(r"Valve", re.IGNORECASE), EntityHint(
        entity_type="sensor", icon="mdi:valve")),
    (re.compile(r"Setpoint", re.IGNORECASE), EntityHint(
        entity_type="number", icon="mdi:target")),
    (re.compile(r"(Mode|OperationState)", re.IGNORECASE), EntityHint(
        entity_type="sensor", icon="mdi:cog")),
    (re.compile(r"Speed.*RPS", re.IGNORECASE), EntityHint(
        entity_type="sensor", unit="rps",
        state_class="measurement", icon="mdi:speedometer")),
    (re.compile(r"Speed", re.IGNORECASE), EntityHint(
        entity_type="sensor", unit="rpm",
        state_class="measurement", icon="mdi:speedometer")),
    (re.compile(r"(Status|State)", re.IGNORECASE), EntityHint(
        entity_type="sensor", icon="mdi:information-outline")),
    (re.compile(r"(Hours|Starts|Counter|Statistical)", re.IGNORECASE), EntityHint(
        entity_type="sensor", state_class="total_increasing",
        icon="mdi:counter")),
    (re.compile(r"(Current|Voltage)", re.IGNORECASE), EntityHint(
        entity_type="sensor", state_class="measurement",
        icon="mdi:sine-wave")),
]

# Default fallback
_DEFAULT_HINT = EntityHint(entity_type="sensor", icon="mdi:information-outline")


def infer_entity_config(did_name: str, sub_item: str | None = None) -> EntityHint:
    """Infer entity configuration from a DID name using pattern matching.

    Args:
        did_name: The DID name from the MQTT topic (e.g. "FlowTemperatureSensor")
        sub_item: Optional sub-item name (e.g. "Actual", "PowerState")

    Returns:
        EntityHint with inferred entity type, unit, etc.
    """
    # Combine DID name and sub_item for better matching
    search_text = did_name
    if sub_item:
        search_text = f"{did_name}/{sub_item}"

    for pattern, hint in _PATTERNS:
        if pattern.search(search_text):
            return hint

    return _DEFAULT_HINT


# ECU address to device mapping
_ECU_DEVICES: dict[int, DeviceHint] = {
    0x680: DeviceHint("Main Controller", "HPMU", "Primary heat pump controller"),
    0x684: DeviceHint("Display", "HMI", "User interface"),
    0x68C: DeviceHint("Outdoor Unit", "VCMU", "Refrigerant circuit management"),
    0x68F: DeviceHint("Battery Management", "BMCU", "Battery management (VX3)"),
    0x6C2: DeviceHint("Inverter", "Inverter", "PV/Grid inverter"),
    0x6C3: DeviceHint("Gateway", "Backend", "Viessmann cloud gateway"),
    0x6C5: DeviceHint("Gateway", "Backend", "Viessmann cloud gateway"),
    0x6CF: DeviceHint("Auxiliary Heater", "EHCU", "Electric auxiliary heater"),
}


def infer_device(ecu_addr: int) -> DeviceHint:
    """Infer device info from ECU address.

    Args:
        ecu_addr: ECU address as integer (e.g. 0x680)

    Returns:
        DeviceHint with device name, model, and role
    """
    if ecu_addr in _ECU_DEVICES:
        return _ECU_DEVICES[ecu_addr]
    return DeviceHint(f"Unknown ECU {ecu_addr:03X}", None, None)
