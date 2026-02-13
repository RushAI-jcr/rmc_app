# RMC Triage - Azure Infrastructure

Complete Azure deployment architecture for the RMC Triage application (FastAPI + Next.js + Celery + PostgreSQL + Redis).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Container Apps                      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Frontend   │  │     API      │  │    Celery    │      │
│  │   Next.js    │  │   FastAPI    │  │    Worker    │      │
│  │   (Port 3000)│  │  (Port 8000) │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
    ┌─────────▼─────────┐        ┌─────────▼─────────┐
    │   Azure Database  │        │  Azure Cache for  │
    │   for PostgreSQL  │        │      Redis        │
    │  (Flexible Server)│        │   (Basic C0)      │
    └───────────────────┘        └───────────────────┘

    ┌─────────────────────────────────────────────┐
    │         Azure Storage Account               │
    ├─────────────────────────────────────────────┤
    │  • Blob Container (amcas-uploads)           │
    │  • File Share (rmc-data) - mounted volumes  │
    │  • Lifecycle Management (3-year retention)  │
    └─────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────┐
    │            Azure Key Vault                  │
    ├─────────────────────────────────────────────┤
    │  • DATABASE_URL                             │
    │  • REDIS_URL                                │
    │  • JWT_SECRET                               │
    │  • AZURE_STORAGE_CONNECTION_STRING          │
    └─────────────────────────────────────────────┘
```

## Directory Structure

```
infra/
├── provision.sh          # Create all Azure infrastructure
├── deploy.sh             # Deploy application containers
├── rollback.sh           # Rollback to previous deployment
├── docker-compose.yml    # Local development environment
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Prerequisites

### Required Tools

- **Azure CLI** (v2.50.0 or later)
  ```bash
  curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
  ```

- **Docker** (for local development)
  ```bash
  # macOS
  brew install --cask docker

  # Linux
  curl -fsSL https://get.docker.com | sh
  ```

- **Git** (for image tagging)
  ```bash
  brew install git  # macOS
  sudo apt install git  # Ubuntu/Debian
  ```

- **jq** (optional, for JSON parsing)
  ```bash
  brew install jq  # macOS
  sudo apt install jq  # Ubuntu/Debian
  ```

### Azure Setup

1. **Login to Azure**
   ```bash
   az login
   ```

2. **Set active subscription** (if you have multiple)
   ```bash
   az account list --output table
   az account set --subscription "Your Subscription Name"
   ```

3. **Register required resource providers**
   ```bash
   az provider register --namespace Microsoft.App
   az provider register --namespace Microsoft.OperationalInsights
   az provider register --namespace Microsoft.ContainerRegistry
   az provider register --namespace Microsoft.DBforPostgreSQL
   az provider register --namespace Microsoft.Cache
   az provider register --namespace Microsoft.Storage
   az provider register --namespace Microsoft.KeyVault
   ```

## Deployment Guide

### 1. Provision Infrastructure (One-Time Setup)

Run the provision script to create all Azure resources:

```bash
cd infra
chmod +x provision.sh deploy.sh rollback.sh
./provision.sh
```

This creates:
- Resource Group (`rmc-triage-rg`)
- Container Registry (`rmctriageacr`)
- PostgreSQL Flexible Server (`rmc-triage-postgres`)
  - Database: `rmc_triage`
  - SKU: Standard_B1ms
  - Storage: 32GB
  - Version: 16
  - Backup retention: 35 days
- Azure Cache for Redis (`rmc-triage-redis`)
  - SKU: Basic C0
  - TLS: 1.2+ required
- Storage Account (`rmctriagestorage`)
  - Blob container: `amcas-uploads`
  - File share: `rmc-data` (100GB)
  - Lifecycle policy: Cool after 30 days, Archive after 1 year, Delete after 3 years
- Key Vault (`rmc-triage-kv`)
  - Stores all secrets securely
- Container Apps Environment (`rmc-triage-env`)
  - Azure Files storage mount configured

**Duration:** 15-20 minutes

**Output:** The script saves all connection strings and secrets to Azure Key Vault.

### 2. Deploy Application

Deploy the application containers:

```bash
./deploy.sh
```

This performs:
1. Builds Docker images with git SHA tags
2. Pushes images to Azure Container Registry
3. Runs database migrations (Alembic)
4. Deploys Celery worker with Azure Files mount
5. Deploys API with Key Vault secret references
6. Deploys frontend
7. Runs post-deployment health checks

**Duration:** 10-15 minutes

**Output:** URLs for API and frontend

### 3. Verify Deployment

Check application health:

