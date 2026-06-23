from dataclasses import dataclass
from datetime import datetime, timezone
import os
from typing import List, Optional

from license_guard.hardware import get_hardware_hash
from license_guard.public_key import DEFAULT_TEST_PUBLIC_KEY_PEM
from license_guard.token import TokenFormatError, parse_token, verify_signature


@dataclass(frozen=True)
class LicenseState:
    valid: bool
    code: str
    public_error: str
    expires_at: Optional[str] = None
    features: Optional[List[str]] = None


def _parse_time(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def _public_key_pem() -> str:
    return os.getenv("AIHUB_LICENSE_PUBLIC_KEY", DEFAULT_TEST_PUBLIC_KEY_PEM)


def validate_license(env_name: str, required_features: List[str], expected_model_id: str) -> LicenseState:
    raw_token = os.getenv(env_name)
    if not raw_token:
        return LicenseState(False, "LICENSE_MISSING", f"Missing {env_name}. Get a license token from my-deployments.")

    try:
        parsed_token = parse_token(raw_token)
        verify_signature(parsed_token, _public_key_pem())
    except TokenFormatError:
        return LicenseState(False, "LICENSE_SIGNATURE_INVALID", "License token is invalid. Copy it again from my-deployments.")

    payload = parsed_token.payload
    now = datetime.now(timezone.utc)

    not_before = payload.get("not_before")
    if not_before and now < _parse_time(not_before):
        return LicenseState(False, "LICENSE_NOT_YET_VALID", "License token is not valid yet. Check the token or system time.")

    expires_at = payload.get("expires_at")
    if not expires_at:
        return LicenseState(False, "LICENSE_SIGNATURE_INVALID", "License token is missing expires_at.")
    if now > _parse_time(expires_at):
        return LicenseState(False, "LICENSE_EXPIRED", "License token is expired. Renew it from my-deployments.")

    if payload.get("model_id") != expected_model_id:
        return LicenseState(False, "FEATURE_NOT_ALLOWED", "License token does not allow this model.")

    expected_hardware_hash = payload.get("hardware_hash")
    if expected_hardware_hash and expected_hardware_hash != get_hardware_hash():
        return LicenseState(False, "DEVICE_MISMATCH", "License token is bound to a different device.")

    features = payload.get("features") or []
    missing_features = [feature for feature in required_features if feature not in features]
    if missing_features:
        return LicenseState(False, "FEATURE_NOT_ALLOWED", "License token does not allow the requested interface.")

    return LicenseState(True, "OK", "License is valid.", expires_at=expires_at, features=features)
