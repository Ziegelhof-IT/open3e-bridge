"""Tests for C04-C06: Auto-discovery integration (heuristic fallback)."""
import json


def _discover(gen, topic, value="0"):
    results = gen.generate_discovery_message(topic, value, test_mode=False)
    if not results:
        return None, None
    disc_topic, raw_payload = results[0]
    return disc_topic, json.loads(raw_payload)


class TestAutoDiscoverFlagOff:
    """When auto_discover is OFF, unknown DIDs are skipped."""

    def test_unknown_did_skipped(self, generator_en):
        # DID 99999 is not in datapoints.yaml
        topic = "open3e/680_99999_SomeUnknownSensor/Actual"
        results = generator_en.generate_discovery_message(topic, "42", test_mode=False)
        assert results == []

    def test_known_did_still_works(self, generator_en):
        # DID 268 is configured → should still produce discovery
        topic = "open3e/680_268_FlowTemperatureSensor/Actual"
        results = generator_en.generate_discovery_message(topic, "42", test_mode=False)
        assert len(results) >= 1


class TestAutoDiscoverFlagOn:
    """When auto_discover is ON, unknown DIDs get heuristic entities."""

    def test_unknown_temperature_sensor(self, generator_auto):
        topic = "open3e/680_99999_SomeTemperatureSensor/Actual"
        disc_topic, p = _discover(generator_auto, topic, "42.5")

        assert disc_topic is not None
        assert "/sensor/" in disc_topic
        assert p["name"] == "DID 99999 SomeTemperatureSensor Actual"
        assert p["device_class"] == "temperature"
        assert p["unit_of_measurement"] == "°C"
        assert p["state_class"] == "measurement"
        assert p["state_topic"] == topic
        assert p["availability_topic"] == "open3e/LWT"
        assert "origin" in p
        assert p["origin"]["name"] == "Open3E Bridge"

    def test_unknown_pressure_sensor(self, generator_auto):
        topic = "open3e/680_88888_WaterPressureSensor"
        disc_topic, p = _discover(generator_auto, topic, "2.1")

        assert "/sensor/" in disc_topic
        assert p["device_class"] == "pressure"
        assert p["unit_of_measurement"] == "bar"

    def test_unknown_power_sensor(self, generator_auto):
        topic = "open3e/680_77777_ElectricalPowerConsumption"
        disc_topic, p = _discover(generator_auto, topic, "1500")

        assert "/sensor/" in disc_topic
        assert p["device_class"] == "power"
        assert p["unit_of_measurement"] == "W"

    def test_unknown_binary_pump_status(self, generator_auto):
        topic = "open3e/680_66666_PrimaryPumpStatus/PowerState"
        disc_topic, p = _discover(generator_auto, topic, "1")

        assert "/binary_sensor/" in disc_topic
        assert p["device_class"] == "power"

    def test_unknown_setpoint_as_number(self, generator_auto):
        topic = "open3e/680_55555_SomeSetpoint"
        disc_topic, p = _discover(generator_auto, topic, "20.0")

        assert "/number/" in disc_topic
        assert p["icon"] == "mdi:target"

    def test_unknown_generic_fallback(self, generator_auto):
        """Completely unrecognizable DID name gets default sensor."""
        topic = "open3e/680_44444_XyzFooBar"
        disc_topic, p = _discover(generator_auto, topic, "123")

        assert "/sensor/" in disc_topic
        assert p["icon"] == "mdi:information-outline"
        assert "device_class" not in p

    def test_unknown_did_without_sub_item(self, generator_auto):
        """Topic with no sub-item path."""
        topic = "open3e/680_33333_FlowTemperature"
        disc_topic, p = _discover(generator_auto, topic, "35")

        assert "/sensor/" in disc_topic
        assert p["name"] == "DID 33333 FlowTemperature"
        assert p["device_class"] == "temperature"

    def test_auto_discovered_count(self, generator_auto):
        """auto_discovered_count increments for each heuristic entity."""
        assert generator_auto.auto_discovered_count == 0

        generator_auto.generate_discovery_message(
            "open3e/680_99999_SomeTemperatureSensor/Actual", "42", test_mode=False)
        assert generator_auto.auto_discovered_count == 1

        generator_auto.generate_discovery_message(
            "open3e/680_88888_PressureSensor", "2", test_mode=False)
        assert generator_auto.auto_discovered_count == 2

    def test_entity_id_format(self, generator_auto):
        topic = "open3e/680_99999_TestSensor/SubPath"
        disc_topic, p = _discover(generator_auto, topic, "1")

        assert p["unique_id"] == "open3e_680_99999_subpath"
        assert p["object_id"] == "open3e_680_99999_subpath"


