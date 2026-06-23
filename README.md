# AI Hub Model Card Package Template

這是 AI Hub Model Card 上架用的 public repository template。模型提供者可以從這個 repo 建立自己的封裝專案，將單一模型與指定 accelerator/runtime 包成可審核、可配發合法 token、可由容器端驗證授權狀態的 Docker Image。

> 此 template 只提供上架封裝骨架、測試用 token 驗證流程與 CI gate。正式 `AIHUB_LICENSE_KEY` 由 AI Hub 平台的 `my-deployments` 配發；正式私鑰不得放入此 repo。

## 你會得到什麼

| 元件 | 用途 |
| --- | --- |
| `model_card.yaml` | Model Card metadata、部署目標、授權入口與 image 命名範本。 |
| `app/` | OpenAI-compatible gateway、echo runtime、CLI 與服務入口骨架。 |
| `license_guard/` | ECDSA token 驗簽、期限、硬體 hash、feature 檢查的測試實作。 |
| `Dockerfile` | 使用 Nuitka 將 `license_guard/guard.py` 編成 `.so` 的 multi-stage build。 |
| `tests/` | 授權必填、無效 token、過期 token、硬體不符、有效 token 的行為測試。 |
| `.github/workflows/` | PR / push 時執行 pytest、Docker build、OCI label 與 `.so` guard 檢查。 |

## 使用流程

1. 在 GitHub 選擇 **Use this template** 建立自己的模型封裝 repo。
2. 更新 `model_card.yaml`，填入你的模型、accelerator、runtime、features 與 image path。
3. 將 `app/model_runtime.py` 的 echo runtime 換成你的模型載入與推論邏輯。
4. 確認 `license_guard/guard.py` 的驗證欄位與 AI Hub 平台簽發 token 契約一致。
5. 執行測試：

   ```bash
   python -m pytest -q
   ```

6. 建置 image：

   ```bash
   docker build -t model-cards.azurecr.io/<vendor>/<accelerator>/<model>:<version> .
   ```

7. 用測試 token 驗證容器：

   ```bash
   docker run --rm -p 8080:8080 \
     -e AIHUB_LICENSE_KEY="<test-license-token>" \
     -e AIHUB_HARDWARE_FINGERPRINT="local-dev-device" \
     model-cards.azurecr.io/<vendor>/<accelerator>/<model>:<version>
   ```

8. 驗證服務入口：

   ```bash
   curl http://127.0.0.1:8080/healthz
   curl http://127.0.0.1:8080/v1/models
   python -m app.cli --base-url http://127.0.0.1:8080 --prompt "hello"
   ```

9. 推送 image，保存 digest，提交 AI Hub 上架審核。

## 上架前必須通過

- 無 `AIHUB_LICENSE_KEY` 時，容器不得進入可推論狀態。
- 無效 token、過期 token、硬體不符 token 必須被拒絕。
- 有效 token 通過後，`/healthz` ready，`/v1/models` 只回傳單一模型。
- CLI、API、OpenAI SDK 與 Open WebUI 必須共用同一個 license guard 狀態。
- Runtime image 必須包含 `.so` 或等效 native module，且不得保留可直接修改的 `license_guard/guard.py`。
- Log 不得輸出完整 token、signature、私鑰、公鑰來源路徑或硬體原始識別值。

## 與 AI Hub 文件的關係

- AI Hub 上架快速入門：https://github.com/R300-AI/ai-hub-webui/blob/main/docs/model_provider_packaging_quickstart.md
- Model Card 容器化規範：https://github.com/R300-AI/ai-hub-webui/blob/main/docs/model_card_containerization_standard.md
- 授權 token 流程：https://github.com/R300-AI/ai-hub-webui/blob/main/docs/model_license_token_standard.md

## 不在範圍

- 本 template 不包含正式 license signing private key。
- 本 template 不替代 AI Hub 平台的 token 簽發、吊銷與 `my-deployments` 資產管理。
- 本 template 不提供模型權重授權審查；`model_card.yaml` 中的 license 只代表封裝與顯示資料。
- 本 template 尚未宣告正式開源授權。正式對外授權需由 repo owner 決定並新增 LICENSE。
