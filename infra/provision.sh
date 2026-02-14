#!/usr/bin/env bash
# provision.sh - Provision all Azure infrastructure resources for RMC Triage
# This script creates the complete Azure environment including networking, storage, databases, and container infrastructure
set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================
RG=rmc-triage-rg
LOCATION=centralus
ACR_NAME=rmctriageacr
ENV_NAME=rmc-triage-env
KV_NAME=rmc-triage-kv
STORAGE_ACCOUNT=rmctriagestorage
POSTGRES_SERVER=rmc-triage-postgres
REDIS_NAME=rmc-triage-redis

# Database configuration
DB_ADMIN_USER=rmcadmin
DB_ADMIN_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
DB_NAME=rmc_triage
JWT_SECRET=$(openssl rand -base64 32)

echo "=========================================="
echo "RMC Triage - Azure Infrastructure Provisioning"
echo "=========================================="
echo "Resource Group: $RG"
echo "Location: $LOCATION"
echo "=========================================="

# ============================================================================
# 1. RESOURCE GROUP
# ============================================================================
echo ""
echo "=== 1. Creating Resource Group ==="
if az group show --name "$RG" &>/dev/null; then
  echo "Resource group '$RG' already exists"
else
  az group create --name "$RG" --location "$LOCATION"
  echo "✓ Resource group created"
fi

# ============================================================================
# 2. CONTAINER REGISTRY (ACR)
# ============================================================================
echo ""
echo "=== 2. Creating Azure Container Registry ==="
if az acr show --name "$ACR_NAME" --resource-group "$RG" &>/dev/null; then
  echo "ACR '$ACR_NAME' already exists"
else
  az acr create \
    --resource-group "$RG" \
    --name "$ACR_NAME" \
    --sku Basic \
    --admin-enabled true
  echo "✓ Container Registry created"
fi

# ============================================================================
# 3. POSTGRESQL FLEXIBLE SERVER
# ============================================================================
echo ""
echo "=== 3. Creating PostgreSQL Flexible Server ==="
if az postgres flexible-server show --name "$POSTGRES_SERVER" --resource-group "$RG" &>/dev/null; then
  echo "PostgreSQL server '$POSTGRES_SERVER' already exists"
else
  echo "Creating PostgreSQL Flexible Server (this may take 5-10 minutes)..."
  az postgres flexible-server create \
    --resource-group "$RG" \
    --name "$POSTGRES_SERVER" \
    --location "$LOCATION" \
    --admin-user "$DB_ADMIN_USER" \
    --admin-password "$DB_ADMIN_PASS" \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 16 \
    --public-access 0.0.0.0-0.0.0.0 \
    --backup-retention 35 \
    --yes

  echo "✓ PostgreSQL server created"

  # Create database
  echo "Creating database '$DB_NAME'..."
  az postgres flexible-server db create \
    --resource-group "$RG" \
    --server-name "$POSTGRES_SERVER" \
    --database-name "$DB_NAME"

  echo "✓ Database created"

  # Configure SSL enforcement
  echo "Configuring SSL enforcement..."
  az postgres flexible-server parameter set \
    --resource-group "$RG" \
    --server-name "$POSTGRES_SERVER" \
    --name require_secure_transport \
    --value ON

  echo "✓ SSL enforcement enabled"
fi

# Build DATABASE_URL
DATABASE_URL="postgresql://${DB_ADMIN_USER}:${DB_ADMIN_PASS}@${POSTGRES_SERVER}.postgres.database.azure.com/${DB_NAME}?sslmode=require"

# ============================================================================
# 4. AZURE CACHE FOR REDIS
# ============================================================================
echo ""
echo "=== 4. Creating Azure Cache for Redis ==="
if az redis show --name "$REDIS_NAME" --resource-group "$RG" &>/dev/null; then
  echo "Redis cache '$REDIS_NAME' already exists"
else
  echo "Creating Redis cache (this may take 5-10 minutes)..."
  az redis create \
    --resource-group "$RG" \
    --name "$REDIS_NAME" \
    --location "$LOCATION" \
    --sku Basic \
    --vm-size c0 \
    --minimum-tls-version 1.2

  echo "✓ Redis cache created"
fi

# Get Redis connection string
echo "Retrieving Redis access keys..."
REDIS_KEY=$(az redis list-keys --name "$REDIS_NAME" --resource-group "$RG" --query primaryKey -o tsv)
REDIS_URL="rediss://:${REDIS_KEY}@${REDIS_NAME}.redis.cache.windows.net:6380/0?ssl_cert_reqs=required"

# ============================================================================
# 5. STORAGE ACCOUNT + BLOB + FILE SHARE
# ============================================================================
echo ""
echo "=== 5. Creating Storage Account ==="
if az storage account show --name "$STORAGE_ACCOUNT" --resource-group "$RG" &>/dev/null; then
  echo "Storage account '$STORAGE_ACCOUNT' already exists"
else
  az storage account create \
    --resource-group "$RG" \
    --name "$STORAGE_ACCOUNT" \
    --location "$LOCATION" \
    --sku Standard_LRS \
    --kind StorageV2 \
    --access-tier Hot \
    --allow-blob-public-access false \
    --https-only true \
    --min-tls-version TLS1_2

  echo "✓ Storage account created"
fi

# Get storage connection string
echo "Retrieving storage connection string..."
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RG" \
  --query connectionString -o tsv)

