# CI/CD Setup Guide

Complete guide to setting up automated deployments with GitHub Actions.

## Overview

The CI/CD pipeline automatically:
- Runs tests on every push and pull request
- Performs security scans
- Builds Docker images
- Deploys to Azure Container Apps
- Runs health checks
- Sends notifications

## Prerequisites

- GitHub repository with admin access
- Azure subscription with deployed infrastructure (run `./provision.sh` first)
- Azure CLI installed locally

## Step 1: Create Azure Service Principal

Create a service principal for GitHub Actions to authenticate with Azure:

```bash
# Get your subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create service principal
az ad sp create-for-rbac \
  --name "rmc-triage-github-actions" \
  --role Contributor \
  --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/rmc-triage-rg" \
  --sdk-auth

# Save the entire JSON output - you'll need it for GitHub secrets
```

The output will look like:
```json
{
  "clientId": "00000000-0000-0000-0000-000000000000",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "00000000-0000-0000-0000-000000000000",
  "tenantId": "00000000-0000-0000-0000-000000000000",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

**Important:** Save this entire JSON output securely!

## Step 2: Get ACR Credentials

Get credentials for Azure Container Registry:

```bash
# Get ACR username
az acr credential show --name rmctriageacr --query username -o tsv

# Get ACR password
az acr credential show --name rmctriageacr --query "passwords[0].value" -o tsv
```

## Step 3: Get API URL

Get the API URL for the frontend build:

```bash
# Get API URL
az containerapp show \
  --name rmc-api \
  --resource-group rmc-triage-rg \
  --query "properties.configuration.ingress.fqdn" -o tsv
```

## Step 4: Configure GitHub Secrets

Go to your GitHub repository settings and add the following secrets:

**Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `AZURE_CREDENTIALS` | Service principal JSON | Output from Step 1 (entire JSON) |
| `ACR_USERNAME` | Container registry username | Output from Step 2 (first command) |
| `ACR_PASSWORD` | Container registry password | Output from Step 2 (second command) |
| `API_URL` | API URL for frontend | Output from Step 3 with `https://` prefix |

### Optional Secrets (for notifications)

| Secret Name | Description |
|-------------|-------------|
| `SLACK_WEBHOOK_URL` | Slack webhook for deployment notifications |
| `DISCORD_WEBHOOK_URL` | Discord webhook for deployment notifications |

### Example: Adding Secrets via GitHub UI

1. Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
2. Click **"New repository secret"**
3. Enter name: `AZURE_CREDENTIALS`
4. Paste the entire JSON output from Step 1
5. Click **"Add secret"**
6. Repeat for other secrets

### Example: Adding Secrets via GitHub CLI

```bash
# Install GitHub CLI if needed
brew install gh  # macOS
# or: sudo apt install gh  # Ubuntu/Debian

# Login to GitHub
gh auth login

# Add secrets
gh secret set AZURE_CREDENTIALS < azure-credentials.json
gh secret set ACR_USERNAME --body "rmctriageacr"
gh secret set ACR_PASSWORD --body "your-acr-password"
gh secret set API_URL --body "https://rmc-api.azurecontainerapps.io"

# Optional: Add Slack webhook
gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

## Step 5: Verify Workflow File

The workflow file should already exist at `.github/workflows/azure-deploy.yml`. Verify it's present:

```bash
ls -la .github/workflows/azure-deploy.yml
```

If not, copy it from the infra directory:

```bash
mkdir -p .github/workflows
cp infra/azure-deploy.yml .github/workflows/
```

## Step 6: Test the Workflow

### Automatic Trigger (Push to Main)

Push to main branch to trigger automatic deployment:

```bash
git add .
git commit -m "Set up CI/CD pipeline"
git push origin main
```

### Manual Trigger

Trigger deployment manually from GitHub:

1. Go to **Actions** tab in your repository
2. Select **"Deploy to Azure Container Apps"** workflow
3. Click **"Run workflow"**
4. Select environment (staging/production)
5. Click **"Run workflow"**

## Step 7: Monitor Deployment

### Via GitHub Actions UI

1. Go to **Actions** tab
2. Click on the running workflow
3. View real-time logs for each job

### Via CLI

```bash
# View latest workflow run
gh run list --limit 1

# View logs for specific run
gh run view <run-id> --log

# Watch workflow in real-time
gh run watch
```

## Workflow Details

### Jobs

1. **test** - Runs unit and integration tests
   - Sets up PostgreSQL and Redis services
   - Installs dependencies
   - Runs pytest with coverage
   - Uploads coverage to Codecov

2. **security** - Scans for vulnerabilities
   - Runs Trivy scanner
   - Uploads results to GitHub Security

3. **deploy** - Builds and deploys application
   - Builds Docker images with build cache
   - Pushes to Azure Container Registry
   - Runs database migrations
   - Deploys all container apps
   - Runs health checks
   - Creates deployment summary

4. **notify** - Sends notifications
   - Sends Slack/Discord notifications
   - Reports deployment status

### Deployment Flow

```
┌──────────────┐
│  Push/PR     │
└──────┬───────┘
       │
       ├─────────┬─────────┐
       ▼         ▼         ▼
   ┌──────┐ ┌──────┐ ┌──────┐
   │ Test │ │Security│ │Lint │
   └──┬───┘ └───┬──┘ └───┬──┘
       │         │        │
       └────┬────┴────┬───┘
            ▼         ▼
         ┌─────────────────┐
         │   Build Images  │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │ Run Migrations  │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │ Deploy to Azure │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  Health Checks  │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │    Notify       │
         └─────────────────┘
