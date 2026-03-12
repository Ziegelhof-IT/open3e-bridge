"""Tests for A09: NRC (Negative Response Code) handling."""
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


class TestNRCDetection:
    def test_nrc_hex_detected(self, bridge):
        assert bridge._is_nrc_payload("NRC 0x22") is True

    def test_nrc_named_detected(self, bridge):
        assert bridge._is_nrc_payload("ConditionsNotCorrect") is True
        assert bridge._is_nrc_payload("RequestOutOfRange") is True

    def test_normal_payload_not_nrc(self, bridge):
        assert bridge._is_nrc_payload("12.5") is False
        assert bridge._is_nrc_payload("0") is False
        assert bridge._is_nrc_payload("online") is False

    def test_empty_payload_not_nrc(self, bridge):
        assert bridge._is_nrc_payload("") is False


class TestNRCHandling:
    def test_nrc_logged_with_code(self, bridge, caplog):
        with caplog.at_level(logging.WARNING):
            result = bridge._handle_nrc("open3e/680_396_DHW", "NRC 0x22")
        assert result is True
        assert "ConditionsNotCorrect" in caplog.text

    def test_nrc_logged_unknown_code(self, bridge, caplog):
        with caplog.at_level(logging.WARNING):
            result = bridge._handle_nrc("open3e/680_396_DHW", "NRC 0xFF")
        assert result is True
        assert "Unknown NRC" in caplog.text

    def test_nrc_logged_named(self, bridge, caplog):
        with caplog.at_level(logging.WARNING):
            result = bridge._handle_nrc("open3e/680_396_DHW", "ConditionsNotCorrect")
        assert result is True
        assert "NRC on" in caplog.text

    def test_normal_payload_passes(self, bridge):
        result = bridge._handle_nrc("open3e/680_396_DHW", "55.0")
        assert result is False

    def test_nrc_skips_discovery_generation(self, bridge):
        """NRC payload should not generate discovery messages."""
        bridge.process_message("open3e/680_396_DomesticHotWaterTemperatureSetpoint", "NRC 0x31")
        # No discovery should be published (only NRC log)
        discovery_calls = [
            c for c in bridge.client.publish.call_args_list
            if "homeassistant/" in str(c) or "test/homeassistant/" in str(c)
        ]
        assert len(discovery_calls) == 0


class TestNRCCodes:
    def test_known_codes(self, bridge):
        assert "ConditionsNotCorrect" in bridge._nrc_codes["0x22"]
        assert "RequestOutOfRange" in bridge._nrc_codes["0x31"]
        assert "ResponseTooLong" in bridge._nrc_codes["0x14"]
        assert "SecurityAccessDenied" in bridge._nrc_codes["0x33"]
