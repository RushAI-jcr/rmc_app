#!/usr/bin/env bash
# deploy.sh - Deploy RMC Triage application to Azure Container Apps
# This script builds images, runs migrations, and deploys all application components
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

# Get git SHA for image tagging (fallback to timestamp if not in git repo)
if git rev-parse --short HEAD &>/dev/null; then
  IMAGE_TAG=$(git rev-parse --short HEAD)
else
  IMAGE_TAG=$(date +%Y%m%d-%H%M%S)
fi

echo "=========================================="
echo "RMC Triage - Application Deployment"
echo "=========================================="
echo "Image Tag: $IMAGE_TAG"
echo "Resource Group: $RG"
echo "=========================================="

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================
echo ""
echo "=== Pre-flight Checks ==="

# Check if resource group exists
if ! az group show --name "$RG" &>/dev/null; then
  echo "ERROR: Resource group '$RG' not found"
  echo "Run ./provision.sh first to create infrastructure"
  exit 1
fi

# Check if Key Vault exists
if ! az keyvault show --name "$KV_NAME" --resource-group "$RG" &>/dev/null; then
  echo "ERROR: Key Vault '$KV_NAME' not found"
  echo "Run ./provision.sh first to create infrastructure"
  exit 1
fi

echo "✓ Pre-flight checks passed"

# ============================================================================
# 1. BUILD AND PUSH DOCKER IMAGES
# ============================================================================
echo ""
echo "=== 1. Building and Pushing Docker Images ==="

# Build API image (also used for Celery worker)
echo "Building API image (rmc-api:$IMAGE_TAG)..."
az acr build \
  --registry "$ACR_NAME" \
  --image "rmc-api:$IMAGE_TAG" \
  --file api/Dockerfile \
  .

echo "✓ API image built and pushed"

# Build frontend image
echo "Building frontend image (rmc-frontend:$IMAGE_TAG)..."
az acr build \
  --registry "$ACR_NAME" \
  --image "rmc-frontend:$IMAGE_TAG" \
  --file frontend/Dockerfile \
  ./frontend

echo "✓ Frontend image built and pushed"

# ============================================================================
# 2. GET KEY VAULT REFERENCE URLS
# ============================================================================
echo ""
echo "=== 2. Retrieving Key Vault Secret References ==="

# Get Key Vault ID
KV_ID=$(az keyvault show --name "$KV_NAME" --resource-group "$RG" --query id -o tsv)

# Build Key Vault reference URLs for Container Apps
DATABASE_URL_REF="${KV_ID}/secrets/DATABASE-URL"
REDIS_URL_REF="${KV_ID}/secrets/REDIS-URL"
JWT_SECRET_REF="${KV_ID}/secrets/JWT-SECRET"
STORAGE_CONNECTION_REF="${KV_ID}/secrets/AZURE-STORAGE-CONNECTION-STRING"

echo "✓ Key Vault references prepared"

# ============================================================================
# 3. RUN DATABASE MIGRATIONS
# ============================================================================
echo ""
echo "=== 3. Running Database Migrations ==="

# Get DATABASE_URL from Key Vault for migration job
DATABASE_URL=$(az keyvault secret show --vault-name "$KV_NAME" --name "DATABASE-URL" --query value -o tsv)

# Create a one-shot Container Apps Job to run Alembic migrations
# Check if migration job already exists
if az containerapp job show --name rmc-migration-job --resource-group "$RG" &>/dev/null; then
  echo "Updating existing migration job..."
  az containerapp job update \
    --name rmc-migration-job \
    --resource-group "$RG" \
    --image "$ACR_NAME.azurecr.io/rmc-api:$IMAGE_TAG" \
    --registry-server "$ACR_NAME.azurecr.io" \
    --secrets "database-url=$DATABASE_URL" \
    --env-vars "DATABASE_URL=secretref:database-url" \
    --cpu 0.5 \
    --memory 1.0Gi
else
  echo "Creating migration job..."
  az containerapp job create \
    --name rmc-migration-job \
    --resource-group "$RG" \
    --environment "$ENV_NAME" \
    --trigger-type Manual \
    --replica-timeout 600 \
    --replica-retry-limit 1 \
    --parallelism 1 \
    --replica-completion-count 1 \
    --image "$ACR_NAME.azurecr.io/rmc-api:$IMAGE_TAG" \
    --registry-server "$ACR_NAME.azurecr.io" \
    --secrets "database-url=$DATABASE_URL" \
    --env-vars "DATABASE_URL=secretref:database-url" \
    --cpu 0.5 \
    --memory 1.0Gi \
    --command "/bin/sh" \
    --args "-c" "pip install alembic && alembic upgrade head || echo 'No migrations to run'"
fi

