# Infrastructure Files Reference

Complete list of all infrastructure and deployment files for the RMC Triage application.

## Directory Structure

```
rmc_every/
├── .github/
│   └── workflows/
│       └── azure-deploy.yml          # GitHub Actions CI/CD workflow
│
├── infra/
│   ├── provision.sh                  # Provision Azure infrastructure
│   ├── deploy.sh                     # Deploy application to Azure
│   ├── rollback.sh                   # Rollback to previous deployment
│   ├── docker-compose.yml            # Local development environment
│   ├── .env.example                  # Environment variables template
│   ├── Makefile                      # Convenience commands
│   ├── README.md                     # Full documentation
│   ├── QUICKSTART.md                 # Quick start guide
│   ├── CICD-SETUP.md                 # CI/CD setup instructions
│   └── FILES.md                      # This file
│
├── api/
│   ├── Dockerfile                    # API Docker image (also used for Celery)
│   └── requirements.txt              # Python dependencies
│
└── frontend/
    ├── Dockerfile                    # Frontend Docker image
    └── package.json                  # Node.js dependencies
```

## File Descriptions

### Deployment Scripts

#### `/Users/JCR/Desktop/rmc_every/infra/provision.sh`
**Purpose:** One-time infrastructure provisioning script

**Creates:**
- Resource Group (rmc-triage-rg)
- Azure Container Registry (rmctriageacr)
- PostgreSQL Flexible Server (rmc-triage-postgres)
  - Database: rmc_triage
  - SKU: Standard_B1ms
  - Storage: 32GB
  - Version: 16
  - SSL enforced
  - 35-day backup retention
- Azure Cache for Redis (rmc-triage-redis)
  - SKU: Basic C0
  - TLS 1.2+ enabled
- Storage Account (rmctriagestorage)
  - Blob container: amcas-uploads
  - File share: rmc-data (100GB)
  - Lifecycle policy (3-year retention)
- Key Vault (rmc-triage-kv)
  - Stores all secrets
- Container Apps Environment (rmc-triage-env)
  - Azure Files storage mount

**Duration:** 15-20 minutes

**Usage:**
```bash
cd infra
chmod +x provision.sh
./provision.sh
```

---

#### `/Users/JCR/Desktop/rmc_every/infra/deploy.sh`
**Purpose:** Deploy application to Azure Container Apps

**Performs:**
1. Builds Docker images with git SHA tags
2. Pushes images to Azure Container Registry
3. Retrieves Key Vault secret references
4. Runs database migrations (Alembic job)
5. Deploys Celery worker with Azure Files mount
6. Deploys API with secrets and volume mounts
7. Deploys Frontend
8. Enables managed identities
9. Grants Key Vault access
10. Runs post-deployment health checks

**Duration:** 10-15 minutes

**Usage:**
```bash
cd infra
./deploy.sh
```

**Output:**
- API URL: https://rmc-api.azurecontainerapps.io
- Frontend URL: https://rmc-frontend.azurecontainerapps.io
- Image tag saved for rollback

---

#### `/Users/JCR/Desktop/rmc_every/infra/rollback.sh`
**Purpose:** Rollback to previous deployment

**Features:**
- Lists available image tags from ACR
- Verifies images exist before rollback
- Backs up current deployment info
- Confirms before executing
- Rolls back all container apps (API, Frontend, Celery)
- Runs health checks after rollback
- Provides recovery instructions

**Duration:** 5-10 minutes

**Usage:**
```bash
cd infra
./rollback.sh              # List available tags
./rollback.sh a1b2c3d      # Rollback to specific tag
```

---

### Local Development

#### `/Users/JCR/Desktop/rmc_every/infra/docker-compose.yml`
**Purpose:** Complete local development environment

**Services:**
1. **postgres** - PostgreSQL 16 database
   - Port: 5432
   - Health checks enabled
   - Persistent volume

2. **redis** - Redis 7 cache
   - Port: 6379
   - Health checks enabled
   - Persistent volume

3. **azurite** - Azure Storage emulator
   - Blob: 10000
   - Queue: 10001
   - Table: 10002

4. **api** - FastAPI backend
   - Port: 8000
   - Volume mount: data/
   - Depends on: postgres, redis, azurite

5. **celery-worker** - Background task worker
   - Same image as API
   - Volume mount: data/
   - Depends on: postgres, redis, azurite

