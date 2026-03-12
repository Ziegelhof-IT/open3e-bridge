"""Tests for C02/C03/C07: Heuristic engine for auto-discovery."""

from generators.heuristics import infer_device, infer_entity_config


class TestInferEntityConfig:
    """Test DID name → entity config inference."""

    # Temperature patterns
    def test_flow_temperature_sensor(self):
        hint = infer_entity_config("FlowTemperatureSensor")
        assert hint.entity_type == "sensor"
        assert hint.device_class == "temperature"
        assert hint.unit == "°C"
        assert hint.state_class == "measurement"

    def test_outside_temperature(self):
        hint = infer_entity_config("OutsideTemperatureSensor")
        assert hint.device_class == "temperature"

    def test_domestic_hot_water_temperature_setpoint(self):
        hint = infer_entity_config("DomesticHotWaterTemperatureSetpoint")
        assert hint.device_class == "temperature"

    # Pressure
    def test_water_pressure(self):
        hint = infer_entity_config("WaterPressureSensor")
        assert hint.device_class == "pressure"
        assert hint.unit == "bar"

    # Power
    def test_electrical_power(self):
        hint = infer_entity_config("CurrentElectricalPowerConsumptionSystem")
        assert hint.device_class == "power"
        assert hint.unit == "W"

    def test_thermal_capacity(self):
        # "ThermalCapacity" doesn't match Power pattern — tests fallback
        hint = infer_entity_config("CurrentThermalCapacitySystem")
        assert hint.entity_type == "sensor"

    # Energy
    def test_electrical_energy(self):
        hint = infer_entity_config("ObjectElectricalEnergyStatistical")
        assert hint.device_class == "energy"
        assert hint.unit == "kWh"
        assert hint.state_class == "total_increasing"

    def test_grid_energy(self):
        hint = infer_entity_config("GridFeedInEnergy")
        assert hint.device_class == "energy"

    # Pump with status → binary
    def test_pump_power_state(self):
        hint = infer_entity_config("MixerOneCircuitPump", "PowerState")
        assert hint.entity_type == "binary_sensor"

    def test_pump_status(self):
        hint = infer_entity_config("CentralHeatingPumpStatus")
        assert hint.entity_type == "binary_sensor"

    # Pump without status → sensor %
    def test_pump_sensor(self):
        hint = infer_entity_config("CentralHeatingPump")
        assert hint.entity_type == "sensor"
        assert hint.unit == "%"

    # Fan
    def test_fan(self):
        hint = infer_entity_config("PrimaryCircuitFanOne")
        assert hint.entity_type == "sensor"
        assert hint.unit == "%"
        assert hint.icon == "mdi:fan"

    # Valve
    def test_valve_position(self):
        hint = infer_entity_config("ThreeWayValvePosition")
        assert hint.unit == "%"
        assert hint.icon == "mdi:valve"

    def test_valve_generic(self):
        hint = infer_entity_config("FourWayValve")
        assert hint.icon == "mdi:valve"

    # Setpoint → number
    def test_setpoint(self):
        hint = infer_entity_config("FlowTemperatureSetpoint")
        # Temperature pattern wins over Setpoint (first match)
        assert hint.device_class == "temperature"

    def test_pure_setpoint(self):
        hint = infer_entity_config("MinimumSetpoint")
        assert hint.entity_type == "number"

    # Mode/OperationState
    def test_operation_state(self):
        hint = infer_entity_config("MixerOneCircuitOperationState")
        assert hint.entity_type == "sensor"

    # Speed
    def test_speed_rps(self):
        hint = infer_entity_config("CompressorSpeedRPS")
        assert hint.unit == "rps"

    def test_speed_generic(self):
        hint = infer_entity_config("CompressorSpeed")
        assert hint.unit == "rpm"

    # Statistics/counters
    def test_statistical(self):
        hint = infer_entity_config("AdditionalElectricHeaterStatistical")
        assert hint.state_class == "total_increasing"

    # Status/State generic
    def test_status(self):
        hint = infer_entity_config("PVStatus")
        assert hint.entity_type == "sensor"

    # Default fallback
    def test_unknown_did(self):
        hint = infer_entity_config("SomeCompletelyUnknownDID")
        assert hint.entity_type == "sensor"
        assert hint.icon == "mdi:information-outline"

    # Sub-item influence
    def test_sub_item_enhances_matching(self):
        hint = infer_entity_config("SomePump", "PowerState")
        assert hint.entity_type == "binary_sensor"

    # Edge cases
    def test_empty_name(self):
        hint = infer_entity_config("")
        assert hint.entity_type == "sensor"

    def test_numeric_name(self):
        hint = infer_entity_config("12345")
        assert hint.entity_type == "sensor"

    def test_case_insensitive(self):
        hint = infer_entity_config("flowtemperaturesensor")
        assert hint.device_class == "temperature"


class TestInferDevice:
    """Test ECU address → device inference."""

    def test_main_controller(self):
        device = infer_device(0x680)
        assert device.name == "Main Controller"
        assert device.model == "HPMU"

    def test_display(self):
        device = infer_device(0x684)
        assert device.name == "Display"

    def test_outdoor_unit(self):
        device = infer_device(0x68C)
        assert device.name == "Outdoor Unit"
        assert device.role == "Refrigerant circuit management"

    def test_battery(self):
        device = infer_device(0x68F)
        assert device.name == "Battery Management"

    def test_inverter(self):
        device = infer_device(0x6C2)
        assert device.name == "Inverter"

    def test_gateway_6c3(self):
        device = infer_device(0x6C3)
        assert device.name == "Gateway"

    def test_gateway_6c5(self):
        device = infer_device(0x6C5)
        assert device.name == "Gateway"

    def test_aux_heater(self):
        device = infer_device(0x6CF)
        assert device.name == "Auxiliary Heater"

    def test_unknown_ecu(self):
        device = infer_device(0x6FF)
        assert "Unknown ECU" in device.name
        assert "6FF" in device.name
        assert device.model is None

    def test_unknown_ecu_zero(self):
        device = infer_device(0x000)
        assert "Unknown ECU" in device.name