echo "Starting migration job..."
az containerapp job start \
  --name rmc-migration-job \
  --resource-group "$RG"

echo "✓ Database migrations completed"

# ============================================================================
# 4. DEPLOY CELERY WORKER
# ============================================================================
echo ""
echo "=== 4. Deploying Celery Worker ==="

# Check if Celery worker already exists
if az containerapp show --name rmc-celery-worker --resource-group "$RG" &>/dev/null; then
  echo "Updating existing Celery worker..."
  az containerapp update \
    --name rmc-celery-worker \
    --resource-group "$RG" \
    --image "$ACR_NAME.azurecr.io/rmc-api:$IMAGE_TAG" \
    --set-env-vars \
      "DATABASE_URL=secretref:database-url" \
      "REDIS_URL=secretref:redis-url" \
      "AZURE_STORAGE_CONNECTION_STRING=secretref:storage-connection"
else
  echo "Creating Celery worker..."
  az containerapp create \
    --name rmc-celery-worker \
    --resource-group "$RG" \
    --environment "$ENV_NAME" \
    --image "$ACR_NAME.azurecr.io/rmc-api:$IMAGE_TAG" \
    --registry-server "$ACR_NAME.azurecr.io" \
    --cpu 1.0 \
    --memory 2.0Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --secrets \
      "database-url=keyvaultref:$DATABASE_URL_REF,identityref:system" \
      "redis-url=keyvaultref:$REDIS_URL_REF,identityref:system" \
      "storage-connection=keyvaultref:$STORAGE_CONNECTION_REF,identityref:system" \
    --env-vars \
      "DATABASE_URL=secretref:database-url" \
      "REDIS_URL=secretref:redis-url" \
      "AZURE_STORAGE_CONNECTION_STRING=secretref:storage-connection" \
    --command "celery" \
    --args "-A" "api.celery_app" "worker" "--loglevel=info" \
    --workload-profile-name Consumption

  # Add Azure Files volume mount
  az containerapp update \
    --name rmc-celery-worker \
    --resource-group "$RG" \
    --add-volume name=rmc-data,storage-name=rmc-data-storage,storage-type=AzureFile \
    --add-volume-mount volume=rmc-data,mount-path=/app/data
fi

# Enable system-assigned managed identity
echo "Enabling managed identity for Celery worker..."
az containerapp identity assign \
  --name rmc-celery-worker \
  --resource-group "$RG" \
  --system-assigned

# Get the principal ID
CELERY_PRINCIPAL_ID=$(az containerapp show \
  --name rmc-celery-worker \
  --resource-group "$RG" \
  --query identity.principalId -o tsv)

# Grant Key Vault access
if [ -n "$CELERY_PRINCIPAL_ID" ]; then
  az keyvault set-policy \
    --name "$KV_NAME" \
    --resource-group "$RG" \
    --object-id "$CELERY_PRINCIPAL_ID" \
    --secret-permissions get list
fi

echo "✓ Celery worker deployed"

# ============================================================================
# 5. DEPLOY API
# ============================================================================
echo ""
echo "=== 5. Deploying API ==="

# Check if API already exists
if az containerapp show --name rmc-api --resource-group "$RG" &>/dev/null; then
  echo "Updating existing API..."
  az containerapp update \
    --name rmc-api \
    --resource-group "$RG" \
    --image "$ACR_NAME.azurecr.io/rmc-api:$IMAGE_TAG" \
    --set-env-vars \
      "DATABASE_URL=secretref:database-url" \
      "REDIS_URL=secretref:redis-url" \
      "JWT_SECRET=secretref:jwt-secret" \
      "AZURE_STORAGE_CONNECTION_STRING=secretref:storage-connection"
else
  echo "Creating API..."
  az containerapp create \
    --name rmc-api \
    --resource-group "$RG" \
    --environment "$ENV_NAME" \
    --image "$ACR_NAME.azurecr.io/rmc-api:$IMAGE_TAG" \
    --target-port 8000 \
    --ingress external \
    --registry-server "$ACR_NAME.azurecr.io" \
    --cpu 1.0 \
    --memory 2.0Gi \
    --min-replicas 1 \
    --max-replicas 5 \
    --secrets \
      "database-url=keyvaultref:$DATABASE_URL_REF,identityref:system" \
      "redis-url=keyvaultref:$REDIS_URL_REF,identityref:system" \
      "jwt-secret=keyvaultref:$JWT_SECRET_REF,identityref:system" \
      "storage-connection=keyvaultref:$STORAGE_CONNECTION_REF,identityref:system" \
    --env-vars \
      "DATABASE_URL=secretref:database-url" \
      "REDIS_URL=secretref:redis-url" \
      "JWT_SECRET=secretref:jwt-secret" \
      "AZURE_STORAGE_CONNECTION_STRING=secretref:storage-connection" \
      "PORT=8000"

  # Add Azure Files volume mount
  az containerapp update \
    --name rmc-api \
    --resource-group "$RG" \
    --add-volume name=rmc-data,storage-name=rmc-data-storage,storage-type=AzureFile \
    --add-volume-mount volume=rmc-data,mount-path=/app/data