```

## Environments

The workflow uses GitHub Environments for deployment protection:

### Set Up Environments

1. Go to **Settings → Environments**
2. Create `staging` environment
3. Create `production` environment
4. Add protection rules for `production`:
   - Required reviewers (optional)
   - Wait timer (optional)
   - Deployment branches: Only main branch

### Environment-Specific Configuration

The workflow automatically determines environment based on branch:
- `main` branch → `production` environment
- Other branches → `staging` environment

## Branch Strategy

### Recommended Git Flow

```
main (production)
  ↑
  │ PR + Review
  │
develop (staging)
  ↑
  │ PR
  │
feature/xxx (local)
```

### Branch Configuration

```bash
# Create staging branch
git checkout -b staging
git push -u origin staging

# Protect main branch
gh repo edit --enable-branch-protection main

# Add required status checks
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][]=test \
  --field required_status_checks[contexts][]=security
```

## Customization

### Modify Deployment Triggers

Edit `.github/workflows/azure-deploy.yml`:

```yaml
# Deploy only on specific paths
on:
  push:
    branches: [main]
    paths:
      - 'api/**'
      - 'frontend/**'
      - '.github/workflows/**'

# Deploy on schedule
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

### Add More Tests

Add additional test jobs:

```yaml
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Run integration tests
        run: |
          cd tests
          pytest integration/

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Run E2E tests
        run: |
          npx playwright test
```

### Add Deployment Slots

Deploy to staging slot first, then swap:

```yaml
  - name: Deploy to staging slot
    run: |
      az containerapp revision copy \
        --name rmc-api \
        --resource-group rmc-triage-rg \
        --target-revision staging

  - name: Run smoke tests
    run: |
      curl https://rmc-api---staging.azurecontainerapps.io/health

  - name: Swap to production
    run: |
      az containerapp ingress traffic set \
        --name rmc-api \
        --resource-group rmc-triage-rg \
        --revision-weight latest=100
```

## Monitoring

### View Deployment History

```bash
# List recent workflow runs
gh run list --workflow=azure-deploy.yml --limit 10

# View specific run
gh run view <run-id>

# Download logs
gh run download <run-id>
```

### Set Up Alerts

Create alerts for failed deployments:

1. Go to **Settings → Notifications**
2. Enable **GitHub Actions** notifications
3. Choose notification method (email, Slack, etc.)

## Troubleshooting

### Authentication Failures

```bash
# Test service principal
az login --service-principal \
  -u <clientId> \
  -p <clientSecret> \
  --tenant <tenantId>

# Verify permissions
az role assignment list --assignee <clientId>
```

### Image Build Failures

```bash
# Test build locally
docker build -f api/Dockerfile -t test-api .
docker build -f frontend/Dockerfile -t test-frontend ./frontend

# Check ACR connectivity
az acr login --name rmctriageacr
```

### Deployment Failures

```bash
# Check Container Apps status
az containerapp show --name rmc-api --resource-group rmc-triage-rg

# View logs
az containerapp logs show --name rmc-api --resource-group rmc-triage-rg --tail 100

# Check recent revisions
az containerapp revision list --name rmc-api --resource-group rmc-triage-rg
```

### Health Check Failures

```bash
# Test health endpoint manually
API_URL=$(az containerapp show --name rmc-api --resource-group rmc-triage-rg \
  --query "properties.configuration.ingress.fqdn" -o tsv)
curl -v https://$API_URL/health

# Check container logs
az containerapp logs show --name rmc-api --resource-group rmc-triage-rg --follow
```

## Rollback

If a deployment fails, rollback using the workflow artifact:

```bash
# From GitHub UI:
# 1. Go to failed workflow run
# 2. Find "Rollback Command" in summary
# 3. Run the command locally

# Or use rollback script:
cd infra
./rollback.sh <previous-image-tag>
```

## Best Practices

1. **Use Environment Protection**: Require reviews for production deployments
2. **Test Thoroughly**: Run all tests before merging to main
3. **Monitor Deployments**: Watch the workflow progress for failures
4. **Keep Secrets Secure**: Rotate secrets regularly
5. **Use Semantic Versioning**: Tag releases with version numbers
6. **Document Changes**: Update CHANGELOG.md for each release
7. **Review Logs**: Check deployment logs for warnings
8. **Set Up Alerts**: Get notified of deployment failures

## Security Considerations

- Service principal has minimal required permissions (Contributor on resource group only)
- Secrets are stored in GitHub encrypted secrets
- Container images are scanned for vulnerabilities
- All connections use HTTPS/TLS
- Database credentials stored in Azure Key Vault
- Managed identities used for Azure resource access

## Cost Optimization

- Workflow uses caching for Docker builds (saves time and bandwidth)
- Only deploys on specific branches (main/staging)
- Can be configured to skip deployments for documentation changes
- Uses self-hosted runners for cost savings (optional)

## Next Steps

1. Set up branch protection rules
2. Configure required reviewers
3. Add integration tests
4. Set up monitoring and alerts
5. Configure Slack/Discord notifications
6. Add deployment approval workflows
7. Set up rollback automation

## Resources

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Azure Login Action](https://github.com/Azure/login)
- [Docker Build Action](https://github.com/docker/build-push-action)
- [Azure Container Apps Documentation](https://docs.microsoft.com/azure/container-apps)

---

**Questions?** Check the [main README](README.md) or [Quick Start Guide](QUICKSTART.md).
