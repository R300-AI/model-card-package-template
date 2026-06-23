from app.gateway import chat_completions, healthz, list_models
from app.schemas import ChatCompletionRequest, ChatMessage


def _as_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def test_healthz_ready_with_valid_license(configured_env):
    payload = healthz()

    assert payload["status"] == "ready"
    assert payload["license"]["code"] == "OK"


def test_models_endpoint_returns_single_model(configured_env):
    payload = list_models()

    assert _as_dict(payload)["data"] == [{"id": "echo-model-template", "object": "model", "owned_by": "example-provider"}]


def test_chat_completion_uses_runtime(configured_env):
    payload = chat_completions(
        ChatCompletionRequest(
            model="echo-model-template",
            messages=[ChatMessage(role="user", content="hello")],
        )
    )

    assert _as_dict(payload)["choices"][0]["message"]["content"] == "Echo: hello"
