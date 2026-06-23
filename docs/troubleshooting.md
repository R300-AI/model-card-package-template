# Troubleshooting

| Symptom | Likely Cause | Action |
| --- | --- | --- |
| `/healthz` returns `LICENSE_MISSING` | `AIHUB_LICENSE_KEY` is not set. | Copy a token from AI Hub `my-deployments` or use a test token in development. |
| `/healthz` returns `LICENSE_SIGNATURE_INVALID` | Token was truncated, modified, or signed by another key. | Copy the token again and confirm `AIHUB_LICENSE_PUBLIC_KEY` is correct in test mode. |
| `/healthz` returns `LICENSE_EXPIRED` | Token is expired. | Renew the deployment token in AI Hub. |
| `/healthz` returns `DEVICE_MISMATCH` | Hardware fingerprint differs from the bound value. | Verify deployment device or request re-binding. |
| `/v1/models` returns 403 | License is not valid for `api`. | Check token `features`. |
| SDK request fails | Client API key and AI Hub license token are mixed. | Keep SDK `api_key` as client-side placeholder; inject AI Hub token only via container env. |
| Docker image still contains `guard.py` | Runtime stage copied source files too broadly. | Copy only `guard*.so` and the non-secret support modules required by your guard. |
