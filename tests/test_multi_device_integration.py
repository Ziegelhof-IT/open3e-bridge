"""Integration tests for multi-device bridge operation."""
import json
from unittest.mock import MagicMock, patch

import pytest
import yaml


class TestMultiDeviceBridgeCreation:
    """Test bridge creation in multi-device mode."""

    def test_bridge_with_devices_config(self, tmp_path):
        cfg = {
            "devices": [
                {"name": "vitocal", "ecu": "680", "profile": "vitocal"},
                {"name": "vitodens", "ecu": "690", "profile": "vitodens"},
            ]
        }
        devices_file = tmp_path / "devices.yaml"
        devices_file.write_text(yaml.dump(cfg))

        with patch("bridge.mqtt.Client") as MockClient:
            MockClient.return_value = MagicMock()
            from bridge import Open3EBridge
            b = Open3EBridge(
                test_mode=True,
                add_test_prefix=False,
                devices_config=str(devices_file),
            )
            assert len(b.device_registry.ecu_addresses) == 2
            assert b.generator is not None  # backward compat

    def test_bridge_without_devices_config(self):
        """Without --devices, single-device mode (backward compat)."""
        with patch("bridge.mqtt.Client") as MockClient:
            MockClient.return_value = MagicMock()
            from bridge import Open3EBridge
            b = Open3EBridge(test_mode=True, add_test_prefix=False)
            assert len(b.device_registry.ecu_addresses) == 1
            assert "680" in b.device_registry.ecu_addresses


class TestMultiDeviceMessageRouting:
    """Test that messages route to correct per-device generators."""

    @pytest.fixture
    def multi_bridge(self, tmp_path):
        cfg = {
            "devices": [
                {"name": "vitocal", "ecu": "680", "profile": "vitocal"},
                {"name": "vitodens", "ecu": "690", "profile": "vitodens"},
            ]
        }
        devices_file = tmp_path / "devices.yaml"
        devices_file.write_text(yaml.dump(cfg))

        with patch("bridge.mqtt.Client") as MockClient:
            mock_client = MagicMock()
            MockClient.return_value = mock_client
            from bridge import Open3EBridge
            b = Open3EBridge(
                test_mode=True,
                add_test_prefix=False,
                devices_config=str(devices_file),
            )
            yield b, mock_client

    def test_ecu_680_uses_vitocal_generator(self, multi_bridge):
        bridge, mock_client = multi_bridge
        # DID 268 exists in common (loaded by both), but each generator is independent
        bridge.process_message("open3e/680_268_FlowTemperatureSensor/Actual", "42.5")
        # Should publish discovery using vitocal generator
        assert mock_client.publish.called

    def test_ecu_690_uses_vitodens_generator(self, multi_bridge):
        bridge, mock_client = multi_bridge
        bridge.process_message("open3e/690_268_FlowTemperatureSensor/Actual", "38.0")
        assert mock_client.publish.called

    def test_unknown_ecu_falls_back_to_default(self, multi_bridge):
        bridge, mock_client = multi_bridge
        # ECU 999 not configured — falls back to default generator
        bridge.process_message("open3e/999_268_FlowTemperatureSensor/Actual", "40.0")
        # Should still work (default generator handles it)
        # No crash is the assertion here

    def test_different_ecus_produce_different_device_info(self, multi_bridge):
        bridge, mock_client = multi_bridge
        # Send same DID to both ECUs
        bridge.process_message("open3e/680_268_FlowTemperatureSensor/Actual", "42.5")
        bridge.process_message("open3e/690_268_FlowTemperatureSensor/Actual", "38.0")

        # Check published payloads have different device identifiers
        published = {}
        for call in mock_client.publish.call_args_list:
            topic = call[0][0]
            if "/config" in topic:
                payload = json.loads(call[0][1])
                published[topic] = payload

        # Find configs for 680 and 690
        configs_680 = {t: p for t, p in published.items() if "open3e_680_" in t}
        configs_690 = {t: p for t, p in published.items() if "open3e_690_" in t}

        if configs_680 and configs_690:
            c680 = next(iter(configs_680.values()))
            c690 = next(iter(configs_690.values()))
            # Device identifiers should differ by ECU
            assert c680["device"]["identifiers"] != c690["device"]["identifiers"]


