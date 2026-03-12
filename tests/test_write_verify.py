"""Tests for A01: Write verification feature."""
import json
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


class TestWriteAndVerify:
    def test_write_publishes_write_and_read_commands(self, bridge):
        bridge.write_and_verify("680", 396, "55.0")

        calls = bridge.client.publish.call_args_list
        assert len(calls) == 2

        # First call: write command
        write_topic = calls[0].args[0]
        write_data = calls[0].args[1]
        assert write_topic == "open3e/cmnd"
        write_cmd = json.loads(write_data)
        assert write_cmd["mode"] == "write"
        assert write_cmd["data"] == [[396, "55.0"]]

        # Second call: read command
        read_topic = calls[1].args[0]
        read_data = calls[1].args[1]
        assert read_topic == "open3e/cmnd"
        read_cmd = json.loads(read_data)
        assert read_cmd["mode"] == "read"
        assert read_cmd["data"] == [396]

    def test_write_tracks_pending(self, bridge):
        bridge.write_and_verify("680", 396, "55.0")
        assert ("680", 396) in bridge._pending_writes
        assert bridge._pending_writes[("680", 396)] == "55.0"

    def test_verification_ok_logs_info(self, bridge, caplog):
        bridge._pending_writes[("680", 396)] = "55.0"
        with caplog.at_level(logging.INFO):
            bridge._check_write_verification("680", 396, "55.0")
        assert "Write verification OK" in caplog.text
        assert ("680", 396) not in bridge._pending_writes

    def test_verification_mismatch_logs_warning(self, bridge, caplog):
        bridge._pending_writes[("680", 396)] = "55.0"
        with caplog.at_level(logging.WARNING):
            bridge._check_write_verification("680", 396, "50.0")
        assert "Write verification FAILED" in caplog.text
        assert "expected=55.0" in caplog.text
        assert "actual=50.0" in caplog.text

    def test_no_pending_write_does_nothing(self, bridge, caplog):
        with caplog.at_level(logging.DEBUG):
            bridge._check_write_verification("680", 396, "55.0")
        assert "Write verification" not in caplog.text

    def test_verification_called_on_message(self, bridge):
        """When a state topic message arrives, write verification is checked."""
        bridge._pending_writes[("680", 396)] = "55.0"
        bridge.process_message(
            "open3e/680_396_DomesticHotWaterTemperatureSetpoint", "55.0"
        )
        # Pending write should be consumed
        assert ("680", 396) not in bridge._pending_writes
