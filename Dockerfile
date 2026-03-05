FROM python:3.12-slim

LABEL org.opencontainers.image.title="open3e-bridge" \
      org.opencontainers.image.description="Open3E Home Assistant MQTT Discovery Bridge" \
      org.opencontainers.image.source="https://github.com/open3e/open3e-bridge"

WORKDIR /app

COPY pyproject.toml .
COPY bridge.py .
COPY generators/ generators/
COPY config/ config/

RUN pip install --no-cache-dir .

HEALTHCHECK --interval=60s --timeout=5s --start-period=10s \
  CMD ["open3e-bridge", "--validate-config"]

ENTRYPOINT ["open3e-bridge"]
CMD ["--mqtt-host", "localhost", "--language", "de"]
