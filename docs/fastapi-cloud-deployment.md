# FastAPI Cloud Deployment Guide

Last researched: 2026-05-26

FastAPI Cloud is the official FastAPI-focused deployment platform from the FastAPI team. The core workflow is to build a normal FastAPI app and deploy it with:

```powershell
fastapi deploy
```

FastAPI Cloud packages the app, uploads it, installs and builds it in the cloud, deploys it with zero downtime, verifies the deployment, and gives the app an HTTPS URL such as:

```text
https://myapp.fastapicloud.dev
```

It also handles HTTPS, request-based autoscaling, replication, and scale-to-zero. Current public pricing information says FastAPI Cloud is in private beta with complimentary access, and official pricing is still under development.

Sources:

- [FastAPI Cloud homepage](https://fastapicloud.com/)
- [FastAPI Cloud pricing information](https://fastapicloud.com/legal/links/pricing/)
- [How FastAPI Cloud deployments work](https://fastapicloud.com/docs/builds-and-deployments/how-it-works/)
- [Official FastAPI deployment page](https://fastapi.tiangolo.com/deployment/fastapicloud/)

## Current Availability

FastAPI Cloud is still beta and waitlist-oriented. The docs assume you already have an account, while the homepage still asks users to join the waitlist.

Some features are rolling out gradually and may not be enabled for every account:

- GitHub repository integration
- Custom domains
- Some monitoring and platform features

Sources:

- [GitHub integration](https://fastapicloud.com/docs/source-control/github-integration/)
- [Custom domains](https://fastapicloud.com/docs/advanced-features/custom-domains/)

## Deploy a New App

Use `uv` and `fastapi-new` for the quickest path:

```powershell
uvx fastapi-new myapp
cd myapp
```

Run locally first:

```powershell
uv run fastapi dev
```

Deploy:

```powershell
uv run fastapi deploy
```

On the first deploy, the CLI prompts you to log in, select or create a team, and create or link an app. After the first deploy, a local `.fastapicloud` directory is created to link the project to the cloud app.

Future deploys from the same directory are:

```powershell
uv run fastapi deploy
```

After deployment, visit:

```text
https://myapp.fastapicloud.dev
https://myapp.fastapicloud.dev/docs
```

Sources:

- [Quick Start](https://fastapicloud.com/docs/getting-started/)
- [Deploy command](https://fastapicloud.com/docs/fastapi-cloud-cli/deploy/)

## Deploy an Existing App

FastAPI Cloud works with standard Python project layouts.

Recommended layout:

```text
myproject/
  pyproject.toml
  main.py
```

Package layout:

```text
myproject/
  pyproject.toml
  app/
    main.py
```

The app file should expose a FastAPI app instance, typically:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def main():
    return {"message": "Hello World"}
```

Add the deploy-capable FastAPI package:

```powershell
uv add "fastapi[standard]"
```

Or in `requirements.txt`:

```text
fastapi[standard]
```

The `fastapi[standard]` package includes the FastAPI CLI commands used for local development and deployment, including:

- `fastapi dev`
- `fastapi login`
- `fastapi deploy`

Source: [Migrate an existing project](https://fastapicloud.com/docs/getting-started/existing-project/)

## Python Version

FastAPI Cloud supports currently supported Python versions, 3.10 and newer. By default, it uses the latest stable Python version available.

Pin Python when dependencies are sensitive to Python versions:

```toml
[project]
requires-python = "==3.13.*"
```

This is useful when a dependency does not yet provide prebuilt wheels for a newer Python release.

Sources:

- [Install dependencies](https://fastapicloud.com/docs/builds-and-deployments/install-dependencies/)
- [Common issues](https://fastapicloud.com/docs/troubleshooting-and-faqs/common-issues/)

## Entrypoint Configuration

If your app is not auto-detected, or if you normally run local development with a file path such as:

```powershell
fastapi dev app/main.py
```

configure the entrypoint in `pyproject.toml`:

```toml
[tool.fastapi]
entrypoint = "app.main:app"
```

Then verify:

```powershell
uv run fastapi dev
```

If `fastapi dev` works without passing a file path, `fastapi deploy` should work too.

Source: [Configuring FastAPI](https://fastapicloud.com/docs/builds-and-deployments/configuring-fastapi/)

## Uploaded Files

FastAPI Cloud respects `.gitignore` when packaging files for deployment. Use `.fastapicloudignore` for deployment-specific rules.

Exclude files tracked in git but not needed in production:

```text
tests/
docs/
scripts/
```

Include files ignored by git but needed for deployment:

```text
!dist/
```

Source: [Ignore or un-ignore files](https://fastapicloud.com/docs/builds-and-deployments/fastapicloudignore/)

## Environment Variables

Set environment variables with the CLI:

```powershell
uv run fastapi cloud env set ENVIRONMENT "production"
```

Set secrets:

```powershell
uv run fastapi cloud env set --secret API_KEY "your-api-key"
```

List variables:

```powershell
uv run fastapi cloud env list
```

Delete a variable:

```powershell
uv run fastapi cloud env delete API_KEY
```

Important notes:

- Secrets are encrypted.
- Secrets cannot be viewed in the dashboard after creation.
- CLI environment variable changes require a new deploy to take effect.
- Dashboard changes can use "Save and Redeploy" to apply immediately.
- The dashboard supports bulk import from `.env` files.

Sources:

- [Environment variables](https://fastapicloud.com/docs/builds-and-deployments/environment-variables/)
- [Env command](https://fastapicloud.com/docs/fastapi-cloud-cli/env/)

## Deployment Flow

When `fastapi deploy` runs, FastAPI Cloud:

1. Packages and uploads the app code.
2. Creates a deployment record.
3. Installs dependencies and builds the app in the cloud.
4. Rolls out the deployment gradually.
5. Verifies the new deployment.
6. Keeps the last successful deployment if the new one fails verification.

FastAPI Cloud says deployments are zero downtime. During rollout, old and new app instances can briefly run at the same time.

Source: [How it works](https://fastapicloud.com/docs/builds-and-deployments/how-it-works/)

## Database Integrations

FastAPI Cloud has integrations for external services and databases. The general flow is:

1. Go to team settings.
2. Open Integrations.
3. Connect the provider account.
4. Open the app details.
5. Go to the Storage tab.
6. Attach the provider resource.
7. Let FastAPI Cloud create a secure environment variable, usually `DATABASE_URL`.
8. Optionally redeploy immediately.

Supported documented database integrations include:

- Neon
- Supabase
- Redis Cloud, marked as coming soon in the docs navigation

Sources:

- [Third-party integrations](https://fastapicloud.com/docs/integrations/third-party-integrations/)
- [Neon integration](https://fastapicloud.com/docs/integrations/neon-integration/)
- [Supabase integration](https://fastapicloud.com/docs/integrations/supabase-integration/)

## Database Migrations

Because FastAPI Cloud performs gradual zero-downtime rollouts, old and new versions of the app can run at the same time.

Use migration stages that keep both old and new app versions compatible with the database:

- Additive changes: run the migration before deploying code that uses the new schema.
- Removal changes: deploy code that no longer uses the old schema first, then run the migration that removes it.
- Mixed add and remove changes: split them into multiple staged migrations and deployments.

Source: [Deployments and database migrations](https://fastapicloud.com/docs/builds-and-deployments/database-migrations/)

## Logs and Monitoring

Stream logs:

```powershell
uv run fastapi cloud logs
```

Show recent logs without streaming:

```powershell
uv run fastapi cloud logs --no-follow
```

Limit log lines:

```powershell
uv run fastapi cloud logs --tail 50
```

Filter by time:

```powershell
uv run fastapi cloud logs --since 1h
```

The dashboard also shows app-level runtime logs and build logs.

Sources:

- [Logs command](https://fastapicloud.com/docs/fastapi-cloud-cli/logs/)
- [Monitoring logs](https://fastapicloud.com/docs/monitoring-and-performance/logs/)

## CI/CD with GitHub Actions

FastAPI Cloud provides a setup command:

```powershell
uv run fastapi cloud setup-ci
```

This can:

1. Read the GitHub repo slug from the `origin` remote.
2. Detect the default branch.
3. Create or regenerate a deploy token.
4. Set `FASTAPI_CLOUD_TOKEN` and `FASTAPI_CLOUD_APP_ID` as GitHub secrets if the GitHub CLI is installed and authenticated.
5. Write `.github/workflows/deploy.yml`.

Useful variants:

```powershell
uv run fastapi cloud setup-ci --branch production
uv run fastapi cloud setup-ci --dry-run
uv run fastapi cloud setup-ci --secrets-only
uv run fastapi cloud setup-ci --file deploy-prod.yml
```

Minimal GitHub Actions workflow:

```yaml
name: Deploy

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v7
      - run: uv run fastapi deploy
        env:
          FASTAPI_CLOUD_TOKEN: ${{ secrets.FASTAPI_CLOUD_TOKEN }}
          FASTAPI_CLOUD_APP_ID: ${{ secrets.FASTAPI_CLOUD_APP_ID }}
```

Sources:

- [Setup CI command](https://fastapicloud.com/docs/fastapi-cloud-cli/setup-ci/)
- [Deploy tokens](https://fastapicloud.com/docs/advanced-features/deploy-tokens/)

## Deploy Tokens

Deploy tokens allow CI/CD systems to deploy without using a personal account login.

Create a deploy token in the dashboard:

1. Open the app.
2. Select Deploy Tokens.
3. Click Create Token.
4. Enter a token name.
5. Set expiration, from 1 to 365 days.
6. Copy the token immediately. It is shown only once.

Use a token locally or in CI:

```powershell
$env:FASTAPI_CLOUD_TOKEN = "your-token"
$env:FASTAPI_CLOUD_APP_ID = "a1b2c3d4-e5f6-7890-abcd-1234567890ab"
uv run fastapi deploy
```

Or pass the app ID:

```powershell
$env:FASTAPI_CLOUD_TOKEN = "your-token"
uv run fastapi deploy --app-id "a1b2c3d4-e5f6-7890-abcd-1234567890ab"
```

Source: [Deploy tokens](https://fastapicloud.com/docs/advanced-features/deploy-tokens/)

## GitHub Integration

FastAPI Cloud also documents a GitHub app integration that can deploy on pushes to the default branch. The docs mark it as rolling out and not available to all accounts yet.

Create a new app from GitHub:

1. Open the FastAPI Cloud dashboard.
2. Go to your team.
3. Create a new app from GitHub.
4. Connect GitHub if prompted.
5. Install or update the FastAPI Cloud GitHub App.
6. Select the GitHub account or organization.
7. Select the repository.
8. Set Root Directory if the app is not at the repository root.
9. Click Create App.

Source: [GitHub integration](https://fastapicloud.com/docs/source-control/github-integration/)

## Custom Domains

Custom domains are rolling out gradually. If enabled for your account:

1. Deploy the app successfully at least once.
2. Open the app in the dashboard.
3. Select Domains.
4. Click Add Custom Domain.
5. Enter a domain such as `api.example.com` or `example.com`.
6. Add the DNS records shown by the dashboard.
7. Wait for verification and TLS certificate issuance.

Subdomains usually use CNAME records. Apex/root domains use A records. TLS certificates are issued and renewed automatically.

If DNS is managed by Cloudflare, set the relevant records to DNS only, not proxied, so FastAPI Cloud can validate and issue certificates.

Source: [Custom domains](https://fastapicloud.com/docs/advanced-features/custom-domains/)

## Monorepos and App Directory

By default, FastAPI Cloud expects the app at the repository root. If the FastAPI app is inside a subdirectory, configure the application directory in the dashboard:

1. Open the app.
2. Go to Settings.
3. Find Application Directory.
4. Enter a relative path such as `backend` or `packages/api`.
5. Click Update.

Rules:

- Use relative paths only.
- Do not use `..`.
- Allowed characters include letters, numbers, spaces, `/`, `.`, `_`, and `-`.

FastAPI Cloud supports `uv` workspaces. If `uv.lock` is at the repository root and the app is in a subdirectory, it can resolve dependencies from the root lock file and install workspace members used by the app.

Source: [Application directory](https://fastapicloud.com/docs/builds-and-deployments/application-directory/)

## Custom URL Generation

FastAPI Cloud converts app names into DNS-safe subdomains:

- Lowercase the name.
- Remove special characters.
- Convert spaces and underscores to hyphens.
- Ensure the label starts with a letter.
- Trim to 63 characters.
- Collapse repeated hyphens.
- Add a hash suffix if needed for uniqueness.

Source: [How app URLs are generated](https://fastapicloud.com/docs/other-resources/how-app-urls-are-generated/)

## Troubleshooting

### Build Failed While Installing Dependencies

This often means a dependency cannot build from source or does not have a prebuilt wheel for the selected Python version.

Fix:

1. Pin Python to a version known to work with dependencies.
2. Re-run local dependency installation.
3. Deploy again.

Source: [Common issues](https://fastapicloud.com/docs/troubleshooting-and-faqs/common-issues/)

### App Not Found

This can happen when:

- You are logged into a different account than the one that created the app.
- The app was deleted from the dashboard.

If the app was deleted and the local project still points to it, unlink:

```powershell
uv run fastapi cloud unlink
```

Then deploy again to create or link a new app.

Sources:

- [Deploy command troubleshooting](https://fastapicloud.com/docs/fastapi-cloud-cli/deploy/)
- [Unlink command](https://fastapicloud.com/docs/fastapi-cloud-cli/unlink/)

## Practical Checklist

Before deployment:

- Confirm you have FastAPI Cloud account access.
- Confirm `fastapi[standard]` is installed.
- Confirm `pyproject.toml` or `requirements.txt` is present.
- Pin Python if dependency compatibility matters.
- Configure `[tool.fastapi] entrypoint` if needed.
- Run `uv run fastapi dev` successfully.
- Review `.gitignore` and `.fastapicloudignore`.
- Configure required environment variables and secrets.
- Plan database migrations for zero-downtime rollout.

Deploy:

```powershell
uv run fastapi deploy
```

After deployment:

- Visit the app URL.
- Visit `/docs`.
- Check runtime logs.
- Configure database integrations if needed.
- Configure CI/CD with `fastapi cloud setup-ci`.
- Add a custom domain if the feature is enabled.
