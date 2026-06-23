# Replace Model Runtime

`app/model_runtime.py` is the main file providers replace. Keep the gateway, schemas, license guard, and workflow shape unchanged unless AI Hub has approved a different contract.

## What To Change

Replace the echo behavior with your model loading and inference code:

```python
from app.schemas import ChatCompletionRequest


class EchoModelRuntime:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        self.model = load_your_model()

    def generate(self, request: ChatCompletionRequest) -> str:
        prompt = request.messages[-1].content
        return self.model.generate(prompt)
```

You may rename the class if you also update the import site, but the simplest path is to keep the class name and replace the internals.

## Contract To Keep

| Item | Requirement |
| --- | --- |
| Constructor | Accepts `model_id: str`. |
| `generate` input | Receives `ChatCompletionRequest` from `app.schemas`. |
| `generate` output | Returns a string response for `/v1/chat/completions`. |
| License flow | Do not read or validate `AIHUB_LICENSE_KEY` here. The shared license guard handles that before runtime is used. |
| Logging | Do not log full tokens, signatures, private key paths, raw hardware identifiers, prompts, or model outputs. |

## Loading Patterns

### Local Files

Use this when the model weights are included in the image or mounted into a known path.

```python
class EchoModelRuntime:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        self.model_path = "/app/models/my-model"
        self.model = load_model_from_path(self.model_path)
```

### Hugging Face Style Loader

Use this when your runtime downloads or loads from a model id. Pin versions and avoid downloading untrusted code at runtime.

```python
class EchoModelRuntime:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        self.model = load_model(model_id)
        self.tokenizer = load_tokenizer(model_id)
```

### Upstream API Proxy

Use this only when AI Hub has approved proxy-style packaging. The gateway contract remains the same.

```python
class EchoModelRuntime:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        self.upstream_url = "http://127.0.0.1:9000"
```

## Failure Handling

Raise a clear exception during startup if the model cannot load. The container should fail early instead of accepting traffic with a broken model.

Common cases to handle:

| Case | Expected behavior |
| --- | --- |
| Model file missing | Raise startup error with file path, not secret values. |
| Unsupported accelerator | Raise startup error naming the expected accelerator/runtime. |
| Out of memory | Raise startup error or return a controlled inference error. |
| Invalid request shape | Let gateway validation return a client error. |

## Local Check

After replacement, run:

```bash
python -m tools.preflight
```

Then start the service with a test license token and verify:

```bash
curl http://127.0.0.1:8080/healthz
curl http://127.0.0.1:8080/v1/models
python -m app.cli --base-url http://127.0.0.1:8080 --prompt "hello"
```
