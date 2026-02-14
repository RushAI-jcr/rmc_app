# RMC Triage - Infrastructure Management Makefile
# Run 'make help' to see all available commands

.PHONY: help provision deploy rollback logs clean dev-up dev-down dev-logs db-migrate

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ Azure Deployment

provision: ## Provision all Azure infrastructure (one-time setup)
	@echo "$(BLUE)Provisioning Azure infrastructure...$(NC)"
	@chmod +x provision.sh && ./provision.sh

deploy: ## Deploy application to Azure Container Apps
	@echo "$(BLUE)Deploying application...$(NC)"
	@chmod +x deploy.sh && ./deploy.sh

rollback: ## Rollback to previous deployment (run: make rollback TAG=a1b2c3d)
	@echo "$(BLUE)Rolling back deployment...$(NC)"
ifdef TAG
	@chmod +x rollback.sh && ./rollback.sh $(TAG)
else
	@chmod +x rollback.sh && ./rollback.sh
endif

##@ Local Development

dev-up: ## Start local development environment
	@echo "$(GREEN)Starting local development environment...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "API:      http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "PostgreSQL: localhost:5432"
	@echo "Redis:    localhost:6379"

dev-down: ## Stop local development environment
	@echo "$(YELLOW)Stopping local development environment...$(NC)"
	@docker-compose down

dev-logs: ## View logs from local development environment
	@docker-compose logs -f

dev-restart: ## Restart local development environment
	@echo "$(YELLOW)Restarting local development environment...$(NC)"
	@docker-compose restart

dev-rebuild: ## Rebuild and restart local development environment
	@echo "$(YELLOW)Rebuilding local development environment...$(NC)"
	@docker-compose up -d --build

##@ Database

db-migrate: ## Run database migrations locally
	@echo "$(BLUE)Running database migrations...$(NC)"
	@docker-compose exec api alembic upgrade head

db-shell: ## Open PostgreSQL shell locally
	@docker-compose exec postgres psql -U postgres -d rmc_triage

db-reset: ## Reset local database (WARNING: destroys all data)
	@echo "$(RED)WARNING: This will destroy all local database data!$(NC)"
	@read -p "Are you sure? [y/N]: " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose down -v; \
		docker-compose up -d postgres; \
		sleep 5; \
		docker-compose exec api alembic upgrade head; \
		echo "$(GREEN)✓ Database reset complete$(NC)"; \
	else \
		echo "$(YELLOW)Database reset cancelled$(NC)"; \
	fi

##@ Monitoring

logs-api: ## View API logs (Azure)
	@az containerapp logs show --name rmc-api --resource-group rmc-triage-rg --follow

logs-frontend: ## View frontend logs (Azure)
	@az containerapp logs show --name rmc-frontend --resource-group rmc-triage-rg --follow

logs-celery: ## View Celery worker logs (Azure)
	@az containerapp logs show --name rmc-celery-worker --resource-group rmc-triage-rg --follow

status: ## Show deployment status
	@echo "$(BLUE)Checking deployment status...$(NC)"
	@echo ""
	@echo "$(GREEN)Container Apps:$(NC)"
	@az containerapp list --resource-group rmc-triage-rg --output table 2>/dev/null || echo "Not deployed"
	@echo ""
	@echo "$(GREEN)Database:$(NC)"
	@az postgres flexible-server show --name rmc-triage-postgres --resource-group rmc-triage-rg --output table 2>/dev/null || echo "Not provisioned"
	@echo ""
	@echo "$(GREEN)Redis:$(NC)"
	@az redis show --name rmc-triage-redis --resource-group rmc-triage-rg --output table 2>/dev/null || echo "Not provisioned"

health: ## Check application health
	@echo "$(BLUE)Checking application health...$(NC)"
	@API_URL=$$(az containerapp show --name rmc-api --resource-group rmc-triage-rg --query "properties.configuration.ingress.fqdn" -o tsv 2>/dev/null); \
	if [ -n "$$API_URL" ]; then \
		echo "API: https://$$API_URL"; \
		curl -sf https://$$API_URL/health && echo "$(GREEN)✓ API healthy$(NC)" || echo "$(RED)✗ API unhealthy$(NC)"; \
	else \
		echo "$(YELLOW)API not deployed$(NC)"; \
	fi
	@echo ""
	@FRONTEND_URL=$$(az containerapp show --name rmc-frontend --resource-group rmc-triage-rg --query "properties.configuration.ingress.fqdn" -o tsv 2>/dev/null); \
	if [ -n "$$FRONTEND_URL" ]; then \
		echo "Frontend: https://$$FRONTEND_URL"; \
		curl -sf https://$$FRONTEND_URL && echo "$(GREEN)✓ Frontend accessible$(NC)" || echo "$(RED)✗ Frontend inaccessible$(NC)"; \
	else \
		echo "$(YELLOW)Frontend not deployed$(NC)"; \
	fi

urls: ## Show application URLs
	@echo "$(BLUE)Application URLs:$(NC)"
	@API_URL=$$(az containerapp show --name rmc-api --resource-group rmc-triage-rg --query "properties.configuration.ingress.fqdn" -o tsv 2>/dev/null); \
	if [ -n "$$API_URL" ]; then echo "API:      https://$$API_URL"; fi
	@FRONTEND_URL=$$(az containerapp show --name rmc-frontend --resource-group rmc-triage-rg --query "properties.configuration.ingress.fqdn" -o tsv 2>/dev/null); \
	if [ -n "$$FRONTEND_URL" ]; then echo "Frontend: https://$$FRONTEND_URL"; fi

##@ Secrets