6. **frontend** - Next.js frontend
   - Port: 3000
   - Depends on: api

**Usage:**
```bash
cd infra
docker-compose up -d          # Start all services
docker-compose logs -f        # View logs
docker-compose down           # Stop all services
docker-compose down -v        # Stop and remove volumes
```

---

#### `/Users/JCR/Desktop/rmc_every/infra/.env.example`
**Purpose:** Environment variables template for local development

**Contains:**
- Database configuration
- Redis configuration
- Celery configuration
- Azure Storage (Azurite) configuration
- JWT authentication settings
- Application configuration
- Development tool settings

**Usage:**
```bash
cd infra
cp .env.example .env
# Edit .env with your values
```

---

### Convenience Tools

#### `/Users/JCR/Desktop/rmc_every/infra/Makefile`
**Purpose:** Convenient shortcuts for common operations

**Categories:**
- **Azure Deployment:** provision, deploy, rollback
- **Local Development:** dev-up, dev-down, dev-logs, dev-restart, dev-rebuild
- **Database:** db-migrate, db-shell, db-reset
- **Monitoring:** logs-api, logs-frontend, logs-celery, status, health, urls
- **Secrets:** secrets-list, secrets-show, secrets-update
- **Scaling:** scale-api, scale-celery
- **Cleanup:** clean, clean-local
- **Utility:** env-setup, check-tools, help

**Usage:**
```bash
make help                     # Show all commands
make provision                # Provision infrastructure
make deploy                   # Deploy application
make dev-up                   # Start local dev environment
make logs-api                 # View API logs
make scale-api MIN=2 MAX=10   # Scale API
```

---

### Documentation

#### `/Users/JCR/Desktop/rmc_every/infra/README.md`
**Purpose:** Complete infrastructure documentation

**Sections:**
- Architecture overview with diagrams
- Directory structure
- Prerequisites and Azure setup
- Deployment guide (step-by-step)
- Local development guide
- Configuration and secrets management
- Resource scaling
- Monitoring and metrics
- Backup and recovery
- Cost optimization
- Troubleshooting
- Cleanup procedures
- CI/CD integration
- Security best practices

**Size:** ~500 lines, comprehensive reference

---

#### `/Users/JCR/Desktop/rmc_every/infra/QUICKSTART.md`
**Purpose:** Fast-track deployment guide

**Sections:**
- Prerequisites (5 minutes)
- Production deployment (25 minutes)
- Local development (2 minutes)
- Make command reference
- Common tasks
- Architecture at a glance
- Cost estimate
- Troubleshooting
- Next steps

**Size:** ~300 lines, quick reference

---

#### `/Users/JCR/Desktop/rmc_every/infra/CICD-SETUP.md`
**Purpose:** Complete CI/CD setup guide

**Sections:**
- Overview of CI/CD pipeline
- Prerequisites
- Creating Azure service principal
- Getting ACR credentials
- Configuring GitHub secrets
- Verifying workflow file
- Testing the workflow
- Workflow details and jobs
- Deployment flow diagram
- Environment setup
- Branch strategy
- Customization options
- Monitoring deployments
- Troubleshooting
- Best practices
- Security considerations

**Size:** ~400 lines, detailed setup guide

---

### CI/CD Workflow

#### `/Users/JCR/Desktop/rmc_every/.github/workflows/azure-deploy.yml`
**Purpose:** Automated CI/CD pipeline for GitHub Actions

**Jobs:**
1. **test** - Run tests with PostgreSQL and Redis services
   - Python 3.12
   - pytest with coverage
   - Upload to Codecov

2. **security** - Security scanning
   - Trivy vulnerability scanner
   - Upload to GitHub Security

3. **deploy** - Build and deploy
   - Build Docker images with cache
   - Push to ACR with git SHA tags
   - Run database migrations
   - Deploy Celery worker
   - Deploy API
   - Deploy Frontend
   - Health checks
   - Deployment summary

4. **notify** - Send notifications
   - Slack webhook
   - Discord webhook

**Triggers:**
- Push to main/staging branches
- Pull requests to main
- Manual workflow dispatch

**Environments:**
- Production (main branch)
- Staging (other branches)

---

### Application Dockerfiles

