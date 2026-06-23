# Provider Workflow

This template keeps the provider workflow small: edit one config, replace one runtime, then let CI publish and report the artifact.

## Before You Start

- Confirm Python 3.11+ and Docker are installed.
- Create a repository from this template with GitHub **Use this template**.
- Keep production secrets out of chat, README, commits, issues and workflow logs.
- If AI Hub provider portal is not available yet, use `model_card.yaml` as the PoC metadata copy and replace it later with portal-generated values.

## 1. Create Repository

Use this template to create your model package repository.

## 2. Update `model_card.yaml`

Copy the non-secret Model Card draft and Publish Grant values shown by AI Hub WebUI into `model_card.yaml`. This file is the repository-local review copy of portal metadata. OCI labels are generated from this file during the workflow build, so providers should not hand-edit Dockerfile metadata labels.

## 3. Replace Model Runtime

Replace `app/model_runtime.py` with your model loading and inference logic. Keep the public gateway contract unchanged unless AI Hub has approved a different API shape. See [Replace Model Runtime](replace-model-runtime.md).

## 4. Validate Locally

```bash
python -m tools.preflight
```

`tools.preflight` checks config, generated OCI labels and pytest. Use `--check-publish-env` inside GitHub Actions or a controlled shell when you also want to confirm publish variables and secrets are present.

## 5. Configure GitHub Settings

Copy Variables and Secrets from AI Hub WebUI into GitHub Actions settings. See [GitHub Variables and Secrets](github-variables-and-secrets.md).

## 6. Publish

Run the `publish-model-card` workflow. Option A: push a tag such as `v1.0.0`. Option B: open GitHub **Actions > publish-model-card > Run workflow**. The workflow pushes the image to AI Hub ACR and reports the digest back to AI Hub WebUI.

## 7. Check AI Hub Status

Return to AI Hub WebUI and check the publish grant status.

| Status | Meaning |
| --- | --- |
| `waiting_for_callback` | GitHub Actions has not reported a completed publish yet. |
| `ci_failed` | Workflow failed before a usable image was reported. |
| `image_received` | Callback arrived; AI Hub still needs to verify registry metadata. |
| `pending_review` | Image passed automated checks and is waiting for platform review. |
| `published` | Provider publishing work is complete for this version. |
| `rejected` | Fix the shown issue, rerun preflight, then rerun publish. |

## What Providers Should Not Do

- Do not manually push to a different ACR repository path.
- Do not edit callback payloads by hand.
- Do not commit production license tokens, callback tokens, or ACR credentials.
- Do not bypass the license guard from CLI, API, SDK or Open WebUI.
- Do not hand-edit image metadata labels in Dockerfile; update AI Hub portal / `model_card.yaml` and rerun validation.