secrets-list: ## List all secrets in Key Vault
	@az keyvault secret list --vault-name rmc-triage-kv --output table

secrets-show: ## Show a specific secret (run: make secrets-show SECRET=DATABASE-URL)
ifdef SECRET
	@az keyvault secret show --vault-name rmc-triage-kv --name $(SECRET) --query value -o tsv
else
	@echo "$(RED)ERROR: Please specify SECRET name$(NC)"
	@echo "Example: make secrets-show SECRET=DATABASE-URL"
endif

secrets-update: ## Update a secret (run: make secrets-update SECRET=JWT-SECRET VALUE=newsecret)
ifdef SECRET
ifdef VALUE
	@az keyvault secret set --vault-name rmc-triage-kv --name $(SECRET) --value "$(VALUE)"
	@echo "$(GREEN)✓ Secret updated. Restart containers to apply changes.$(NC)"
else
	@echo "$(RED)ERROR: Please specify VALUE$(NC)"
	@echo "Example: make secrets-update SECRET=JWT-SECRET VALUE=newsecret"
endif
else
	@echo "$(RED)ERROR: Please specify SECRET and VALUE$(NC)"
	@echo "Example: make secrets-update SECRET=JWT-SECRET VALUE=newsecret"
endif

##@ Scaling

scale-api: ## Scale API (run: make scale-api MIN=1 MAX=2)
ifdef MIN
ifdef MAX
	@echo "$(BLUE)Scaling API to $(MIN)-$(MAX) replicas...$(NC)"
	@az containerapp update --name rmc-api --resource-group rmc-triage-rg --min-replicas $(MIN) --max-replicas $(MAX)
	@echo "$(GREEN)✓ API scaled$(NC)"
else
	@echo "$(RED)ERROR: Please specify MIN and MAX$(NC)"
	@echo "Example: make scale-api MIN=1 MAX=2"
endif
else
	@echo "$(RED)ERROR: Please specify MIN and MAX$(NC)"
	@echo "Example: make scale-api MIN=1 MAX=2"
endif

scale-celery: ## Scale Celery workers (run: make scale-celery MIN=1 MAX=2)
ifdef MIN
ifdef MAX
	@echo "$(BLUE)Scaling Celery to $(MIN)-$(MAX) replicas...$(NC)"
	@az containerapp update --name rmc-celery-worker --resource-group rmc-triage-rg --min-replicas $(MIN) --max-replicas $(MAX)
	@echo "$(GREEN)✓ Celery scaled$(NC)"
else
	@echo "$(RED)ERROR: Please specify MIN and MAX$(NC)"
	@echo "Example: make scale-celery MIN=1 MAX=2"
endif
else
	@echo "$(RED)ERROR: Please specify MIN and MAX$(NC)"
	@echo "Example: make scale-celery MIN=1 MAX=2"
endif

##@ Cleanup

clean: ## Remove all Azure resources (WARNING: destructive)
	@echo "$(RED)WARNING: This will delete ALL Azure resources!$(NC)"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		az group delete --name rmc-triage-rg --yes --no-wait; \
		echo "$(YELLOW)Resource group deletion started (running in background)$(NC)"; \
	else \
		echo "$(GREEN)Cleanup cancelled$(NC)"; \
	fi

clean-local: ## Remove all local Docker volumes and containers
	@echo "$(YELLOW)Removing local Docker resources...$(NC)"
	@docker-compose down -v
	@echo "$(GREEN)✓ Local resources cleaned$(NC)"

##@ Utility

env-setup: ## Create .env file from template
	@if [ -f .env ]; then \
		echo "$(YELLOW).env file already exists$(NC)"; \
		read -p "Overwrite? [y/N]: " confirm; \
		if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
			echo "$(GREEN)Keeping existing .env$(NC)"; \
			exit 0; \
		fi; \
	fi
	@cp .env.example .env
	@echo "$(GREEN)✓ Created .env file$(NC)"
	@echo "$(YELLOW)Remember to update values in .env$(NC)"

check-tools: ## Check if required tools are installed
	@echo "$(BLUE)Checking required tools...$(NC)"
	@command -v az >/dev/null 2>&1 && echo "$(GREEN)✓ Azure CLI$(NC)" || echo "$(RED)✗ Azure CLI not installed$(NC)"
	@command -v docker >/dev/null 2>&1 && echo "$(GREEN)✓ Docker$(NC)" || echo "$(RED)✗ Docker not installed$(NC)"
	@command -v docker-compose >/dev/null 2>&1 && echo "$(GREEN)✓ Docker Compose$(NC)" || echo "$(RED)✗ Docker Compose not installed$(NC)"
	@command -v git >/dev/null 2>&1 && echo "$(GREEN)✓ Git$(NC)" || echo "$(RED)✗ Git not installed$(NC)"
	@command -v curl >/dev/null 2>&1 && echo "$(GREEN)✓ curl$(NC)" || echo "$(RED)✗ curl not installed$(NC)"
	@command -v jq >/dev/null 2>&1 && echo "$(GREEN)✓ jq$(NC)" || echo "$(YELLOW)○ jq not installed (optional)$(NC)"

help: ## Display this help message
	@echo "$(BLUE)RMC Triage Infrastructure Management$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-18s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""
	@echo "Examples:"
	@echo "  make provision              # Create Azure infrastructure"
	@echo "  make deploy                 # Deploy application"
	@echo "  make rollback TAG=a1b2c3d   # Rollback to specific version"
	@echo "  make dev-up                 # Start local development"
	@echo "  make logs-api               # View API logs"
	@echo "  make scale-api MIN=2 MAX=10 # Scale API"
	@echo ""
