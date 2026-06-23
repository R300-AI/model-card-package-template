from pathlib import Path

from tools.validate_config import expected_image_uri, load_yaml, parse_dockerfile_labels, validate_config


def test_current_template_config_is_valid():
    config = load_yaml(Path("model_card.yaml"))
    labels = parse_dockerfile_labels(Path("Dockerfile"))

    assert validate_config(config, labels) == []
    assert expected_image_uri(config) == "model-cards.azurecr.io/example/cpu/echo-model-template:0.1.0"


def test_model_id_label_must_match_config():
    config = load_yaml(Path("model_card.yaml"))
    labels = parse_dockerfile_labels(Path("Dockerfile"))
    labels["aihub.model.id"] = "different-model"

    errors = validate_config(config, labels)

    assert "Dockerfile label aihub.model.id must match model_card.yaml model.id." in errors
