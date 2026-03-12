"""Tests for A08: COP calculation feature."""
import json
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def bridge():
    with patch("bridge.mqtt.Client") as MockClient:
        MockClient.return_value = MagicMock()
        from bridge import Open3EBridge
        b = Open3EBridge()
        return b


class TestCOPCalculation:
    def test_cop_calculated_when_both_values_present(self, bridge):
        bridge._electrical_power = 1000.0
        bridge._thermal_power = 4000.0
        bridge._update_cop(2488, "1000")  # triggers recalc with existing values

        # Should publish COP
        bridge.client.publish.assert_called_with(
            "open3e/bridge/cop", "4.0", retain=True
        )

    def test_cop_not_published_when_electrical_zero(self, bridge):
        bridge._thermal_power = 4000.0
        bridge._update_cop(2488, "0")

        bridge.client.publish.assert_not_called()

    def test_cop_not_published_when_only_one_value(self, bridge):
        bridge._update_cop(2488, "1000")
        bridge.client.publish.assert_not_called()

        bridge._update_cop(2496, "4000")
        # Now both values are present
        bridge.client.publish.assert_called_once()

    def test_cop_precision(self, bridge):
        bridge._electrical_power = 1500.0
        bridge._update_cop(2496, "5000")

        call_args = bridge.client.publish.call_args
        cop_value = float(call_args[0][1])
        assert cop_value == pytest.approx(3.33, abs=0.01)

    def test_cop_ignores_invalid_value(self, bridge):
        bridge._update_cop(2488, "not_a_number")
        assert bridge._electrical_power is None

    def test_cop_ignores_unrelated_did(self, bridge):
        bridge._update_cop(999, "1000")
        assert bridge._electrical_power is None
        assert bridge._thermal_power is None

    def test_cop_updated_via_process_message(self, bridge):
        bridge.process_message("open3e/680_2488_CurrentElectricalPowerConsumptionSystem", "1000")
        assert bridge._electrical_power == 1000.0

        bridge.process_message("open3e/680_2496_CurrentThermalCapacitySystem", "4000")
        assert bridge._thermal_power == 4000.0

        # COP should have been published
        cop_calls = [c for c in bridge.client.publish.call_args_list if c[0][0] == "open3e/bridge/cop"]
        assert len(cop_calls) >= 1

    def test_cop_discovery_published_on_connect(self, bridge):
        """COP discovery config is published when bridge connects."""
        bridge._on_connect(bridge.client, None, None, 0, None)

        # Find COP discovery publish
        cop_discovery_calls = [
            c for c in bridge.client.publish.call_args_list
            if "open3e_bridge_cop" in str(c)
        ]
        assert len(cop_discovery_calls) >= 1
        payload = json.loads(cop_discovery_calls[0][0][1])
        assert payload["unique_id"] == "open3e_bridge_cop"
        assert payload["state_topic"] == "open3e/bridge/cop"
        assert payload["device_class"] == "power_factor"
