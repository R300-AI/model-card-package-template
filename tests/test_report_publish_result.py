from tools.report_publish_result import build_payload


def test_build_payload_uses_github_and_aihub_environment(monkeypatch):
    monkeypatch.setenv("AIHUB_PUBLISH_GRANT_ID", "pg_test_001")
    monkeypatch.setenv("AIHUB_CARD_ID", "12")
    monkeypatch.setenv("AIHUB_IMAGE_REPOSITORY", "example/cpu/echo-model-template")
    monkeypatch.setenv("AIHUB_IMAGE_TAG", "0.1.0")
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    monkeypatch.setenv("GITHUB_RUN_ID", "456")

    payload = build_payload(
        "sha256:testdigest",
        "model-cards.azurecr.io/example/cpu/echo-model-template@sha256:testdigest",
    )

    assert payload["publish_grant_id"] == "pg_test_001"
    assert payload["card_id"] == "12"
    assert payload["model_id"] == "echo-model-template"
    assert payload["image_digest"] == "sha256:testdigest"
    assert payload["commit_sha"] == "abc123"
    assert payload["workflow_run_id"] == "456"
    assert payload["labels"]["aihub.security.guard"] == "native-module"
