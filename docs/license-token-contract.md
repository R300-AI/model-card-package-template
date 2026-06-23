# License Token Contract

AI Hub 合法 token 使用 `base64url(payload).base64url(signature)` 測試格式。正式格式可由 AI Hub 平台調整，但語意必須保留：簽章、期限、硬體綁定、功能權限與部署資產識別。

## Payload

```json
{
  "license_id": "lic_test_001",
  "deployment_id": "dep_test_001",
  "username": "template-test-user",
  "card_id": 1,
  "model_id": "echo-model-template",
  "image_digest": "sha256:testdigest",
  "features": ["api", "cli", "sdk", "webui"],
  "hardware_hash": "sha256:<hardware-binding>",
  "hardware_binding_mode": "pre-bound",
  "issued_at": "2026-06-23T00:00:00Z",
  "not_before": "2026-06-23T00:00:00Z",
  "expires_at": "2026-09-23T00:00:00Z",
  "grace_period_days": 0,
  "revocation_epoch": 1
}
```

## Validation Order

1. Verify signature.
2. Check revocation status when revocation data is available.
3. Check `not_before` and `expires_at`.
4. Compare hardware binding hash.
5. Check requested feature.
6. Release gateway and model runtime only after validation passes.

## Error Codes

| Code | Meaning |
| --- | --- |
| `LICENSE_MISSING` | `AIHUB_LICENSE_KEY` is not provided. |
| `LICENSE_SIGNATURE_INVALID` | Payload or signature is invalid. |
| `LICENSE_REVOKED` | License is revoked. |
| `LICENSE_NOT_YET_VALID` | License is not valid yet. |
| `LICENSE_EXPIRED` | License is expired. |
| `DEVICE_MISMATCH` | Hardware binding does not match. |
| `FEATURE_NOT_ALLOWED` | Requested interface is not allowed. |
| `CLOCK_TAMPERED` | System time is suspicious. |

Errors must not include full token, signature, private key, public key file path, or raw hardware identifiers.
