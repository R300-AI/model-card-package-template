from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.config import load_model_card
from app.model_runtime import EchoModelRuntime
from app.schemas import ChatChoice, ChatCompletionRequest, ChatCompletionResponse, ChatMessage, ModelInfo, ModelsResponse
from license_guard.guard import LicenseState, validate_license


model_card = load_model_card()
model_id = model_card["model"]["id"]
model_owner = model_card["model"]["owner"]
license_env = model_card["license"]["env"]
runtime = EchoModelRuntime(model_id=model_id)
app = FastAPI(title="AI Hub Model Card Package Template")


def _validate(required_feature: str) -> LicenseState:
    return validate_license(license_env, [required_feature], model_id)


def _require_license(required_feature: str) -> LicenseState:
    state = _validate(required_feature)
    if not state.valid:
        raise HTTPException(status_code=403, detail={"code": state.code, "message": state.public_error})
    return state


@app.get("/healthz")
def healthz():
    state = _validate("api")
    status = "ready" if state.valid else "not_ready"
    status_code = 200 if state.valid else 503
    content = {
        "status": status,
        "license": {
            "valid": state.valid,
            "code": state.code,
            "expires_at": state.expires_at,
            "features": state.features or [],
        },
        "model_id": model_id,
    }
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=content)
    return content


@app.get("/v1/models", response_model=ModelsResponse)
def list_models():
    _require_license("api")
    return ModelsResponse(data=[ModelInfo(id=model_id, owned_by=model_owner)])


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def chat_completions(request: ChatCompletionRequest):
    _require_license("api")
    if request.model != model_id:
        raise HTTPException(status_code=404, detail={"code": "MODEL_NOT_FOUND", "message": "This container serves one model only."})

    content = runtime.generate(request)
    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid4().hex}",
        model=model_id,
        choices=[ChatChoice(index=0, message=ChatMessage(role="assistant", content=content))],
    )


@app.get("/", response_class=HTMLResponse)
def webui_placeholder():
    _require_license("webui")
    return "<html><body><h1>AI Hub Model Card Template</h1><p>Replace this page with Open WebUI integration.</p></body></html>"
