from pathlib import Path

from tools.generate_oci_labels import format_docker_build_args
from tools.validate_config import expected_image_uri, expected_oci_labels, load_yaml, validate_config


def test_current_template_config_is_valid():
    config = load_yaml(Path("model_card.yaml"))

    assert validate_config(config) == []
    assert expected_image_uri(config) == "model-cards.azurecr.io/example/cpu/echo-model-template:0.1.0"


def test_expected_oci_labels_are_generated_from_config():
    config = load_yaml(Path("model_card.yaml"))
    labels = expected_oci_labels(config)

    assert labels["aihub.model.id"] == "echo-model-template"
    assert labels["aihub.model.name"] == "Echo Model Template"
    assert labels["aihub.hardware.minimum"] == "CPU development environment"
    assert labels["aihub.entry.api"] == "http://127.0.0.1:8080/v1"


def test_generated_label_mismatch_is_reported():
    config = load_yaml(Path("model_card.yaml"))
    labels = expected_oci_labels(config)
    labels["aihub.model.id"] = "different-model"

    errors = validate_config(config, labels)

    assert "OCI label aihub.model.id must be echo-model-template." in errors


def test_docker_build_label_args_do_not_include_shell_quotes():
    args = format_docker_build_args({"aihub.model.name": "Echo Model Template"})

    assert args == "--label=aihub.model.name=Echo Model Template"
