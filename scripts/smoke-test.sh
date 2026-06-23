#!/usr/bin/env sh
set -eu
BASE_URL="${BASE_URL:-http://127.0.0.1:8080}"
curl "$BASE_URL/healthz"
curl "$BASE_URL/v1/models"
python -m app.cli --base-url "$BASE_URL" --prompt "hello"
