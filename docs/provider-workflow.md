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

Copy the non-secret Model Card values shown by AI Hub into `model_card.yaml`. This file is the repository-local review copy of platform metadata. OCI labels are generated from this file during the workflow build, so providers should not hand-edit Dockerfile metadata labels.

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

Run the `publish-model-card` workflow. Option A: push a tag such as `v1.0.0`. Option B: open GitHub **Actions > publish-model-card > Run workflow**. The workflow publishes the image and reports status back to AI Hub.

## 7. Check AI Hub Status

Return to AI Hub WebUI and check the publish grant status.

| Status | What to do |
| --- | --- |
| Pending review | Your workflow finished; wait for platform review. |
| Published | Provider publishing work is complete for this version. |
| Needs fix / Rejected | Fix the shown issue, rerun preflight, then rerun publish. |

## What Providers Should Not Do

- Do not manually push to a different ACR repository path.
- Do not edit workflow-generated publish reports by hand.
- Do not commit production license tokens or platform-provided publish secrets.
- Do not bypass the license guard from CLI, API, SDK or Open WebUI.
- Do not hand-edit image metadata labels in Dockerfile; update AI Hub portal / `model_card.yaml` and rerun validation.
