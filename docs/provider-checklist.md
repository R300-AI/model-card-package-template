# Model Provider Checklist

模型提供者提交 AI Hub 上架審核前，請確認下列項目。

## Metadata

- [ ] `model_card.yaml` 的 `model.id` 與 `/v1/models` 回傳值一致。
- [ ] `model.name`、`model.version`、`model.owner` 已填寫。
- [ ] `deployment.accelerator` 對應 AI Hub 核准的 accelerator path。
- [ ] `license.env` 固定使用 `AIHUB_LICENSE_KEY`，除非 AI Hub 平台另行公告。

## Container

- [ ] Image 使用固定版本 tag，不只依賴 `latest`。
- [ ] Image labels 包含 `aihub.package.kind`、`aihub.model.id`、`aihub.license.required` 與 `aihub.security.guard.*`。
- [ ] Runtime image 內存在 `license_guard/guard*.so` 或等效 native module。
- [ ] Runtime image 內不存在可直接修改的 `license_guard/guard.py`。

## License Token

- [ ] 缺少 `AIHUB_LICENSE_KEY` 時，`/healthz` 非 ready。
- [ ] 無效 token 回 `LICENSE_SIGNATURE_INVALID`。
- [ ] 到期 token 回 `LICENSE_EXPIRED`。
- [ ] 硬體不符 token 回 `DEVICE_MISMATCH`。
- [ ] 功能未授權 token 回 `FEATURE_NOT_ALLOWED`。
- [ ] 有效 token 通過後，所有支援入口共用同一個 license state。

## Service Interface

- [ ] `/healthz` 不輸出 secret，但能顯示非敏感授權狀態。
- [ ] `/v1/models` 只回傳此容器唯一模型。
- [ ] `/v1/chat/completions` 或對應推論 endpoint 可用。
- [ ] CLI 使用 gateway，不繞過 license guard。
- [ ] SDK 與 WebUI 不把 `AIHUB_LICENSE_KEY` 當作 client API key。

## Evidence

- [ ] 附上 pytest 結果。
- [ ] 附上 Docker build 結果。
- [ ] 附上 image URI 與 digest。
- [ ] 附上無 token、無效 token、有效 token 的 smoke test log，且 log 不含 secret。
