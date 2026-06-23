import base64
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


MODEL_ID = "echo-model-template"


def _hardware_hash(fingerprint: str) -> str:
    return f"sha256:{hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()}"


@pytest.fixture()
def signing_key():
    return ec.generate_private_key(ec.SECP256R1())


@pytest.fixture()
def public_key_pem(signing_key) -> str:
    return signing_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")


def _base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


@pytest.fixture()
def make_token(signing_key):
    def _make_token(
        *,
        model_id: str = MODEL_ID,
        features: Iterable[str] = ("api", "cli", "sdk", "webui"),
        expires_delta: timedelta = timedelta(days=30),
        hardware_hash: str = _hardware_hash("local-dev-device"),
        overrides: Dict[str, object] = None,
    ) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "license_id": "lic_test_001",
            "deployment_id": "dep_test_001",
            "username": "template-test-user",
            "card_id": 1,
            "model_id": model_id,
            "image_digest": "sha256:testdigest",
            "features": list(features),
            "hardware_hash": hardware_hash,
            "hardware_binding_mode": "pre-bound",
            "issued_at": now.isoformat().replace("+00:00", "Z"),
            "not_before": now.isoformat().replace("+00:00", "Z"),
            "expires_at": (now + expires_delta).isoformat().replace("+00:00", "Z"),
            "grace_period_days": 0,
            "revocation_epoch": 1,
        }
        if overrides:
            payload.update(overrides)

        payload_segment = _base64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        signature = signing_key.sign(payload_segment.encode("ascii"), ec.ECDSA(hashes.SHA256()))
        return f"{payload_segment}.{_base64url(signature)}"

    return _make_token


@pytest.fixture()
def configured_env(monkeypatch, public_key_pem, make_token):
    monkeypatch.setenv("AIHUB_LICENSE_PUBLIC_KEY", public_key_pem)
    monkeypatch.setenv("AIHUB_HARDWARE_FINGERPRINT", "local-dev-device")
    monkeypatch.setenv("AIHUB_LICENSE_KEY", make_token())