```bash
# Get URLs
API_URL=$(az containerapp show --name rmc-api --resource-group rmc-triage-rg --query "properties.configuration.ingress.fqdn" -o tsv)
FRONTEND_URL=$(az containerapp show --name rmc-frontend --resource-group rmc-triage-rg --query "properties.configuration.ingress.fqdn" -o tsv)

# Test API
curl https://$API_URL/health

# Open frontend
open https://$FRONTEND_URL
```

View logs:

```bash
# API logs
az containerapp logs show --name rmc-api --resource-group rmc-triage-rg --follow

# Celery worker logs
az containerapp logs show --name rmc-celery-worker --resource-group rmc-triage-rg --follow

# Frontend logs
az containerapp logs show --name rmc-frontend --resource-group rmc-triage-rg --follow
```

### 4. Rollback (If Needed)

Rollback to a previous deployment:

```bash
# List available image tags
./rollback.sh

# Rollback to specific tag
./rollback.sh a1b2c3d
```

## Local Development

### Setup Local Environment

1. **Copy environment template**
   ```bash
   cd infra
   cp .env.example .env
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f
   ```

4. **Stop services**
   ```bash
   docker-compose down
   ```

### Local Services

- **API:** http://localhost:8000
  - Health: http://localhost:8000/health
  - Docs: http://localhost:8000/docs

- **Frontend:** http://localhost:3000

- **PostgreSQL:** localhost:5432
  - Database: `rmc_triage`
  - User: `postgres`
  - Password: `postgres`

- **Redis:** localhost:6379
  - Password: `redis123`

- **Azurite (Storage Emulator):**
  - Blob: http://localhost:10000
  - Queue: http://localhost:10001
  - Table: http://localhost:10002

### Run Database Migrations Locally

```bash
docker-compose exec api alembic upgrade head
```

### Access Database Locally

```bash
docker-compose exec postgres psql -U postgres -d rmc_triage
```

### Access Redis CLI Locally

```bash
docker-compose exec redis redis-cli -a redis123
```

## Configuration

### Environment Variables

All production secrets are stored in Azure Key Vault and referenced in Container Apps:

| Secret Name | Description |
|-------------|-------------|
| `DATABASE-URL` | PostgreSQL connection string with SSL |
| `REDIS-URL` | Redis connection string with TLS |
| `JWT-SECRET` | JWT signing secret |
| `AZURE-STORAGE-CONNECTION-STRING` | Azure Storage connection string |
| `DB-ADMIN-USER` | PostgreSQL admin username |
| `DB-ADMIN-PASS` | PostgreSQL admin password |

### Retrieve Secrets

```bash
# View all secrets
az keyvault secret list --vault-name rmc-triage-kv --output table

# Get specific secret
az keyvault secret show --vault-name rmc-triage-kv --name DATABASE-URL --query value -o tsv
```

### Update Secrets

```bash
# Update a secret
az keyvault secret set --vault-name rmc-triage-kv --name JWT-SECRET --value "new-secret-value"

# Restart containers to pick up new values
az containerapp revision restart --name rmc-api --resource-group rmc-triage-rg
```

## Resource Scaling

### Manual Scaling

```bash
# Scale API
az containerapp update \
  --name rmc-api \
  --resource-group rmc-triage-rg \
  --min-replicas 2 \
  --max-replicas 10

# Scale Celery workers
az containerapp update \
  --name rmc-celery-worker \
  --resource-group rmc-triage-rg \
  --min-replicas 2 \
  --max-replicas 5
```

### Database Scaling

```bash
# Upgrade PostgreSQL SKU
az postgres flexible-server update \
  --resource-group rmc-triage-rg \
  --name rmc-triage-postgres \
  --sku-name Standard_B2s

# Increase storage
az postgres flexible-server update \
  --resource-group rmc-triage-rg \
  --name rmc-triage-postgres \
  --storage-size 64
```

### Redis Scaling

```bash
# Upgrade Redis to Standard C1
az redis update \
  --resource-group rmc-triage-rg \
  --name rmc-triage-redis \
  --sku Standard \
  --vm-size c1
```

## Monitoring

### View Metrics

```bash
# Container Apps metrics
az monitor metrics list \
  --resource $(az containerapp show --name rmc-api --resource-group rmc-triage-rg --query id -o tsv) \
  --metric Requests

# Database metrics
az monitor metrics list \
  --resource $(az postgres flexible-server show --name rmc-triage-postgres --resource-group rmc-triage-rg --query id -o tsv) \
  --metric cpu_percent
```

### Set Up Alerts

```bash
# High CPU alert for API
az monitor metrics alert create \
  --name api-high-cpu \
  --resource-group rmc-triage-rg \
  --scopes $(az containerapp show --name rmc-api --resource-group rmc-triage-rg --query id -o tsv) \
  --condition "avg Percentage CPU > 80" \
  --window-size 5m \
  --evaluation-frequency 1m
```

