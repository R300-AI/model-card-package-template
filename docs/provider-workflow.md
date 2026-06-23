# Provider Workflow

This template keeps the provider workflow small: edit one config, replace one runtime, then let CI publish and report the artifact.

## 1. Create Repository

Use this template to create your model package repository.

## 2. Update `model_card.yaml`

Copy the non-secret Model Card draft and Publish Grant values shown by AI Hub WebUI into `model_card.yaml`. This file is the repository-local review copy of portal metadata. OCI labels are generated from this file during the workflow build, so providers should not hand-edit Dockerfile metadata labels.

## 3. Replace Model Runtime

Replace `app/model_runtime.py` with your model loading and inference logic. Keep the public gateway contract unchanged unless AI Hub has approved a different API shape.

## 4. Validate Locally

```bash
python -m tools.validate_config
python -m pytest -q
```

## 5. Configure GitHub Settings

Copy Variables and Secrets from AI Hub WebUI into GitHub Actions settings. See [GitHub Variables and Secrets](github-variables-and-secrets.md).

## 6. Publish

Run the `publish-model-card` workflow. The workflow pushes the image to AI Hub ACR and reports the digest back to AI Hub WebUI.

## 7. Check AI Hub Status

Return to AI Hub WebUI and check the publish grant status. The site should show whether the image was received, verified, rejected, or is pending review.

## What Providers Should Not Do

- Do not manually push to a different ACR repository path.
- Do not edit callback payloads by hand.
- Do not commit production license tokens, callback tokens, or ACR credentials.
- Do not bypass the license guard from CLI, API, SDK or Open WebUI.
- Do not hand-edit image metadata labels in Dockerfile; update AI Hub portal / `model_card.yaml` and rerun validation.
