from pathlib import Path

from tools.preflight import collect_config_errors, collect_label_errors, main


def test_preflight_collects_no_errors_for_template_config():
    model_card_path = Path("model_card.yaml")

    assert collect_config_errors(model_card_path) == []
    assert collect_label_errors(model_card_path) == []


def test_preflight_reports_missing_model_card(tmp_path):
    missing_path = tmp_path / "missing.yaml"

    import sys

    original_argv = sys.argv
    try:
        sys.argv = ["preflight", "--model-card", str(missing_path), "--skip-tests"]
        assert main() == 1
    finally:
        sys.argv = original_argv
