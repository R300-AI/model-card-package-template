import argparse

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Call the AI Hub model card gateway.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--model", default="echo-model-template")
    args = parser.parse_args()

    response = httpx.post(
        f"{args.base_url.rstrip('/')}/v1/chat/completions",
        json={
            "model": args.model,
            "messages": [{"role": "user", "content": args.prompt}],
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    print(payload["choices"][0]["message"]["content"])


if __name__ == "__main__":
    main()
