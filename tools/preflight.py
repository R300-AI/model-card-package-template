import argparse
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Sequence

from tools.generate_oci_labels import format_plain
from tools.validate_config import expected_image_uri, expected_oci_labels, load_yaml, validate_config, validate_publish_environment

PUBLISH_ENV_NAMES = [
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


def print_section(title: str) -> None:
    print(f"\n== {title} ==")


def collect_config_errors(model_card_path: Path) -> List[str]:
    config = load_yaml(model_card_path)
    return validate_config(config)


def collect_label_errors(model_card_path: Path) -> List[str]:
    config = load_yaml(model_card_path)
    labels = expected_oci_labels(config)
    if not labels:
        return ["No OCI labels were generated from model_card.yaml."]
    return []


def run_pytest(extra_args: Sequence[str]) -> int:
    command = [sys.executable, "-m", "pytest", "-q", *extra_args]
    return subprocess.run(command, check=False).returncode


def print_errors(errors: Iterable[str]) -> None:
    for error in errors:
        print(f"ERROR: {error}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AI Hub Model Card package preflight checks.")
    parser.add_argument("--model-card", default="model_card.yaml")
    parser.add_argument("--check-publish-env", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--pytest-arg", action="append", default=[])
    args = parser.parse_args()

    model_card_path = Path(args.model_card)
    if not model_card_path.exists():
        print(f"ERROR: {model_card_path} does not exist.")
        return 1

    exit_code = 0

    print_section("Config")
    config_errors = collect_config_errors(model_card_path)
    if config_errors:
        print_errors(config_errors)
        exit_code = 1
    else:
        config = load_yaml(model_card_path)
        print(f"OK: {expected_image_uri(config)}")

    print_section("OCI labels")
    label_errors = collect_label_errors(model_card_path)
    if label_errors:
        print_errors(label_errors)
        exit_code = 1
    else:
        config = load_yaml(model_card_path)
        print(format_plain(expected_oci_labels(config)))

    if args.check_publish_env:
        print_section("Publish environment")
        missing = validate_publish_environment(PUBLISH_ENV_NAMES)
        if missing:
            print_errors([f"Missing GitHub Actions variable or secret: {name}" for name in missing])
            exit_code = 1
        else:
            print("OK: all publish environment names are present.")

    if not args.skip_tests:
        print_section("Tests")
        pytest_code = run_pytest(args.pytest_arg)
        if pytest_code != 0:
            exit_code = pytest_code

    if exit_code == 0:
        print("\nPreflight OK. The package is ready for local review or GitHub Actions publish.")
    else:
        print("\nPreflight failed. Fix the first ERROR above, then run this command again.")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
