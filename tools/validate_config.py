import argparse
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

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


def validate_config(config: Dict[str, Any], labels: Dict[str, str]) -> List[str]:
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
    if labels.get("aihub.model.id") != model_id:
        errors.append("Dockerfile label aihub.model.id must match model_card.yaml model.id.")

    if labels.get("aihub.model.name") != model.get("name"):
        errors.append("Dockerfile label aihub.model.name must match model.name.")

    if labels.get("aihub.model.version") != model.get("version"):
        errors.append("Dockerfile label aihub.model.version must match model.version.")

    if labels.get("aihub.model.owner") != model.get("owner"):
        errors.append("Dockerfile label aihub.model.owner must match model.owner.")

    if labels.get("aihub.accelerator") != deployment.get("accelerator"):
        errors.append("Dockerfile label aihub.accelerator must match deployment.accelerator.")

    if labels.get("aihub.host.runtime") != deployment.get("host_runtime"):
        errors.append("Dockerfile label aihub.host.runtime must match deployment.host_runtime.")

    input_types = model.get("input_types") or []
    if labels.get("aihub.input.types") != ",".join(input_types):
        errors.append("Dockerfile label aihub.input.types must match model.input_types.")

    for label_name, expected_value in REQUIRED_LABELS.items():
        if labels.get(label_name) != expected_value:
            errors.append(f"Dockerfile label {label_name} must be {expected_value}.")

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

    return errors


def validate_publish_environment(required_names: Iterable[str]) -> List[str]:
    import os

    return [name for name in required_names if not os.getenv(name)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AI Hub Model Card package configuration.")
    parser.add_argument("--model-card", default="model_card.yaml")
    parser.add_argument("--dockerfile", default="Dockerfile")
    parser.add_argument("--check-publish-env", action="store_true")
    args = parser.parse_args()

    config = load_yaml(Path(args.model_card))
    labels = parse_dockerfile_labels(Path(args.dockerfile))
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
