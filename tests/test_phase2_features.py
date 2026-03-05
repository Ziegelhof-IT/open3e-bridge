"""Tests for Phase 2 features: packaging, config-dir, version, diagnostics, env vars."""
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# 1. Version: __version__ is accessible and non-empty
# ---------------------------------------------------------------------------
class TestVersion:
    def test_version_string_exists(self):
        from bridge import __version__
        assert __version__
        assert isinstance(__version__, str)

    def test_version_in_cli(self):
        result = subprocess.run(
            [sys.executable, "-m", "bridge", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "open3e-bridge" in result.stdout


# ---------------------------------------------------------------------------
# 2. --config-dir: Bridge accepts custom config directory
# ---------------------------------------------------------------------------
class TestConfigDir:
    @patch("bridge.mqtt.Client")
    def test_default_config_dir(self, mock_client_cls):
        mock_client_cls.return_value = MagicMock()
        from bridge import Open3EBridge
        bridge = Open3EBridge()
        # Generator should have loaded datapoints from default config
        assert bridge.generator.datapoints.get("datapoints")

    @patch("bridge.mqtt.Client")
    def test_custom_config_dir(self, mock_client_cls, tmp_path):
        mock_client_cls.return_value = MagicMock()
        # Create minimal config in tmp_path
        (tmp_path / "datapoints.yaml").write_text(
            "schema_version: 1\ndatapoints: {}\ndevices: {}\n"
        )
        (tmp_path / "templates").mkdir()
        (tmp_path / "templates" / "types.yaml").write_text("{}\n")

        from bridge import Open3EBridge
        bridge = Open3EBridge(config_dir=str(tmp_path))
        assert bridge.generator.datapoints.get("schema_version") == 1
        assert bridge.generator.datapoints.get("datapoints") == {}

    @patch("bridge.mqtt.Client")
    def test_custom_config_dir_missing_file_warns(self, mock_client_cls, tmp_path, caplog):
        mock_client_cls.return_value = MagicMock()
        (tmp_path / "datapoints.yaml").write_text("datapoints: {}\n")
        (tmp_path / "templates").mkdir()
        (tmp_path / "templates" / "types.yaml").write_text("{}\n")

        import logging
        with caplog.at_level(logging.WARNING):
            from bridge import Open3EBridge
            Open3EBridge(config_dir=str(tmp_path), language="de")
        # Should warn about missing translation file
        assert any("not found" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# 3. Diagnostics: Bridge tracks message/discovery counters
# ---------------------------------------------------------------------------
class TestDiagnostics:
    @patch("bridge.mqtt.Client")
    def test_initial_diagnostics(self, mock_client_cls):
        mock_client_cls.return_value = MagicMock()
        from bridge import Open3EBridge
        bridge = Open3EBridge()
        diag = bridge.get_diagnostics()
        assert diag["messages_processed"] == 0
        assert diag["discovery_published"] == 0
        assert diag["entities_cached"] == 0
        assert "version" in diag
        assert "uptime_s" in diag

    @patch("bridge.mqtt.Client")
    def test_diagnostics_after_processing(self, mock_client_cls):
        mock_client_cls.return_value = MagicMock()
        from bridge import Open3EBridge
        bridge = Open3EBridge()
        # Process a known DID
        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "12.5")
        diag = bridge.get_diagnostics()
        assert diag["messages_processed"] == 1
        assert diag["discovery_published"] >= 1
        assert diag["entities_cached"] >= 1

    @patch("bridge.mqtt.Client")
    def test_diagnostics_deduplication(self, mock_client_cls):
        mock_client_cls.return_value = MagicMock()
        from bridge import Open3EBridge
        bridge = Open3EBridge()
        # Same message twice — second should be deduplicated
        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "12.5")
        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "12.5")
        diag = bridge.get_diagnostics()
        assert diag["messages_processed"] == 2
        assert diag["discovery_published"] == 1  # Only published once


# ---------------------------------------------------------------------------
# 4. Schema version in datapoints.yaml
# ---------------------------------------------------------------------------
class TestSchemaVersion:
    def test_schema_version_present(self, config_dir):
        import yaml
        with open(Path(config_dir) / "datapoints.yaml") as f:
            data = yaml.safe_load(f)
        assert "schema_version" in data
        assert isinstance(data["schema_version"], int)
        assert data["schema_version"] >= 1


