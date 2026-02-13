#!/usr/bin/env bash
# rollback.sh - Rollback RMC Triage application to a previous deployment
# This script reverts all Container Apps to a specified image tag
set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================
RG=rmc-triage-rg
ACR_NAME=rmctriageacr

# Get target image tag from argument or prompt
if [ $# -eq 0 ]; then
  echo "=========================================="
  echo "RMC Triage - Rollback Deployment"
  echo "=========================================="
  echo ""
  echo "Usage: $0 <image-tag>"
  echo ""
  echo "Available image tags in Azure Container Registry:"
  echo ""

  # List available API image tags
  echo "API images (rmc-api):"
  az acr repository show-tags \
    --name "$ACR_NAME" \
    --repository rmc-api \
    --orderby time_desc \
    --output table 2>/dev/null || echo "  No images found"

  echo ""
  echo "Frontend images (rmc-frontend):"
  az acr repository show-tags \
    --name "$ACR_NAME" \
    --repository rmc-frontend \
    --orderby time_desc \
    --output table 2>/dev/null || echo "  No images found"

  echo ""
  echo "Examples:"
  echo "  $0 a1b2c3d           # Rollback to git SHA"
  echo "  $0 20240101-120000   # Rollback to timestamp"
  echo ""
  exit 1
fi

IMAGE_TAG=$1

echo "=========================================="
echo "RMC Triage - Rollback Deployment"
echo "=========================================="
echo "Target Image Tag: $IMAGE_TAG"
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
  exit 1
fi

# Verify images exist in ACR
echo "Verifying images exist in ACR..."
if ! az acr repository show-tags --name "$ACR_NAME" --repository rmc-api --output tsv 2>/dev/null | grep -q "^${IMAGE_TAG}$"; then
  echo "ERROR: Image 'rmc-api:$IMAGE_TAG' not found in ACR"
  echo "Available tags:"
  az acr repository show-tags --name "$ACR_NAME" --repository rmc-api --orderby time_desc --output table
  exit 1
fi

if ! az acr repository show-tags --name "$ACR_NAME" --repository rmc-frontend --output tsv 2>/dev/null | grep -q "^${IMAGE_TAG}$"; then
  echo "ERROR: Image 'rmc-frontend:$IMAGE_TAG' not found in ACR"
  echo "Available tags:"
  az acr repository show-tags --name "$ACR_NAME" --repository rmc-frontend --orderby time_desc --output table
  exit 1
fi

echo "✓ Images verified in ACR"

# Get current deployment info for backup
echo "Backing up current deployment info..."
CURRENT_API_IMAGE=$(az containerapp show \
  --name rmc-api \
  --resource-group "$RG" \
  --query "properties.template.containers[0].image" -o tsv 2>/dev/null || echo "unknown")

CURRENT_FRONTEND_IMAGE=$(az containerapp show \
  --name rmc-frontend \
  --resource-group "$RG" \
  --query "properties.template.containers[0].image" -o tsv 2>/dev/null || echo "unknown")

CURRENT_CELERY_IMAGE=$(az containerapp show \
  --name rmc-celery-worker \
  --resource-group "$RG" \
  --query "properties.template.containers[0].image" -o tsv 2>/dev/null || echo "unknown")

echo ""
echo "Current deployment:"
echo "  API:      $CURRENT_API_IMAGE"
echo "  Frontend: $CURRENT_FRONTEND_IMAGE"
echo "  Celery:   $CURRENT_CELERY_IMAGE"
echo ""

# Confirmation prompt
read -p "Are you sure you want to rollback to $IMAGE_TAG? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Rollback cancelled"
  exit 0
fi

# ============================================================================
# ROLLBACK PROCESS
# ============================================================================
echo ""
echo "=== Starting Rollback ==="

# ============================================================================
# 1. ROLLBACK CELERY WORKER
# ============================================================================
echo ""
echo "=== 1. Rolling back Celery Worker ==="
if az containerapp show --name rmc-celery-worker --resource-group "$RG" &>/dev/null; then
  az containerapp update \
    --name rmc-celery-worker \
    --resource-group "$RG" \
    --image "$ACR_NAME.azurecr.io/rmc-api:$IMAGE_TAG"

  echo "✓ Celery worker rolled back"
else
  echo "⚠ Celery worker not found, skipping"
fi

# ============================================================================
# 2. ROLLBACK API
# ============================================================================
echo ""
echo "=== 2. Rolling back API ==="
if az containerapp show --name rmc-api --resource-group "$RG" &>/dev/null; then
  az containerapp update \
    --name rmc-api \
    --resource-group "$RG" \
    --image "$ACR_NAME.azurecr.io/rmc-api:$IMAGE_TAG"

  echo "✓ API rolled back"
else
  echo "ERROR: API container app not found"
  exit 1
fi

# Wait for API to stabilize
echo "Waiting for API to stabilize..."
sleep 10

# Get API URL for health check
API_FQDN=$(az containerapp show \
  --name rmc-api \
  --resource-group "$RG" \
  --query "properties.configuration.ingress.fqdn" -o tsv)

# ============================================================================
# 3. ROLLBACK FRONTEND
# ============================================================================
echo ""
echo "=== 3. Rolling back Frontend ==="
if az containerapp show --name rmc-frontend --resource-group "$RG" &>/dev/null; then
  az containerapp update \
    --name rmc-frontend \
    --resource-group "$RG" \
    --image "$ACR_NAME.azurecr.io/rmc-frontend:$IMAGE_TAG"

  echo "✓ Frontend rolled back"
else
  echo "ERROR: Frontend container app not found"
  exit 1
fi

# Get frontend URL
FRONTEND_FQDN=$(az containerapp show \
  --name rmc-frontend \
  --resource-group "$RG" \
  --query "properties.configuration.ingress.fqdn" -o tsv)

# ============================================================================
# 4. HEALTH CHECKS
# ============================================================================
echo ""
echo "=== 4. Running Health Checks ==="

# Wait for containers to stabilize
echo "Waiting for containers to stabilize..."
sleep 15

# Check API health
echo "Checking API health..."
API_HEALTH_URL="https://$API_FQDN/health"
MAX_RETRIES=6
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if curl -sf "$API_HEALTH_URL" > /dev/null 2>&1; then
    echo "✓ API health check passed"
    break
  else
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
      echo "⚠ API health check failed after $MAX_RETRIES attempts"
      echo "  Check manually: $API_HEALTH_URL"
      echo "  View logs: az containerapp logs show --name rmc-api --resource-group $RG --follow"
    else
      echo "  Attempt $RETRY_COUNT/$MAX_RETRIES failed, retrying in 10s..."
      sleep 10
    fi
  fi
done

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
echo "✓ Rollback Complete"
echo "=========================================="
echo ""
echo "Rolled back to: $IMAGE_TAG"
echo ""
echo "Previous deployment (for reference):"
echo "  API:      $CURRENT_API_IMAGE"
echo "  Frontend: $CURRENT_FRONTEND_IMAGE"
echo "  Celery:   $CURRENT_CELERY_IMAGE"
echo ""
echo "Current deployment:"
echo "  API:      $ACR_NAME.azurecr.io/rmc-api:$IMAGE_TAG"
echo "  Frontend: $ACR_NAME.azurecr.io/rmc-frontend:$IMAGE_TAG"
echo "  Celery:   $ACR_NAME.azurecr.io/rmc-api:$IMAGE_TAG"
echo ""
echo "Application URLs:"
echo "  API:      https://$API_FQDN"
echo "  Frontend: https://$FRONTEND_FQDN"
echo ""
echo "Next steps:"
echo "  - Test application: https://$FRONTEND_FQDN"
echo "  - Check API: curl https://$API_FQDN/health"
echo "  - View logs: az containerapp logs show --name rmc-api --resource-group $RG --follow"
echo ""
echo "To rollback this rollback, extract the image tag from the previous deployment above"
echo "and run: $0 <previous-image-tag>"
echo ""
echo "=========================================="