# Create blob container for uploads
echo "Creating blob container 'amcas-uploads'..."
az storage container create \
  --name amcas-uploads \
  --account-name "$STORAGE_ACCOUNT" \
  --connection-string "$STORAGE_CONNECTION_STRING" \
  --public-access off || echo "Container may already exist"

# Create file share for ML models and pipeline data
echo "Creating file share 'rmc-data'..."
az storage share create \
  --name rmc-data \
  --account-name "$STORAGE_ACCOUNT" \
  --connection-string "$STORAGE_CONNECTION_STRING" \
  --quota 100 || echo "File share may already exist"

# Configure lifecycle management policy (3-year retention, cool after 30 days)
echo "Configuring lifecycle management policy..."
cat > /tmp/lifecycle-policy.json <<EOF
{
  "rules": [
    {
      "enabled": true,
      "name": "archive-old-uploads",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "tierToCool": {
              "daysAfterModificationGreaterThan": 30
            },
            "tierToArchive": {
              "daysAfterModificationGreaterThan": 365
            },
            "delete": {
              "daysAfterModificationGreaterThan": 1095
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["amcas-uploads/"]
        }
      }
    }
  ]
}
EOF

az storage account management-policy create \
  --account-name "$STORAGE_ACCOUNT" \
  --resource-group "$RG" \
  --policy @/tmp/lifecycle-policy.json || echo "Lifecycle policy may already exist"

rm /tmp/lifecycle-policy.json
echo "✓ Storage configuration complete"

# ============================================================================
# 6. KEY VAULT
# ============================================================================
echo ""
echo "=== 6. Creating Key Vault ==="
if az keyvault show --name "$KV_NAME" --resource-group "$RG" &>/dev/null; then
  echo "Key Vault '$KV_NAME' already exists"
else
  az keyvault create \
    --resource-group "$RG" \
    --name "$KV_NAME" \
    --location "$LOCATION" \
    --enable-rbac-authorization false \
    --enable-purge-protection true

  echo "✓ Key Vault created"
fi

# Store secrets in Key Vault
echo "Storing secrets in Key Vault..."
az keyvault secret set --vault-name "$KV_NAME" --name "DATABASE-URL" --value "$DATABASE_URL" --output none
az keyvault secret set --vault-name "$KV_NAME" --name "REDIS-URL" --value "$REDIS_URL" --output none
az keyvault secret set --vault-name "$KV_NAME" --name "JWT-SECRET" --value "$JWT_SECRET" --output none
az keyvault secret set --vault-name "$KV_NAME" --name "AZURE-STORAGE-CONNECTION-STRING" --value "$STORAGE_CONNECTION_STRING" --output none
az keyvault secret set --vault-name "$KV_NAME" --name "DB-ADMIN-USER" --value "$DB_ADMIN_USER" --output none
az keyvault secret set --vault-name "$KV_NAME" --name "DB-ADMIN-PASS" --value "$DB_ADMIN_PASS" --output none

echo "✓ Secrets stored in Key Vault"

# ============================================================================
# 7. CONTAINER APPS ENVIRONMENT
# ============================================================================
echo ""
echo "=== 7. Creating Container Apps Environment ==="
if az containerapp env show --name "$ENV_NAME" --resource-group "$RG" &>/dev/null; then
  echo "Container Apps environment '$ENV_NAME' already exists"
else
  az containerapp env create \
    --name "$ENV_NAME" \
    --resource-group "$RG" \
    --location "$LOCATION"

  echo "✓ Container Apps environment created"
fi

# Create storage mount for Azure Files
echo "Creating storage mount for Azure Files..."
STORAGE_ACCOUNT_KEY=$(az storage account keys list \
  --account-name "$STORAGE_ACCOUNT" \
  --resource-group "$RG" \
  --query "[0].value" -o tsv)

az containerapp env storage set \
  --name "$ENV_NAME" \
  --resource-group "$RG" \
  --storage-name rmc-data-storage \
  --azure-file-account-name "$STORAGE_ACCOUNT" \
  --azure-file-account-key "$STORAGE_ACCOUNT_KEY" \
  --azure-file-share-name rmc-data \
  --access-mode ReadWrite || echo "Storage mount may already exist"

echo "✓ Azure Files storage mount configured"

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo "=========================================="
echo "✓ Provisioning Complete"
echo "=========================================="
echo ""
echo "Resources created:"
echo "  Resource Group:      $RG"
echo "  Container Registry:  $ACR_NAME"
echo "  PostgreSQL Server:   $POSTGRES_SERVER"
echo "  Redis Cache:         $REDIS_NAME"
echo "  Storage Account:     $STORAGE_ACCOUNT"
echo "  Key Vault:           $KV_NAME"
echo "  Container Apps Env:  $ENV_NAME"
echo ""
echo "Key Vault Secrets:"
echo "  - DATABASE-URL"
echo "  - REDIS-URL"
echo "  - JWT-SECRET"
echo "  - AZURE-STORAGE-CONNECTION-STRING"
echo "  - DB-ADMIN-USER"
echo "  - DB-ADMIN-PASS"
echo ""
echo "Next steps:"
echo "  1. Run ./deploy.sh to deploy the application"
echo "  2. Access Key Vault secrets: az keyvault secret show --vault-name $KV_NAME --name <secret-name>"
echo ""
echo "Database connection:"
echo "  Server: ${POSTGRES_SERVER}.postgres.database.azure.com"
echo "  Database: $DB_NAME"
echo "  User: $DB_ADMIN_USER"
echo ""
echo "=========================================="
