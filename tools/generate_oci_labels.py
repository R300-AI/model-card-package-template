import argparse
from pathlib import Path
from typing import Dict

from tools.validate_config import expected_oci_labels, load_yaml


def format_plain(labels: Dict[str, str]) -> str:
    return "\n".join(f"{key}={value}" for key, value in sorted(labels.items()))


def format_docker_build_args(labels: Dict[str, str]) -> str:
    return "\n".join(f"--label={key}={value}" for key, value in sorted(labels.items()))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate AI Hub OCI labels from model_card.yaml.")
    parser.add_argument("--model-card", default="model_card.yaml")
    parser.add_argument("--format", choices=("plain", "docker-build-args"), default="plain")
    args = parser.parse_args()

    config = load_yaml(Path(args.model_card))
    labels = expected_oci_labels(config)

    if args.format == "docker-build-args":
        print(format_docker_build_args(labels))
    else:
        print(format_plain(labels))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
