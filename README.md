# AI Hub Model Card Package Template

這是 AI Hub Model Card 上架用的 public repository template。模型提供者可以從這個 repo 建立自己的封裝專案，將單一模型與指定 accelerator/runtime 包成可審核、可配發合法 token、可由容器端驗證授權狀態的 Docker Image。

> 此 template 只提供上架封裝骨架、測試用 token 驗證流程與 CI gate。正式 `AIHUB_LICENSE_KEY` 由 AI Hub 平台的 `my-deployments` 配發；正式私鑰不得放入此 repo。

30 秒版：你把自己的模型接進 `app/model_runtime.py`，把 AI Hub portal 顯示的非 secret metadata 放進 `model_card.yaml`，然後讓 GitHub Actions 自動 build、test、push image、callback 回報 AI Hub。

第一次跑通 echo template 約 15-30 分鐘；替換成真實模型通常取決於模型載入方式與 accelerator 環境。

## Prerequisites

- Python 3.11+。
- Docker 與 Docker Compose。
- GitHub repo 寫入權限。
- AI Hub Model Card 草稿或 PoC 用 metadata。
- AI Hub 提供的測試 license token；正式部署 token 不放進本 repo。

## 你會得到什麼

| 元件 | 用途 |
| --- | --- |
| `model_card.yaml` | AI Hub portal 匯出的 Model Card metadata 副本、部署目標、授權入口與 image 命名範本。 |
| `app/` | OpenAI-compatible gateway、echo runtime、CLI 與服務入口骨架。 |
| `license_guard/` | ECDSA token 驗簽、期限、硬體 hash、feature 檢查的測試實作。 |
| `Dockerfile` | 使用 Nuitka 將 `license_guard/guard.py` 編成 `.so` 的 multi-stage build。 |
| `docker-compose.open-webui.yml` | 直接啟動官方 Open WebUI，並接到本 template 的 `/v1` gateway。 |
| `tests/` | 授權必填、無效 token、過期 token、硬體不符、有效 token 的行為測試。 |
| `.github/workflows/` | PR / push 時執行 pytest、Docker build、OCI label 與 `.so` guard 檢查。 |

## 使用流程

1. 在 GitHub 選擇 **Use this template** 建立自己的模型封裝 repo。
2. 依 AI Hub WebUI 顯示的 Model Card 草稿 / Publish Grant 更新 `model_card.yaml`，填入模型、accelerator、runtime、features 與 image path。
3. 將 `app/model_runtime.py` 的 echo runtime 換成你的模型載入與推論邏輯；參考 [Replace Model Runtime](docs/replace-model-runtime.md)。
4. 確認 `license_guard/guard.py` 的驗證欄位與 AI Hub 平台簽發 token 契約一致。
5. 執行本機 preflight：

   ```bash
   python -m tools.preflight
   ```

6. 建置 image。OCI labels 由 `model_card.yaml` 產生，不需要手動維護 Dockerfile metadata labels：

   ```bash
   mapfile -t AIHUB_OCI_LABEL_ARGS < <(python -m tools.generate_oci_labels --format docker-build-args)
   docker build -t model-cards.azurecr.io/<vendor>/<accelerator>/<model>:<version> "${AIHUB_OCI_LABEL_ARGS[@]}" .
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

9. 啟動 Open WebUI：

   ```bash
   docker compose -f docker-compose.open-webui.yml up --build
   ```

   開啟 `http://127.0.0.1:3000`。Open WebUI 會透過 `http://model-card:8080/v1` 呼叫同一個 license guard 後方的模型 gateway。

10. 將 AI Hub WebUI 顯示的發布憑證填入 GitHub Variables / Secrets，見 [GitHub Variables and Secrets](docs/github-variables-and-secrets.md)。
11. 執行 `publish-model-card` GitHub Actions workflow，讓 CI 自動 push image、解析 digest 並 callback 回報 AI Hub。

## Open WebUI 整合

本 template 不自行實作 WebUI，也不提供假頁面。WebUI 入口直接使用官方 Open WebUI container：

```text
browser -> Open WebUI :3000 -> model-card gateway :8080/v1 -> license guard -> model runtime
```

`AIHUB_LICENSE_KEY` 只注入 `model-card` 容器。Open WebUI 的 `OPENAI_API_KEY` 只是 OpenAI-compatible client 佔位值，不得放入 AI Hub license token。

正式發布時請將 `OPEN_WEBUI_IMAGE` pin 到通過驗收的 Open WebUI 版本，不要只依賴 `main` 或 `latest`。

## 上架前必須通過

- 無 `AIHUB_LICENSE_KEY` 時，容器不得進入可推論狀態。
- 無效 token、過期 token、硬體不符 token 必須被拒絕。
- 有效 token 通過後，`/healthz` ready，`/v1/models` 只回傳單一模型。
- CLI、API、OpenAI SDK 與 Open WebUI 必須共用同一個 license guard 狀態；Open WebUI 只能透過 `/v1` gateway 推論。
- Runtime image 必須包含 `.so` 或等效 native module，且不得保留可直接修改的 `license_guard/guard.py`。
- OCI labels 必須由 `model_card.yaml` / AI Hub portal metadata 產生，build 後需與 image config 逐項比對。
- Log 不得輸出完整 token、signature、私鑰、公鑰來源路徑或硬體原始識別值。
- 發布到 AI Hub ACR 必須透過 `publish-model-card` workflow，使用網站配發的 repository path 與 callback token。

## Provider Documents

- [Provider Workflow](docs/provider-workflow.md)
- [Replace Model Runtime](docs/replace-model-runtime.md)
- [GitHub Variables and Secrets](docs/github-variables-and-secrets.md)
- [Provider Checklist](docs/provider-checklist.md)
- [License Token Contract](docs/license-token-contract.md)
- [Troubleshooting](docs/troubleshooting.md)

## Glossary

| Term | Meaning |
| --- | --- |
| Model Card | AI Hub 上顯示模型名稱、版本、支援硬體、入口與授權資訊的卡片。 |
| Publish Grant | AI Hub 配發給 GitHub Actions 的發布憑證，只能推送指定 image path。 |
| Deployment token | 部署者執行容器時注入的 `AIHUB_LICENSE_KEY`。 |
| OCI label | 寫進 Docker image 的 metadata，由 `model_card.yaml` 產生。 |
| Image digest | image 的不可變指紋，發布後由 workflow 回報 AI Hub。 |
| License guard | 容器內檢查 `AIHUB_LICENSE_KEY` 的授權驗證程式。 |

## 與 AI Hub 文件的關係

- AI Hub 上架快速入門：https://github.com/R300-AI/ai-hub-webui/blob/main/docs/model_provider_packaging_quickstart.md
- Model Card 容器化規範：https://github.com/R300-AI/ai-hub-webui/blob/main/docs/model_card_containerization_standard.md
- 授權 token 流程：https://github.com/R300-AI/ai-hub-webui/blob/main/docs/model_license_token_standard.md

## 不在範圍

- 本 template 不包含正式 license signing private key。
- 本 template 不替代 AI Hub 平台的 token 簽發、吊銷與 `my-deployments` 資產管理。
- 本 template 不提供模型權重授權審查；`model_card.yaml` 中的 license 只代表封裝與顯示資料。
- 本 template 尚未宣告正式開源授權。正式對外授權需由 repo owner 決定並新增 LICENSE。