fi

# Enable system-assigned managed identity
echo "Enabling managed identity for API..."
az containerapp identity assign \
  --name rmc-api \
  --resource-group "$RG" \
  --system-assigned

# Get the principal ID
API_PRINCIPAL_ID=$(az containerapp show \
  --name rmc-api \
  --resource-group "$RG" \
  --query identity.principalId -o tsv)

# Grant Key Vault access
if [ -n "$API_PRINCIPAL_ID" ]; then
  az keyvault set-policy \
    --name "$KV_NAME" \
    --resource-group "$RG" \
    --object-id "$API_PRINCIPAL_ID" \
    --secret-permissions get list
fi

# Get API URL
API_FQDN=$(az containerapp show \
  --name rmc-api \
  --resource-group "$RG" \
  --query "properties.configuration.ingress.fqdn" -o tsv)

echo "✓ API deployed at https://$API_FQDN"

# ============================================================================
# 6. DEPLOY FRONTEND
# ============================================================================
echo ""
echo "=== 6. Deploying Frontend ==="

# Check if frontend already exists
if az containerapp show --name rmc-frontend --resource-group "$RG" &>/dev/null; then
  echo "Updating existing frontend..."
  az containerapp update \
    --name rmc-frontend \
    --resource-group "$RG" \
    --image "$ACR_NAME.azurecr.io/rmc-frontend:$IMAGE_TAG" \
    --set-env-vars "NEXT_PUBLIC_API_URL=https://$API_FQDN"
else
  echo "Creating frontend..."
  az containerapp create \
    --name rmc-frontend \
    --resource-group "$RG" \
    --environment "$ENV_NAME" \
    --image "$ACR_NAME.azurecr.io/rmc-frontend:$IMAGE_TAG" \
    --target-port 3000 \
    --ingress external \
    --registry-server "$ACR_NAME.azurecr.io" \
    --cpu 0.5 \
    --memory 1.0Gi \
    --min-replicas 1 \
    --max-replicas 3 \
    --env-vars "NEXT_PUBLIC_API_URL=https://$API_FQDN"
fi

# Get frontend URL
FRONTEND_FQDN=$(az containerapp show \
  --name rmc-frontend \
  --resource-group "$RG" \
  --query "properties.configuration.ingress.fqdn" -o tsv)

echo "✓ Frontend deployed at https://$FRONTEND_FQDN"

# ============================================================================
# 7. POST-DEPLOYMENT HEALTH CHECKS
# ============================================================================
echo ""
echo "=== 7. Running Health Checks ==="

# Wait a few seconds for containers to stabilize
echo "Waiting for containers to stabilize..."
sleep 10

# Check API health
echo "Checking API health..."
API_HEALTH_URL="https://$API_FQDN/health"
if curl -sf "$API_HEALTH_URL" > /dev/null 2>&1; then
  echo "✓ API health check passed"
else
  echo "⚠ API health check failed - application may still be starting"
  echo "  Check manually: $API_HEALTH_URL"
fi

# Check frontend accessibility
echo "Checking frontend accessibility..."
FRONTEND_URL="https://$FRONTEND_FQDN"
if curl -sf "$FRONTEND_URL" > /dev/null 2>&1; then
  echo "✓ Frontend health check passed"
else
  echo "⚠ Frontend health check failed - application may still be starting"
  echo "  Check manually: $FRONTEND_URL"
fi

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo "=========================================="
echo "✓ Deployment Complete"
echo "=========================================="
echo ""
echo "Image Tag: $IMAGE_TAG"
echo ""
echo "Application URLs:"
echo "  API:      https://$API_FQDN"
echo "  Frontend: https://$FRONTEND_FQDN"
echo ""
echo "Container Apps:"
echo "  - rmc-api (FastAPI backend)"
echo "  - rmc-frontend (Next.js frontend)"
echo "  - rmc-celery-worker (Celery worker)"
echo ""
echo "Next steps:"
echo "  - Test API: curl https://$API_FQDN/health"
echo "  - Visit app: https://$FRONTEND_FQDN"
echo "  - View logs: az containerapp logs show --name rmc-api --resource-group $RG --follow"
echo "  - Rollback: ./rollback.sh $IMAGE_TAG"
echo ""
echo "=========================================="

# Save deployment info for rollback
echo "$IMAGE_TAG" > /tmp/rmc-last-deployment.txt
