import pytest
from fastapi import HTTPException

from app.gateway import chat_completions, healthz
from app.schemas import ChatCompletionRequest, ChatMessage


def test_healthz_is_not_ready_without_license(monkeypatch):
    monkeypatch.delenv("AIHUB_LICENSE_KEY", raising=False)

    with pytest.raises(HTTPException) as error:
        healthz()

    assert error.value.status_code == 503
    assert error.value.detail["license"]["code"] == "LICENSE_MISSING"


def test_inference_rejects_missing_license(monkeypatch):
    monkeypatch.delenv("AIHUB_LICENSE_KEY", raising=False)

    with pytest.raises(HTTPException) as error:
        chat_completions(
            ChatCompletionRequest(
                model="echo-model-template",
                messages=[ChatMessage(role="user", content="hello")],
            )
        )

    assert error.value.status_code == 403
    assert error.value.detail["code"] == "LICENSE_MISSING"
