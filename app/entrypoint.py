import uvicorn

from app.config import load_model_card


if __name__ == "__main__":
    model_card = load_model_card()
    port = int(model_card["deployment"].get("gateway_port", 8080))
    uvicorn.run("app.gateway:app", host="0.0.0.0", port=port)