#### `/Users/JCR/Desktop/rmc_every/api/Dockerfile`
**Purpose:** Build Docker image for FastAPI API and Celery worker

**Base Image:** python:3.12-slim

**Contents:**
- Install Python dependencies
- Copy pipeline and API code
- Copy data directory
- Expose port 8000

**Usage:**
- API: `uvicorn api.main:app --host 0.0.0.0 --port 8000`
- Celery: `celery -A api.celery_app worker --loglevel=info`

---

#### `/Users/JCR/Desktop/rmc_every/frontend/Dockerfile`
**Purpose:** Build Docker image for Next.js frontend

**Multi-stage Build:**
1. **Builder:** node:22-alpine
   - Install dependencies
   - Build Next.js application
   - Create standalone output

2. **Runner:** node:22-alpine
   - Copy standalone output
   - Copy static files
   - Expose port 3000

**Build Args:**
- NEXT_PUBLIC_API_URL (API endpoint)

---

## Quick Reference

### First Time Setup

```bash
# 1. Provision infrastructure (one-time)
cd /Users/JCR/Desktop/rmc_every/infra
chmod +x provision.sh deploy.sh rollback.sh
./provision.sh

# 2. Deploy application
./deploy.sh

# 3. Get URLs
make urls
```

### Local Development

```bash
# Start local environment
cd /Users/JCR/Desktop/rmc_every/infra
cp .env.example .env
make dev-up

# View logs
make dev-logs

# Stop environment
make dev-down
```

### Update Application

```bash
# Make code changes, then:
cd /Users/JCR/Desktop/rmc_every/infra
./deploy.sh

# Or use make:
make deploy
```

### Rollback

```bash
# List available versions
./rollback.sh

# Rollback to specific version
./rollback.sh a1b2c3d

# Or use make:
make rollback TAG=a1b2c3d
```

### CI/CD Setup

```bash
# Follow detailed instructions in:
/Users/JCR/Desktop/rmc_every/infra/CICD-SETUP.md

# Quick version:
# 1. Create Azure service principal
# 2. Add GitHub secrets
# 3. Push to main branch
```

## File Dependencies

```
provision.sh
    ↓ creates
Azure Resources (PostgreSQL, Redis, Storage, Key Vault, etc.)
    ↓ used by
deploy.sh
    ↓ uses
Dockerfile (api/Dockerfile, frontend/Dockerfile)
    ↓ builds
Docker Images (tagged with git SHA)
    ↓ deployed to
Azure Container Apps (API, Frontend, Celery Worker)
    ↓ monitored by
azure-deploy.yml (GitHub Actions)
    ↓ can rollback with
rollback.sh
```

## Important Notes

1. **Run provision.sh only once** - It creates the infrastructure
2. **Run deploy.sh for updates** - It deploys new code versions
3. **Use git SHA tags** - Images are tagged with git commit hashes for traceability
4. **Keep .env local** - Never commit .env files to git
5. **Store secrets in Key Vault** - Production secrets are in Azure Key Vault
6. **Use make commands** - Easier than remembering full commands
7. **Check health after deploy** - Use `make health` to verify deployment
8. **Enable CI/CD for automation** - Follow CICD-SETUP.md for setup

## Getting Help

- **Quick questions:** Check QUICKSTART.md
- **Detailed info:** Read README.md
- **CI/CD setup:** Follow CICD-SETUP.md
- **Local dev issues:** Check docker-compose.yml and .env.example
- **Deployment issues:** Check provision.sh and deploy.sh comments
- **Rollback issues:** Check rollback.sh comments

## File Sizes

| File | Lines | Purpose |
|------|-------|---------|
| provision.sh | ~350 | Infrastructure provisioning |
| deploy.sh | ~300 | Application deployment |
| rollback.sh | ~200 | Deployment rollback |
| docker-compose.yml | ~200 | Local development |
| .env.example | ~80 | Environment template |
| Makefile | ~300 | Convenience commands |
| README.md | ~500 | Full documentation |
| QUICKSTART.md | ~300 | Quick start guide |
| CICD-SETUP.md | ~400 | CI/CD setup guide |
| azure-deploy.yml | ~250 | GitHub Actions workflow |

**Total:** ~2,880 lines of infrastructure code and documentation

---

**All files are located in:** `/Users/JCR/Desktop/rmc_every/infra/`