## Backup and Recovery

### Database Backups

Automated backups are enabled with 35-day retention. To restore:

```bash
# List available backups
az postgres flexible-server backup list \
  --resource-group rmc-triage-rg \
  --server-name rmc-triage-postgres

# Restore from backup
az postgres flexible-server restore \
  --resource-group rmc-triage-rg \
  --name rmc-triage-postgres-restored \
  --source-server rmc-triage-postgres \
  --restore-time "2024-01-15T10:00:00Z"
```

### Storage Backups

Configure geo-redundant storage for critical data:

```bash
az storage account update \
  --name rmctriagestorage \
  --resource-group rmc-triage-rg \
  --sku Standard_GRS
```

## Cost Optimization

### Estimated Monthly Costs (US Central)

| Resource | SKU/Size | Est. Cost |
|----------|----------|-----------|
| Container Apps | Consumption (3 apps) | $20-50 |
| PostgreSQL | Standard_B1ms, 32GB | $25-30 |
| Redis | Basic C0 | $16 |
| Storage | Standard LRS, 100GB | $2-5 |
| Container Registry | Basic | $5 |
| Key Vault | Standard | $0.03/10k ops |
| **Total** | | **~$70-110/month** |

### Cost Reduction Tips

1. **Stop non-production environments**
   ```bash
   az containerapp update --name rmc-api --resource-group rmc-triage-rg --min-replicas 0
   ```

2. **Use Burstable PostgreSQL tier** (already configured)

3. **Enable auto-pause for development databases**

4. **Use lifecycle policies for blob storage** (already configured)

## Troubleshooting

### Container App Not Starting

```bash
# Check revision status
az containerapp revision list --name rmc-api --resource-group rmc-triage-rg --output table

# View detailed logs
az containerapp logs show --name rmc-api --resource-group rmc-triage-rg --tail 100

# Check environment variables
az containerapp show --name rmc-api --resource-group rmc-triage-rg --query properties.template.containers[0].env
```

### Database Connection Issues

```bash
# Test connectivity
az postgres flexible-server connect \
  --name rmc-triage-postgres \
  --resource-group rmc-triage-rg \
  --admin-user rmcadmin

# Check firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group rmc-triage-rg \
  --server-name rmc-triage-postgres
```

### Redis Connection Issues

```bash
# Test Redis connectivity
az redis force-reboot \
  --name rmc-triage-redis \
  --resource-group rmc-triage-rg \
  --reboot-type AllNodes

# Get Redis keys
az redis list-keys --name rmc-triage-redis --resource-group rmc-triage-rg
```

### Storage Access Issues

```bash
# Verify container exists
az storage container exists \
  --name amcas-uploads \
  --account-name rmctriagestorage

# Check file share
az storage share exists \
  --name rmc-data \
  --account-name rmctriagestorage
```

## Cleanup

### Delete All Resources

```bash
# Delete resource group (CAUTION: This deletes everything)
az group delete --name rmc-triage-rg --yes --no-wait
```

### Delete Individual Components

```bash
# Delete Container Apps only
az containerapp delete --name rmc-api --resource-group rmc-triage-rg --yes
az containerapp delete --name rmc-frontend --resource-group rmc-triage-rg --yes
az containerapp delete --name rmc-celery-worker --resource-group rmc-triage-rg --yes

# Delete databases (WARNING: Data loss)
az postgres flexible-server delete --resource-group rmc-triage-rg --name rmc-triage-postgres --yes
az redis delete --name rmc-triage-redis --resource-group rmc-triage-rg --yes
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Deploy Application
        run: |
          cd infra
          ./deploy.sh
```

### Setup Azure Service Principal

```bash
# Create service principal for CI/CD
az ad sp create-for-rbac \
  --name rmc-triage-github-actions \
  --role Contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/rmc-triage-rg \
  --sdk-auth

# Save output as GitHub secret AZURE_CREDENTIALS
```

## Security Best Practices

- ✅ SSL/TLS enforced on all databases
- ✅ Secrets stored in Azure Key Vault
- ✅ Managed identities for Key Vault access
- ✅ Private networking between Container Apps
- ✅ Storage account with HTTPS-only access
- ✅ Container images from private ACR
- ✅ Minimum TLS 1.2 for all services

## Support

For issues or questions:
- Check Azure documentation: https://docs.microsoft.com/azure
- View Container Apps logs: `az containerapp logs show`
- Check application health endpoints
- Review this README for troubleshooting steps

## License

Copyright (c) 2024 RMC Triage. All rights reserved.
