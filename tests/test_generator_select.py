import json
import sys
from pathlib import Path


# Make open3e-bridge importable
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generators.homeassistant import HomeAssistantGenerator  # noqa: E402


def test_select_discovery_for_operation_mode():
    gen = HomeAssistantGenerator(config_dir=str(ROOT / "config"), language="en", discovery_prefix="homeassistant")

    topic = "open3e/680_1415_MixerOneCircuitOperationState/Mode/ID"
    value = "1"

    out = gen.generate_discovery_message(topic, value, test_mode=True)
    # Should produce exactly one discovery config for a select entity
    assert len(out) == 1

    disc_topic, payload = out[0]
    assert disc_topic.startswith("test/homeassistant/select/open3e_680_1415_mode_id/config")

    data = json.loads(payload)
    assert data["name"].lower().startswith("circuit 1 operation mode")
    assert data["unique_id"] == "open3e_680_1415_mode_id"
    assert data["object_id"] == "open3e_680_1415_mode_id"
    assert data["state_topic"] == topic
    assert data["options"] == ["off", "auto"]
    # value/command templates should be present per datapoints.yaml
    assert "value_template" in data
    assert "command_template" in data

