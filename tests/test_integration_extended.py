"""Tests for A10: Extended integration tests — multi-entity flows, reconnect, write-verify, NRC."""
import logging
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def bridge():
    with patch("bridge.mqtt.Client") as MockClient:
        MockClient.return_value = MagicMock()
        from bridge import Open3EBridge
        b = Open3EBridge()
        return b


class TestMultiEntityFlow:
    """Test multiple entity types discovered simultaneously."""

    def test_sensor_and_binary_and_number(self, bridge):
        """Process sensor, binary, and number entity messages."""
        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "12.5")
        bridge.process_message("open3e/680_2442_HeatPumpFrostProtection", "1")
        bridge.process_message("open3e/680_396_DomesticHotWaterTemperatureSetpoint", "55.0")

        # All three should generate discovery
        assert bridge._discovery_published >= 3

    def test_entity_types_tracked(self, bridge):
        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "12.5")
        bridge.process_message("open3e/680_2442_HeatPumpFrostProtection", "1")
        bridge.process_message("open3e/680_396_DomesticHotWaterTemperatureSetpoint", "55.0")

        types = dict(bridge._entity_types)
        assert "sensor" in types
        assert "binary_sensor" in types
        assert "number" in types

    def test_duplicate_messages_deduplicated(self, bridge):
        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "12.5")
        first_count = bridge._discovery_published

        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "13.0")
        # Same discovery config → should not republish
        assert bridge._discovery_published == first_count

    def test_water_heater_plus_sensor(self, bridge):
        """water_heater entity + sensor entity together."""
        bridge.process_message("open3e/680_531_DomesticHotWaterOperationState", "1")
        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "12.5")

        # Check water_heater discovery was published
        wh_calls = [
            c for c in bridge.client.publish.call_args_list
            if "water_heater" in str(c)
        ]
        assert len(wh_calls) >= 1


class TestReconnectScenario:
    """Test HA restart / reconnect behavior."""

    def test_ha_restart_republishes_all(self, bridge):
        """When HA sends 'online', all cached configs are republished."""
        # First, cache some discovery configs
        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "12.5")
        cached_count = len(bridge.published_configs)
        assert cached_count > 0

        initial_publish_count = bridge.client.publish.call_count

        # Simulate HA restart
        bridge.process_message("homeassistant/status", "online")

        # Should have republished all cached configs
        assert bridge.client.publish.call_count >= initial_publish_count + cached_count

    def test_ha_offline_ignored(self, bridge):
        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "12.5")
        count_before = bridge.client.publish.call_count
        bridge.process_message("homeassistant/status", "offline")
        # offline should not trigger republish
        assert bridge.client.publish.call_count == count_before


class TestWriteVerifyFlow:
    """Test write-verify in realistic flow."""

    def test_write_then_state_update_verifies(self, bridge, caplog):
        """Write a value, then receive state update — verify match."""
        bridge.write_and_verify("680", 396, "55.0")

        with caplog.at_level(logging.INFO):
            bridge.process_message(
                "open3e/680_396_DomesticHotWaterTemperatureSetpoint", "55.0"
            )
        assert "Write verification OK" in caplog.text

    def test_write_then_different_value_warns(self, bridge, caplog):
        """Write a value, state update returns different — log warning."""
        bridge.write_and_verify("680", 396, "55.0")

        with caplog.at_level(logging.WARNING):
            bridge.process_message(
                "open3e/680_396_DomesticHotWaterTemperatureSetpoint", "50.0"
            )
        assert "Write verification FAILED" in caplog.text


class TestNRCFlow:
    """Test NRC handling in message flow."""

    def test_nrc_skips_discovery(self, bridge):
        """NRC payload does not generate discovery."""
        bridge.process_message("open3e/680_396_DomesticHotWaterTemperatureSetpoint", "NRC 0x22")

        discovery_calls = [
            c for c in bridge.client.publish.call_args_list
            if "homeassistant/" in str(c[0][0]) or "test/homeassistant/" in str(c[0][0])
        ]
        assert len(discovery_calls) == 0

    def test_nrc_increments_message_counter(self, bridge):
        """NRC messages still count as processed."""
        bridge.process_message("open3e/680_396_DomesticHotWaterTemperatureSetpoint", "NRC 0x22")
        assert bridge._messages_processed == 1

    def test_normal_after_nrc(self, bridge):
        """Normal message after NRC still works."""
        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "NRC 0x31")
        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "12.5")
        assert bridge._discovery_published >= 1


class TestCOPFlow:
    """Test COP calculation in message flow."""

    def test_cop_published_after_both_power_dids(self, bridge):
        bridge.process_message("open3e/680_2488_CurrentElectricalPowerConsumptionSystem", "1000")
        bridge.process_message("open3e/680_2496_CurrentThermalCapacitySystem", "4000")

        cop_calls = [
            c for c in bridge.client.publish.call_args_list
            if c[0][0] == "open3e/bridge/cop"
        ]
        assert len(cop_calls) >= 1
        assert float(cop_calls[-1][0][1]) == 4.0

    def test_cop_not_published_zero_electrical(self, bridge):
        bridge.process_message("open3e/680_2488_CurrentElectricalPowerConsumptionSystem", "0")
        bridge.process_message("open3e/680_2496_CurrentThermalCapacitySystem", "4000")

        cop_calls = [
            c for c in bridge.client.publish.call_args_list
            if c[0][0] == "open3e/bridge/cop"
        ]
        assert len(cop_calls) == 0
