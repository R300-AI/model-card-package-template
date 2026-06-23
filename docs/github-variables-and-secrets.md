# GitHub Variables and Secrets

AI Hub WebUI 會為每次模型上架建立一組發布憑證。供應商只需要把網站顯示的值填入 GitHub repository 的 **Settings > Secrets and variables > Actions**。

不要把 Secrets 貼到 README、issue、commit、workflow log 或 Copilot 對話中。

## Where To Find These Values

In the final AI Hub provider portal, these values should appear under the Model Card draft's Publish Grant panel. Until that UI is implemented, use the PoC values agreed with the AI Hub maintainer and keep the same names shown below.

Copy by destination:

1. Put Variables in GitHub **Repository Settings > Secrets and variables > Actions > Variables**.
2. Put Secrets in GitHub **Repository Settings > Secrets and variables > Actions > Secrets**.
3. Do not paste secret values into Copilot chat or issue comments for review.

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

1. Validate `model_card.yaml` and required publish settings.
2. Run tests.
3. Generate OCI labels from `model_card.yaml`.
4. Build the Docker image with generated labels.
5. Confirm `.so` guard is present and `guard.py` is absent from the runtime image.
6. Push the image to AI Hub ACR.
7. Resolve the pushed image digest.
8. Report the result to AI Hub WebUI callback API.

## Secret Boundaries

- `AIHUB_LICENSE_KEY` is for running the model container. Do not put it in Open WebUI `OPENAI_API_KEY`.
- `AIHUB_CALLBACK_TOKEN` is only for GitHub Actions to call AI Hub WebUI. Do not use it locally unless debugging with a test environment.
- ACR credentials should be scoped to the repository path shown by AI Hub WebUI. Do not use a registry-wide admin key.

Safe placement examples:

| Value | Correct place | Do not place in |
| --- | --- | --- |
| `AIHUB_ACR_PASSWORD` | GitHub Secret `AIHUB_ACR_PASSWORD` | README, Variables, workflow YAML |
| `AIHUB_CALLBACK_TOKEN` | GitHub Secret `AIHUB_CALLBACK_TOKEN` | Copilot chat, issue comments |
| Test `AIHUB_LICENSE_KEY` | GitHub Secret `AIHUB_TEST_LICENSE_KEY` or local shell for smoke tests | Open WebUI `OPENAI_API_KEY` |
