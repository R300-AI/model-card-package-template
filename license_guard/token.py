import base64
import json
from dataclasses import dataclass
from typing import Any, Dict

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


class TokenFormatError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedToken:
    payload: Dict[str, Any]
    signed_part: bytes
    signature: bytes


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def parse_token(raw_token: str) -> ParsedToken:
    parts = raw_token.split(".")
    if len(parts) != 2:
        raise TokenFormatError("Token must use base64url(payload).base64url(signature) format.")

    payload_segment, signature_segment = parts
    try:
        payload_bytes = _base64url_decode(payload_segment)
        signature = _base64url_decode(signature_segment)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as error:
        raise TokenFormatError("Token payload or signature is malformed.") from error

    return ParsedToken(payload=payload, signed_part=payload_segment.encode("ascii"), signature=signature)


def verify_signature(parsed_token: ParsedToken, public_key_pem: str) -> None:
    public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    if not isinstance(public_key, ec.EllipticCurvePublicKey):
        raise TokenFormatError("Public key must be an ECDSA public key.")

    try:
        public_key.verify(parsed_token.signature, parsed_token.signed_part, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as error:
        raise TokenFormatError("Token signature is invalid.") from error