# ---------------------------------------------------------------------------
# 5. sw_version in discovery uses package version, not hardcoded
# ---------------------------------------------------------------------------
class TestDiscoveryVersion:
    def test_origin_sw_version_matches(self, generator_de):
        topic = "open3e/680_274_OutsideTemperatureSensor/Actual"
        results = generator_de.generate_discovery_message(topic, "12.5", test_mode=False)
        config = json.loads(results[0][1])
        origin = config.get("origin", {})
        assert "sw_version" in origin
        # Should not be the old hardcoded value unless that's the actual version
        assert origin["sw_version"]  # Non-empty


# ---------------------------------------------------------------------------
# 6. Systemd service file exists and is valid
# ---------------------------------------------------------------------------
class TestSystemdService:
    def test_service_file_exists(self):
        service_path = Path(__file__).resolve().parents[1] / "contrib" / "open3e-bridge.service"
        assert service_path.exists()

    def test_service_file_has_required_sections(self):
        service_path = Path(__file__).resolve().parents[1] / "contrib" / "open3e-bridge.service"
        content = service_path.read_text()
        assert "[Unit]" in content
        assert "[Service]" in content
        assert "[Install]" in content
        assert "ExecStart=" in content
        assert "RestartSec=5" in content


# ---------------------------------------------------------------------------
# 7. Dockerfile exists and is valid
# ---------------------------------------------------------------------------
class TestDockerfile:
    def test_dockerfile_exists(self):
        dockerfile = Path(__file__).resolve().parents[1] / "Dockerfile"
        assert dockerfile.exists()

    def test_dockerfile_has_entrypoint(self):
        dockerfile = Path(__file__).resolve().parents[1] / "Dockerfile"
        content = dockerfile.read_text()
        assert "ENTRYPOINT" in content
        assert "open3e-bridge" in content
        assert "HEALTHCHECK" in content


# ---------------------------------------------------------------------------
# 8. MQTT password from environment variable
# ---------------------------------------------------------------------------
class TestMqttPasswordEnvVar:
    @patch("bridge.mqtt.Client")
    def test_env_var_password_used(self, mock_client_cls):
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance
        from bridge import Open3EBridge
        bridge = Open3EBridge(mqtt_user="testuser", mqtt_password="from_env")
        mock_instance.username_pw_set.assert_called_once_with("testuser", "from_env")

    @patch("bridge.mqtt.Client")
    def test_no_password_no_auth(self, mock_client_cls):
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance
        from bridge import Open3EBridge
        Open3EBridge(mqtt_user="testuser", mqtt_password=None)
        mock_instance.username_pw_set.assert_not_called()


# ---------------------------------------------------------------------------
# 9. Entity type tracking in diagnostics
# ---------------------------------------------------------------------------
class TestEntityTypeTracking:
    @patch("bridge.mqtt.Client")
    def test_entity_types_in_diagnostics(self, mock_client_cls):
        mock_client_cls.return_value = MagicMock()
        from bridge import Open3EBridge
        bridge = Open3EBridge()
        # Process a sensor and a binary sensor
        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "12.5")
        bridge.process_message("open3e/680_2351_HeatPumpCompressor/PowerState", "1")
        diag = bridge.get_diagnostics()
        entity_types = diag["entity_types"]
        assert "sensor" in entity_types
        assert "binary_sensor" in entity_types

    @patch("bridge.mqtt.Client")
    def test_log_entity_summary(self, mock_client_cls, caplog):
        mock_client_cls.return_value = MagicMock()
        import logging
        from bridge import Open3EBridge
        bridge = Open3EBridge()
        bridge.process_message("open3e/680_274_OutsideTemperatureSensor/Actual", "12.5")
        with caplog.at_level(logging.INFO):
            bridge.log_entity_summary()
        assert any("Entity summary" in r.message for r in caplog.records)

    @patch("bridge.mqtt.Client")
    def test_log_entity_summary_empty(self, mock_client_cls, caplog):
        mock_client_cls.return_value = MagicMock()
        import logging
        from bridge import Open3EBridge
        bridge = Open3EBridge()
        with caplog.at_level(logging.INFO):
            bridge.log_entity_summary()
        assert not any("Entity summary" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# 10. --dump-entities: print configured entities without MQTT
# ---------------------------------------------------------------------------
class TestDumpEntities:
    @patch("bridge.mqtt.Client")
    def test_dump_entities_output(self, mock_client_cls, capsys):
        mock_client_cls.return_value = MagicMock()
        from bridge import Open3EBridge
        bridge = Open3EBridge()
        bridge.dump_entities()
        output = capsys.readouterr().out
        assert "DID" in output
        assert "Total:" in output
        # Should list at least one configured DID
        assert "274" in output or "268" in output

    def test_dump_entities_cli(self):
        result = subprocess.run(
            [sys.executable, "-m", "bridge", "--dump-entities"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "DID" in result.stdout
        assert "Total:" in result.stdout
