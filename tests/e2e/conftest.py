"""E2E test fixtures — session-scoped Mosquitto Docker container."""

import socket
import tempfile
import time

import pytest

try:
    import docker
except ImportError:
    docker = None

MOSQUITTO_PORT = 11883
MOSQUITTO_IMAGE = "eclipse-mosquitto:2"

_MOSQUITTO_CONF = "listener 1883\nallow_anonymous true\n"


@pytest.fixture(scope="session")
def mqtt_broker():
    """Start a Mosquitto MQTT broker in Docker for E2E tests."""
    if docker is None:
        pytest.skip("docker package not installed (pip install docker)")

    client = docker.from_env()

    # Write minimal config that enables anonymous access (required since Mosquitto 2.0)
    conf_file = tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False)
    conf_file.write(_MOSQUITTO_CONF)
    conf_file.flush()
    conf_path = conf_file.name
    conf_file.close()

    container = client.containers.run(
        MOSQUITTO_IMAGE,
        command="mosquitto -c /mosquitto/config/mosquitto.conf -v",
        ports={"1883/tcp": MOSQUITTO_PORT},
        volumes={conf_path: {"bind": "/mosquitto/config/mosquitto.conf", "mode": "ro"}},
        detach=True,
        remove=True,
    )

    # Wait for broker to accept connections
    for _ in range(30):
        try:
            s = socket.create_connection(("localhost", MOSQUITTO_PORT), timeout=1)
            s.close()
            break
        except OSError:
            time.sleep(0.5)
    else:
        container.stop()
        pytest.fail("Mosquitto did not start within 15 seconds")

    yield {"host": "localhost", "port": MOSQUITTO_PORT}

    container.stop()

    import os
    os.unlink(conf_path)
