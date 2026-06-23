import argparse
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml


REQUIRED_FEATURES = {"api"}
REQUIRED_LABELS = {
    "aihub.package.kind": "single-model-accelerator",
    "aihub.license.required": "true",
    "aihub.license.env": "AIHUB_LICENSE_KEY",
    "aihub.security.guard": "native-module",
    "aihub.security.guard.format": "so",
}


class ConfigValidationError(ValueError):
    pass


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


def parse_dockerfile_labels(path: Path) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8")
    labels: Dict[str, str] = {}
    for key, value in re.findall(r'(aihub\.[A-Za-z0-9_.-]+)="([^"]*)"', text):
        labels[key] = value
    return labels


def expected_image_repository(config: Dict[str, Any]) -> str:
    image = config["image"]
    return str(image["repository"]).strip("/")


def expected_image_tag(config: Dict[str, Any]) -> str:
    return str(config["image"]["tag"])


def expected_image_uri(config: Dict[str, Any]) -> str:
    image = config["image"]
    return f"{image['registry'].rstrip('/')}/{expected_image_repository(config)}:{expected_image_tag(config)}"


def expected_oci_labels(config: Dict[str, Any]) -> Dict[str, str]:
    model = config["model"]
    deployment = config["deployment"]
    license_config = config["license"]
    gateway_url = f"http://127.0.0.1:{deployment['gateway_port']}"

    labels = {
        "aihub.package.kind": "single-model-accelerator",
        "aihub.model.id": str(model["id"]),
        "aihub.model.name": str(model["name"]),
        "aihub.model.version": str(model["version"]),
        "aihub.model.owner": str(model["owner"]),
        "aihub.accelerator": str(deployment["accelerator"]),
        "aihub.hardware.minimum": str(deployment["hardware_minimum"]),
        "aihub.host.runtime": str(deployment["host_runtime"]),
        "aihub.input.types": ",".join(model["input_types"]),
        "aihub.entry.gateway": gateway_url,
        "aihub.entry.api": f"{gateway_url}/v1",
        "aihub.entry.webui": f"http://127.0.0.1:{deployment['webui_port']}",
        "aihub.entry.cli": f"python -m app.cli --base-url {gateway_url}",
        "aihub.license.required": str(license_config["required"]).lower(),
        "aihub.license.env": str(license_config["env"]),
        "aihub.security.guard": "native-module",
        "aihub.security.guard.format": "so",
    }
    return labels


def validate_config(config: Dict[str, Any], labels: Optional[Dict[str, str]] = None) -> List[str]:
    errors: List[str] = []

    model = config.get("model") or {}
    deployment = config.get("deployment") or {}
    license_config = config.get("license") or {}
    image = config.get("image") or {}

    for section_name, section in (("model", model), ("deployment", deployment), ("license", license_config), ("image", image)):
        if not section:
            errors.append(f"Missing `{section_name}` section in model_card.yaml.")

    model_id = model.get("id")
    if not model_id:
        errors.append("Missing model.id.")

    features = set(license_config.get("features") or [])
    missing_features = sorted(REQUIRED_FEATURES - features)
    if missing_features:
        errors.append(f"license.features must include: {', '.join(missing_features)}.")

    if "webui" in features and not deployment.get("webui_compose_file"):
        errors.append("deployment.webui_compose_file is required when license.features includes webui.")

    if license_config.get("env") != "AIHUB_LICENSE_KEY":
        errors.append("license.env must be AIHUB_LICENSE_KEY.")

    for key in ("registry", "repository", "tag"):
        if not image.get(key):
            errors.append(f"image.{key} is required.")

    for key in ("gateway_port", "webui_port", "hardware_minimum"):
        if not deployment.get(key):
            errors.append(f"deployment.{key} is required.")

    if not errors and labels is not None:
        for label_name, expected_value in expected_oci_labels(config).items():
            if labels.get(label_name) != expected_value:
                errors.append(f"OCI label {label_name} must be {expected_value}.")

    return errors


def validate_publish_environment(required_names: Iterable[str]) -> List[str]:
    import os

    return [name for name in required_names if not os.getenv(name)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AI Hub Model Card package configuration.")
    parser.add_argument("--model-card", default="model_card.yaml")
    parser.add_argument("--dockerfile", default="Dockerfile")
    parser.add_argument("--check-dockerfile-labels", action="store_true")
    parser.add_argument("--check-publish-env", action="store_true")
    args = parser.parse_args()

    config = load_yaml(Path(args.model_card))
    labels = parse_dockerfile_labels(Path(args.dockerfile)) if args.check_dockerfile_labels else None
    errors = validate_config(config, labels)

    if args.check_publish_env:
        missing = validate_publish_environment(
            [
                "AIHUB_ACR_LOGIN_SERVER",
                "AIHUB_IMAGE_REPOSITORY",
                "AIHUB_IMAGE_TAG",
                "AIHUB_CARD_ID",
                "AIHUB_PUBLISH_GRANT_ID",
                "AIHUB_CALLBACK_URL",
                "AIHUB_ACR_USERNAME",
                "AIHUB_ACR_PASSWORD",
                "AIHUB_CALLBACK_TOKEN",
            ]
        )
        if missing:
            errors.append(f"Missing publish environment variables or secrets: {', '.join(missing)}.")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Configuration OK: {expected_image_uri(config)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
