from app.schemas import ChatCompletionRequest


class EchoModelRuntime:
    """Replace internals only; keep constructor and generate() contract stable for the gateway."""

    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    def generate(self, request: ChatCompletionRequest) -> str:
        user_messages = [message.content for message in request.messages if message.role == "user"]
        if not user_messages:
            return "Echo model is ready. Replace app/model_runtime.py with your model runtime."
        return f"Echo: {user_messages[-1]}"