class TestYamlWinsOverHeuristic:
    """Known DIDs always use YAML config, even with auto_discover ON."""

    def test_known_did_uses_yaml(self, generator_auto):
        # DID 268 is in datapoints.yaml — should use YAML config, not heuristic
        topic = "open3e/680_268_FlowTemperatureSensor/Actual"
        disc_topic, p = _discover(generator_auto, topic, "42")

        assert disc_topic is not None
        # YAML-configured name (not heuristic "DID 268 ...")
        assert not p["name"].startswith("DID 268")
        # Should still be a temperature sensor
        assert p["device_class"] == "temperature"

    def test_ignored_did_stays_ignored(self, generator_auto):
        """Ignored DIDs are skipped even with auto_discover ON."""
        ignored = generator_auto.generator.datapoints.get("ignored_dids", []) if hasattr(generator_auto, 'generator') else generator_auto.datapoints.get("ignored_dids", [])
        if not ignored:
            return  # skip if no ignored DIDs configured
        did = ignored[0]
        topic = f"open3e/680_{did}_IgnoredSensor/Actual"
        results = generator_auto.generate_discovery_message(topic, "0", test_mode=False)
        assert results == []


class TestAutoDiscoverDevice:
    """Device info in auto-discovered entities."""

    def test_device_info_present(self, generator_auto):
        topic = "open3e/680_99999_TestSensor"
        disc_topic, p = _discover(generator_auto, topic, "1")

        dev = p["device"]
        assert "identifiers" in dev
        assert any("open3e_680" in i for i in dev["identifiers"])
        assert dev["manufacturer"] == "Viessmann"

    def test_different_ecu_address(self, generator_auto):
        topic = "open3e/68C_99999_OutdoorTemperature"
        disc_topic, p = _discover(generator_auto, topic, "10")

        dev = p["device"]
        assert any("open3e_68C" in i for i in dev["identifiers"])


class TestAutoDiscoverInBridge:
    """Bridge-level integration with auto_discover flag."""

    def test_diagnostics_includes_auto_discovered(self):
        from unittest.mock import MagicMock, patch

        with patch("bridge.mqtt.Client") as mock_mqtt:
            mock_mqtt.return_value = MagicMock()
            from bridge import Open3EBridge
            bridge = Open3EBridge(auto_discover=True)
            diag = bridge.get_diagnostics()
            assert "auto_discovered_entities" in diag
            assert diag["auto_discovered_entities"] == 0

    def test_bridge_process_unknown_did_with_flag(self):
        from unittest.mock import MagicMock, patch

        with patch("bridge.mqtt.Client") as mock_mqtt:
            mock_instance = MagicMock()
            mock_mqtt.return_value = mock_instance
            from bridge import Open3EBridge
            bridge = Open3EBridge(auto_discover=True)
            bridge.process_message("open3e/680_99999_UnknownTemp/Actual", "25.5")
            # Should have published discovery
            assert bridge._discovery_published >= 1
            assert bridge.generator.auto_discovered_count >= 1

    def test_bridge_process_unknown_did_without_flag(self):
        from unittest.mock import MagicMock, patch

        with patch("bridge.mqtt.Client") as mock_mqtt:
            mock_mqtt.return_value = MagicMock()
            from bridge import Open3EBridge
            bridge = Open3EBridge(auto_discover=False)
            bridge.process_message("open3e/680_99999_UnknownTemp/Actual", "25.5")
            # Should NOT have published discovery
            assert bridge._discovery_published == 0