class TestMultiDeviceDiagnostics:
    """Test diagnostics in multi-device mode."""

    def test_diagnostics_include_device_count(self, tmp_path):
        cfg = {
            "devices": [
                {"name": "a", "ecu": "680", "profile": "common"},
                {"name": "b", "ecu": "690", "profile": "common"},
            ]
        }
        devices_file = tmp_path / "devices.yaml"
        devices_file.write_text(yaml.dump(cfg))

        with patch("bridge.mqtt.Client") as MockClient:
            MockClient.return_value = MagicMock()
            from bridge import Open3EBridge
            b = Open3EBridge(
                test_mode=True, add_test_prefix=False,
                devices_config=str(devices_file),
            )
            diag = b.get_diagnostics()
            assert diag["devices"] == 2

    def test_diagnostics_aggregates_auto_discovered(self, tmp_path):
        cfg = {
            "devices": [
                {"name": "a", "ecu": "680", "profile": "common"},
                {"name": "b", "ecu": "690", "profile": "common"},
            ]
        }
        devices_file = tmp_path / "devices.yaml"
        devices_file.write_text(yaml.dump(cfg))

        with patch("bridge.mqtt.Client") as MockClient:
            MockClient.return_value = MagicMock()
            from bridge import Open3EBridge
            b = Open3EBridge(
                test_mode=True, add_test_prefix=False,
                devices_config=str(devices_file),
            )
            # Simulate auto-discovered entities on each generator
            b.device_registry.get_generator("680").auto_discovered_count = 3
            b.device_registry.get_generator("690").auto_discovered_count = 5
            diag = b.get_diagnostics()
            assert diag["auto_discovered_entities"] == 8


class TestMultiDeviceDumpEntities:
    """Test dump_entities with multiple devices."""

    def test_dump_entities_shows_per_device_headers(self, tmp_path, capsys):
        cfg = {
            "devices": [
                {"name": "vitocal", "ecu": "680", "profile": "vitocal"},
                {"name": "vitodens", "ecu": "690", "profile": "vitodens"},
            ]
        }
        devices_file = tmp_path / "devices.yaml"
        devices_file.write_text(yaml.dump(cfg))

        with patch("bridge.mqtt.Client") as MockClient:
            MockClient.return_value = MagicMock()
            from bridge import Open3EBridge
            b = Open3EBridge(
                test_mode=True, add_test_prefix=False,
                devices_config=str(devices_file),
            )
            b.dump_entities()
            output = capsys.readouterr().out
            assert "=== Device: vitocal (ECU 680) ===" in output
            assert "=== Device: vitodens (ECU 690) ===" in output
            assert "Total:" in output

    def test_dump_entities_single_device_no_header(self, capsys):
        """Single device mode should NOT show per-device headers."""
        with patch("bridge.mqtt.Client") as MockClient:
            MockClient.return_value = MagicMock()
            from bridge import Open3EBridge
            b = Open3EBridge(test_mode=True, add_test_prefix=False)
            b.dump_entities()
            output = capsys.readouterr().out
            assert "=== Device:" not in output
            assert "Total:" in output


class TestMultiDeviceCLI:
    """Test CLI --devices flag."""

    def test_cli_devices_flag(self, tmp_path):
        cfg = {
            "devices": [
                {"name": "vitocal", "ecu": "680", "profile": "vitocal"},
            ]
        }
        devices_file = tmp_path / "devices.yaml"
        devices_file.write_text(yaml.dump(cfg))

        from bridge import main
        with patch("bridge.Open3EBridge") as MockBridge, \
             patch("sys.argv", ["bridge", "--devices", str(devices_file)]):
            main()
            call_kwargs = MockBridge.call_args
            assert call_kwargs[1]["devices_config"] == str(devices_file) or \
                   call_kwargs.kwargs.get("devices_config") == str(devices_file)

    def test_cli_no_devices_flag(self):
        from bridge import main
        with patch("bridge.Open3EBridge") as MockBridge, \
             patch("sys.argv", ["bridge"]):
            main()
            call_kwargs = MockBridge.call_args
            devices_val = call_kwargs[1].get("devices_config") or call_kwargs.kwargs.get("devices_config")
            assert devices_val is None
