FROM python:3.11 AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential patchelf && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt nuitka
COPY license_guard/ ./license_guard/
RUN python -m nuitka --module license_guard/guard.py --output-dir=/build/compiled

FROM python:3.11-slim AS runtime
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY model_card.yaml ./model_card.yaml
COPY app/ ./app/
COPY license_guard/__init__.py ./license_guard/__init__.py
COPY license_guard/hardware.py ./license_guard/hardware.py
COPY license_guard/public_key.py ./license_guard/public_key.py
COPY license_guard/token.py ./license_guard/token.py
COPY --from=builder /build/compiled/guard*.so ./license_guard/

LABEL aihub.package.kind="single-model-accelerator" \
      aihub.model.id="echo-model-template" \
      aihub.model.name="Echo Model Template" \
      aihub.model.version="0.1.0" \
      aihub.model.owner="example-provider" \
      aihub.accelerator="cpu" \
      aihub.hardware.minimum="CPU development environment" \
      aihub.host.runtime="none" \
      aihub.input.types="text" \
      aihub.entry.gateway="http://127.0.0.1:8080" \
      aihub.entry.api="http://127.0.0.1:8080/v1" \
      aihub.entry.webui="http://127.0.0.1:3000" \
      aihub.entry.cli="python -m app.cli --base-url http://127.0.0.1:8080" \
      aihub.license.required="true" \
      aihub.license.env="AIHUB_LICENSE_KEY" \
      aihub.security.guard="native-module" \
      aihub.security.guard.format="so"

EXPOSE 8080
CMD ["python", "-m", "app.entrypoint"]
