# GitHub Variables and Secrets

AI Hub WebUI 會為每次模型上架建立一組發布憑證。供應商只需要把網站顯示的值填入 GitHub repository 的 **Settings > Secrets and variables > Actions**。

不要把 Secrets 貼到 README、issue、commit、workflow log 或 Copilot 對話中。

## Variables

Variables 不是秘密，用來描述這次上架要推到哪裡、回報到哪個網站端 grant。

| Name | Example | Source |
| --- | --- | --- |
| `AIHUB_ACR_LOGIN_SERVER` | `modelcards.azurecr.io` | AI Hub Publish Grant |
| `AIHUB_IMAGE_REPOSITORY` | `provider-a/rocm-igpu/gemma4-4b` | AI Hub Publish Grant |
| `AIHUB_IMAGE_TAG` | `1.0.0` | Provider release version |
| `AIHUB_CARD_ID` | `12` | AI Hub Model Card draft |
| `AIHUB_PUBLISH_GRANT_ID` | `pg_20260623_001` | AI Hub Publish Grant |
| `AIHUB_CALLBACK_URL` | `https://<aihub-host>/api/model-card-publish/callback` | AI Hub Publish Grant |

## Secrets

Secrets 可被濫用，GitHub 只會在 workflow runtime 注入。AI Hub WebUI 若顯示 secret，應只顯示一次。

| Name | Purpose |
| --- | --- |
| `AIHUB_ACR_USERNAME` | ACR scoped token name or publish principal username. |
| `AIHUB_ACR_PASSWORD` | ACR scoped token password or publish principal secret. |
| `AIHUB_CALLBACK_TOKEN` | Callback API bearer token. |
| `AIHUB_TEST_LICENSE_KEY` | Test-only license token used by CI smoke tests. |

## Publish Workflow

After the values are set, run **Actions > publish-model-card > Run workflow**, or push a `v*` tag.

The workflow will:

1. Validate `model_card.yaml` and Dockerfile labels.
2. Run tests.
3. Build the Docker image.
4. Confirm `.so` guard is present and `guard.py` is absent from the runtime image.
5. Push the image to AI Hub ACR.
6. Resolve the pushed image digest.
7. Report the result to AI Hub WebUI callback API.

## Secret Boundaries

- `AIHUB_LICENSE_KEY` is for running the model container. Do not put it in Open WebUI `OPENAI_API_KEY`.
- `AIHUB_CALLBACK_TOKEN` is only for GitHub Actions to call AI Hub WebUI. Do not use it locally unless debugging with a test environment.
- ACR credentials should be scoped to the repository path shown by AI Hub WebUI. Do not use a registry-wide admin key.
