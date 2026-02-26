"""Error handling edge-case tests (TEST-08)."""
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# 1. Malformed topics -> empty list
# ---------------------------------------------------------------------------

class TestMalformedTopics:

    @pytest.mark.parametrize("topic", [
        "",
        "not_open3e/foo",
        "open3e/invalid",
        "open3e/",
    ])
    def test_malformed_topic_returns_empty(self, generator_en, topic):
        result = generator_en.generate_discovery_message(topic, "42")
        assert result == []


# ---------------------------------------------------------------------------
# 2. Unknown DID -> empty list
# ---------------------------------------------------------------------------

class TestUnknownDid:

    def test_unknown_did_returns_empty(self, generator_en):
        result = generator_en.generate_discovery_message(
            "open3e/680_99999_UnknownSensor/Actual", "123"
        )
        assert result == []


# ---------------------------------------------------------------------------
# 3. Ignored DID -> empty list
# ---------------------------------------------------------------------------

class TestIgnoredDid:

    def test_ignored_did_540_returns_empty(self, generator_en):
        result = generator_en.generate_discovery_message(
            "open3e/680_540_SomeIgnoredSensor/Actual", "1"
        )
        assert result == []


# ---------------------------------------------------------------------------
# 4. Non-UTF-8 payload in bridge._on_message
# ---------------------------------------------------------------------------

class TestBridgeNonUtf8:

    def test_non_utf8_payload_does_not_raise(self):
        with patch("paho.mqtt.client.Client") as MockClient:
            MockClient.return_value = MagicMock()
            from bridge import Open3EBridge
            bridge = Open3EBridge(test_mode=True)

        msg = MagicMock()
        msg.topic = "open3e/680_268_FlowTemperatureSensor/Actual"
        msg.payload = b"\xff\xfe\x80\x81"  # invalid UTF-8

        # Should be caught by UnicodeDecodeError handler, not raise
        bridge._on_message(None, None, msg)


# ---------------------------------------------------------------------------
# 5. Empty payload -> no crash
# ---------------------------------------------------------------------------

class TestEmptyPayload:

    def test_empty_string_value_no_crash(self, generator_en):
        result = generator_en.generate_discovery_message(
            "open3e/680_268_FlowTemperatureSensor/Actual", ""
        )
        # Should not raise; may or may not produce output
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# 6. Missing sub_item for complex DID
# ---------------------------------------------------------------------------

class TestMissingSubItem:

    def test_complex_did_without_sub_item(self, generator_en):
        """DID 268 has subs defined but topic has no sub_item path."""
        result = generator_en.generate_discovery_message(
            "open3e/680_268_FlowTemperatureSensor", "22.5"
        )
        # Should not crash; generator decides whether to produce output
        assert isinstance(result, list)
