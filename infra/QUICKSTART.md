# RMC Triage - Quick Start Guide

Fast track to deploying your FastAPI + Next.js application to Azure.

## Prerequisites (5 minutes)

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Install Docker (for local development)
# macOS: brew install --cask docker
# Linux: curl -fsSL https://get.docker.com | sh
```

## Production Deployment (25 minutes)

### Step 1: Provision Infrastructure (15-20 minutes)

```bash
cd infra
chmod +x provision.sh deploy.sh rollback.sh
./provision.sh
```

This creates:
- PostgreSQL database (Standard_B1ms, 32GB)
- Redis cache (Basic C0)
- Azure Storage (Blob + File Share)
- Key Vault with all secrets
- Container Apps environment

### Step 2: Deploy Application (10-15 minutes)

```bash
./deploy.sh
```

This:
- Builds Docker images with git SHA tags
- Runs database migrations
- Deploys API, Frontend, and Celery worker
- Configures secrets and volume mounts
- Runs health checks

### Step 3: Get Your URLs

```bash
# Using make
make urls

# Or manually
az containerapp show --name rmc-api --resource-group rmc-triage-rg \
  --query "properties.configuration.ingress.fqdn" -o tsv

az containerapp show --name rmc-frontend --resource-group rmc-triage-rg \
  --query "properties.configuration.ingress.fqdn" -o tsv
```

## Local Development (2 minutes)

### Quick Start

```bash
cd infra

# Create environment file
cp .env.example .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

Access your local environment:
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000
- **PostgreSQL:** localhost:5432 (postgres/postgres)
- **Redis:** localhost:6379 (password: redis123)

### Common Commands

```bash
# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build

# Run migrations
docker-compose exec api alembic upgrade head

# Access database
docker-compose exec postgres psql -U postgres -d rmc_triage

# Access Redis
docker-compose exec redis redis-cli -a redis123
```

## Using Make Commands (Recommended)

The Makefile provides convenient shortcuts:

### Development
```bash
make dev-up          # Start local environment
make dev-down        # Stop local environment
make dev-logs        # View logs
make dev-rebuild     # Rebuild and restart
```

### Deployment
```bash
make provision       # Create Azure infrastructure
make deploy          # Deploy application
make rollback TAG=abc123  # Rollback to version
```

### Monitoring
```bash
make status          # Show deployment status
make health          # Check application health
make urls            # Show application URLs
make logs-api        # View API logs
make logs-celery     # View Celery logs
make logs-frontend   # View frontend logs
```

### Database
```bash
make db-migrate      # Run migrations
make db-shell        # Open PostgreSQL shell
make db-reset        # Reset database (WARNING: destroys data)
```

### Secrets
```bash
make secrets-list    # List all secrets
make secrets-show SECRET=DATABASE-URL    # Show specific secret
make secrets-update SECRET=JWT-SECRET VALUE=newsecret  # Update secret
```

### Scaling
```bash
make scale-api MIN=2 MAX=10        # Scale API
make scale-celery MIN=2 MAX=5      # Scale Celery workers
```

### Utility
```bash
make help            # Show all commands
make check-tools     # Verify prerequisites
make env-setup       # Create .env file
```

## Common Tasks

### View Logs

```bash
# Local
docker-compose logs -f api
docker-compose logs -f celery-worker

# Azure
az containerapp logs show --name rmc-api --resource-group rmc-triage-rg --follow
az containerapp logs show --name rmc-celery-worker --resource-group rmc-triage-rg --follow
```

### Update Application

```bash
# Make code changes, then:
cd infra
./deploy.sh

# The script automatically:
# - Tags images with current git SHA
# - Builds and pushes new images
# - Updates all container apps
# - Runs health checks
```

### Rollback Deployment

```bash
# List available versions
./rollback.sh

# Rollback to specific version
./rollback.sh a1b2c3d
```

### Scale Resources

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

### Access Secrets

```bash
# List all secrets
az keyvault secret list --vault-name rmc-triage-kv --output table

# Get specific secret
az keyvault secret show --vault-name rmc-triage-kv --name DATABASE-URL --query value -o tsv

# Update secret
az keyvault secret set --vault-name rmc-triage-kv --name JWT-SECRET --value "new-secret"

# Restart to apply new secrets
az containerapp revision restart --name rmc-api --resource-group rmc-triage-rg
```

## Architecture at a Glance

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│     API     │────▶│   Celery    │
│  (Next.js)  │     │  (FastAPI)  │     │   Worker    │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                    │
                    ┌──────▼────────────────────▼──────┐
                    │                                   │
              ┌─────▼─────┐                    ┌───────▼────┐
              │ PostgreSQL │                    │   Redis    │
              └────────────┘                    └────────────┘

              ┌─────────────────────────────────────────────┐
              │         Azure Storage Account              │
              │  • Blob Container (amcas-uploads)          │
              │  • File Share (rmc-data, mounted volumes)  │
              └─────────────────────────────────────────────┘

              ┌─────────────────────────────────────────────┐
              │            Azure Key Vault                 │
              │  • DATABASE_URL • REDIS_URL • JWT_SECRET   │
              └─────────────────────────────────────────────┘
```

## Cost Estimate

**~$70-110/month** for production environment:
- Container Apps: $20-50
- PostgreSQL: $25-30
- Redis: $16
- Storage: $2-5
- Container Registry: $5
- Key Vault: <$1

## Troubleshooting

### Container App Not Starting

```bash
# Check logs
az containerapp logs show --name rmc-api --resource-group rmc-triage-rg --tail 100

# Check revision status
az containerapp revision list --name rmc-api --resource-group rmc-triage-rg --output table
```

### Database Connection Issues

```bash
# Test connectivity
az postgres flexible-server connect \
  --name rmc-triage-postgres \
  --resource-group rmc-triage-rg \
  --admin-user rmcadmin

# View connection string
az keyvault secret show --vault-name rmc-triage-kv --name DATABASE-URL --query value -o tsv
```

### Health Check Failures

```bash
# Check API health endpoint
API_URL=$(az containerapp show --name rmc-api --resource-group rmc-triage-rg \
  --query "properties.configuration.ingress.fqdn" -o tsv)
curl https://$API_URL/health

# Check container status
az containerapp show --name rmc-api --resource-group rmc-triage-rg \
  --query "properties.runningStatus"
```

## Next Steps

1. **Set up monitoring**: Configure Azure Monitor alerts for high CPU/memory
2. **Enable auto-scaling**: Adjust min/max replicas based on load patterns
3. **Configure custom domain**: Add your own domain to Container Apps
4. **Set up CI/CD**: Integrate with GitHub Actions for automated deployments
5. **Review security**: Enable network policies, rotate secrets regularly

## Resources

- **Full Documentation**: `/Users/JCR/Desktop/rmc_every/infra/README.md`
- **Scripts**: `provision.sh`, `deploy.sh`, `rollback.sh`
- **Local Dev**: `docker-compose.yml`, `.env.example`
- **Makefile**: Run `make help` for all commands

## Support

- **Azure Docs**: https://docs.microsoft.com/azure/container-apps
- **Check Status**: `make status`
- **View Logs**: `make logs-api`
- **Health Check**: `make health`

---

**Happy deploying! 🚀**
