#!/usr/bin/env sh
set -eu
IMAGE_NAME="${IMAGE_NAME:-model-cards.azurecr.io/example/cpu/echo-model-template:0.1.0}"
docker build -t "$IMAGE_NAME" .
