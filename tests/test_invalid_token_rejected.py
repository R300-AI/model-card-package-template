from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.gateway import healthz


def test_invalid_signature_is_rejected(monkeypatch, public_key_pem):
    monkeypatch.setenv("AIHUB_LICENSE_PUBLIC_KEY", public_key_pem)
    monkeypatch.setenv("AIHUB_LICENSE_KEY", "invalid.payload")

    with pytest.raises(HTTPException) as error:
        healthz()

    assert error.value.status_code == 503
    assert error.value.detail["license"]["code"] == "LICENSE_SIGNATURE_INVALID"


def test_expired_token_is_rejected(monkeypatch, public_key_pem, make_token):
    monkeypatch.setenv("AIHUB_LICENSE_PUBLIC_KEY", public_key_pem)
    monkeypatch.setenv("AIHUB_HARDWARE_FINGERPRINT", "local-dev-device")
    monkeypatch.setenv("AIHUB_LICENSE_KEY", make_token(expires_delta=timedelta(days=-1)))

    with pytest.raises(HTTPException) as error:
        healthz()

    assert error.value.status_code == 503
    assert error.value.detail["license"]["code"] == "LICENSE_EXPIRED"


def test_device_mismatch_is_rejected(monkeypatch, public_key_pem, make_token):
    monkeypatch.setenv("AIHUB_LICENSE_PUBLIC_KEY", public_key_pem)
    monkeypatch.setenv("AIHUB_HARDWARE_FINGERPRINT", "another-device")
    monkeypatch.setenv("AIHUB_LICENSE_KEY", make_token())

    with pytest.raises(HTTPException) as error:
        healthz()

    assert error.value.status_code == 503
    assert error.value.detail["license"]["code"] == "DEVICE_MISMATCH"
