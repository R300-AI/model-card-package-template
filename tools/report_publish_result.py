import argparse
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict
from urllib import request

from tools.validate_config import load_yaml, parse_dockerfile_labels


class PublishReportError(RuntimeError):
    pass


def _env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise PublishReportError(f"Missing required environment variable: {name}")
    return value


def build_payload(image_digest: str, image_uri: str, config_path: str = "model_card.yaml", dockerfile_path: str = "Dockerfile") -> Dict[str, Any]:
    config = load_yaml(__import__("pathlib").Path(config_path))
    labels = parse_dockerfile_labels(__import__("pathlib").Path(dockerfile_path))

    return {
        "publish_grant_id": _env("AIHUB_PUBLISH_GRANT_ID"),
        "card_id": _env("AIHUB_CARD_ID"),
        "repository": _env("AIHUB_IMAGE_REPOSITORY"),
        "tag": _env("AIHUB_IMAGE_TAG"),
        "image_uri": image_uri,
        "image_digest": image_digest,
        "model_id": config["model"]["id"],
        "commit_sha": os.getenv("GITHUB_SHA", "local"),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "ci_status": "passed",
        "labels": labels,
        "template_version": os.getenv("AIHUB_TEMPLATE_VERSION", "model-card-package-template@main"),
        "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def post_payload(callback_url: str, callback_token: str, payload: Dict[str, Any]) -> int:
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    http_request = request.Request(
        callback_url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {callback_token}",
            "Content-Type": "application/json",
            "User-Agent": "aihub-model-card-package-template",
        },
    )
    with request.urlopen(http_request, timeout=30) as response:
        response_body = response.read().decode("utf-8")
        print(response_body)
        return response.status


def main() -> int:
    parser = argparse.ArgumentParser(description="Report AI Hub Model Card publish result to callback API.")
    parser.add_argument("--image-digest", required=True)
    parser.add_argument("--image-uri", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args.image_digest, args.image_uri)
    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    status = post_payload(_env("AIHUB_CALLBACK_URL"), _env("AIHUB_CALLBACK_TOKEN"), payload)
    if status >= 400:
        raise PublishReportError(f"Callback failed with HTTP {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
