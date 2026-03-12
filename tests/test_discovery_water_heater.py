"""Tests for A05/A06: water_heater discovery generation."""
import json


class TestWaterHeaterDiscovery:
    def test_water_heater_discovery_generated(self, generator_de):
        """DID 531 triggers water_heater discovery."""
        results = generator_de.generate_discovery_message(
            "open3e/680_531_DomesticHotWaterOperationState", "1", test_mode=False
        )
        # Should have typed discovery (generic_sensor) + water_heater entity
        wh_results = [(t, p) for t, p in results if "water_heater" in t]
        assert len(wh_results) == 1

    def test_water_heater_has_required_fields(self, generator_de):
        results = generator_de.generate_discovery_message(
            "open3e/680_531_DomesticHotWaterOperationState", "1", test_mode=False
        )
        wh_results = [(t, p) for t, p in results if "water_heater" in t]
        assert len(wh_results) == 1

        config = json.loads(wh_results[0][1])
        # Required HA water_heater fields
        assert "name" in config
        assert "unique_id" in config
        assert "modes" in config
        assert "mode_state_topic" in config
        assert "mode_command_topic" in config
        assert "temperature_command_topic" in config
        assert "current_temperature_topic" in config
        assert "temperature_state_topic" in config

    def test_water_heater_modes(self, generator_de):
        results = generator_de.generate_discovery_message(
            "open3e/680_531_DomesticHotWaterOperationState", "0", test_mode=False
        )
        wh_results = [(t, p) for t, p in results if "water_heater" in t]
        config = json.loads(wh_results[0][1])
        assert config["modes"] == ["off", "eco", "performance"]

    def test_water_heater_temperature_range(self, generator_de):
        results = generator_de.generate_discovery_message(
            "open3e/680_531_DomesticHotWaterOperationState", "1", test_mode=False
        )
        wh_results = [(t, p) for t, p in results if "water_heater" in t]
        config = json.loads(wh_results[0][1])
        assert config["min_temp"] == 10
        assert config["max_temp"] == 60
        assert config["precision"] == 0.5
        assert config["temperature_unit"] == "C"

    def test_water_heater_topics_correct(self, generator_de):
        results = generator_de.generate_discovery_message(
            "open3e/680_531_DomesticHotWaterOperationState", "1", test_mode=False
        )
        wh_results = [(t, p) for t, p in results if "water_heater" in t]
        config = json.loads(wh_results[0][1])

        assert config["current_temperature_topic"] == "open3e/680_271_DomesticHotWaterSensor/Actual"
        assert config["temperature_state_topic"] == "open3e/680_396_DomesticHotWaterTemperatureSetpoint"
        assert config["mode_state_topic"] == "open3e/680_531_DomesticHotWaterOperationState"
        assert config["mode_command_topic"] == "open3e/cmnd"
        assert config["temperature_command_topic"] == "open3e/cmnd"

    def test_water_heater_has_templates(self, generator_de):
        results = generator_de.generate_discovery_message(
            "open3e/680_531_DomesticHotWaterOperationState", "1", test_mode=False
        )
        wh_results = [(t, p) for t, p in results if "water_heater" in t]
        config = json.loads(wh_results[0][1])

        assert "mode_state_template" in config
        assert "mode_command_template" in config
        assert "temperature_command_template" in config

    def test_water_heater_german_name(self, generator_de):
        results = generator_de.generate_discovery_message(
            "open3e/680_531_DomesticHotWaterOperationState", "1", test_mode=False
        )
        wh_results = [(t, p) for t, p in results if "water_heater" in t]
        config = json.loads(wh_results[0][1])
        assert config["name"] == "Warmwasser"

    def test_water_heater_english_name(self, generator_en):
        results = generator_en.generate_discovery_message(
            "open3e/680_531_DomesticHotWaterOperationState", "1", test_mode=False
        )
        wh_results = [(t, p) for t, p in results if "water_heater" in t]
        config = json.loads(wh_results[0][1])
        assert config["name"] == "Hot Water"

    def test_water_heater_has_origin(self, generator_de):
        results = generator_de.generate_discovery_message(
            "open3e/680_531_DomesticHotWaterOperationState", "1", test_mode=False
        )
        wh_results = [(t, p) for t, p in results if "water_heater" in t]
        config = json.loads(wh_results[0][1])
        assert "origin" in config
        assert config["origin"]["name"] == "Open3E Bridge"

    def test_water_heater_has_device(self, generator_de):
        results = generator_de.generate_discovery_message(
            "open3e/680_531_DomesticHotWaterOperationState", "1", test_mode=False
        )
        wh_results = [(t, p) for t, p in results if "water_heater" in t]
        config = json.loads(wh_results[0][1])
        assert "device" in config
        assert "identifiers" in config["device"]
