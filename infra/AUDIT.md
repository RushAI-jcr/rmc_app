# Azure Infrastructure and Compliance Audit

**Audit date:** 2026-02-13  
**Scope:** provision.sh, deploy.sh, rollback.sh, Makefile, .env.example, and docs (QUICKSTART.md, README.md, CICD-SETUP.md).  
**Standards:** Microsoft Azure deployment and security best practices.

---

## Executive summary

The infrastructure was audited for security, compliance, configuration, and operations. Two **must-fix** items were implemented: PostgreSQL firewall was restricted to Azure services only (no longer open to all IPv4), and Key Vault purge protection was enabled. Pre-flight checks in deploy.sh were extended to require ACR and Container Apps environment. Documentation was updated for secret rotation and Container Apps logging/alerts. Remaining items are documented as recommendations or verified as passed.

---

## 1. Security audit

| # | Check | Where | Result | Notes |
|---|--------|--------|--------|--------|
| 1.1 | PostgreSQL network exposure | provision.sh | **Fixed** | Changed `--public-access` from `0.0.0.0-255.255.255.255` to `0.0.0.0-0.0.0.0` (allow Azure services only). |
| 1.2 | Key Vault purge protection | provision.sh | **Fixed** | Added `--enable-purge-protection true` to Key Vault create. |
| 1.3 | Key Vault RBAC | provision.sh | **Recommend** | Access policies in use; document choice; consider RBAC for consistency. |
| 1.4 | ACR admin user | provision.sh | **Pass** | admin-enabled true; acceptable for small setups; document managed identity option for production. |
| 1.5 | Secrets in Key Vault | provision.sh | **Pass** | DB, JWT, Redis, storage in KV; DATABASE_URL contains password. Secret rotation documented in README. |
| 1.6 | TLS / HTTPS | provision.sh | **Pass** | Postgres require_secure_transport ON; Redis minimum-tls-version 1.2; Storage https-only, min-tls TLS1_2. |
| 1.7 | Blob public access | provision.sh | **Pass** | allow-blob-public-access false; container public-access off. |
| 1.8 | Container Apps identity | deploy.sh | **Pass** | Managed Identity; Key Vault via keyvaultref + identityref:system; no secrets in env. |

---

## 2. Compliance and Azure best practices

| # | Check | Result | Notes |
|---|--------|--------|--------|
| 2.1 | IaC format | **Note** | Bash scripts only; document as intentional; Bicep/Terraform optional for what-if/reproducibility. |
| 2.2 | Key Vault purge protection | **Fixed** | Enabled in provision.sh. |
| 2.3 | ACR anonymous pull | **Pass** | Not enabled. |
| 2.4 | Deployment validation | **Recommend** | No what-if in scripts; document running in dev first or add validation when moving to ARM. |
| 2.5 | Least privilege | **Pass** | Key Vault policy: get, list for Container Apps. |
| 2.6 | No hardcoded credentials | **Pass** | Secrets from openssl rand and Key Vault; none in repo. |
| 2.7 | Container Apps target port | **Pass** | API: Dockerfile uvicorn --port 8000, deploy target-port 8000. Frontend: Dockerfile EXPOSE 3000, deploy target-port 3000. |

---

## 3. Configuration and cost audit

| # | Check | Result | Notes |
|---|--------|--------|--------|
| 3.1 | Resource naming and tags | **Pass** | Naming consistent (RG, ACR, Postgres, Redis, Storage, KV, CA env). Add tags via `az group update --tags` if required by org. |
| 3.2 | Region and quota | **Pass** | LOCATION=centralus; document region choice; use quota tools if scaling. |
| 3.3 | Cost estimate vs. script | **Pass** | QUICKSTART.md and README.md match deploy.sh (0.75/1.5 Gi API, 0.5/1 Gi Celery and Frontend, min 1 max 2). |
| 3.4 | PostgreSQL backup retention | **Pass** | 35-day retention in provision.sh; restore procedure in README. |
| 3.5 | Storage lifecycle | **Pass** | Prefix `amcas-uploads/` matches api/settings.py and provision; lifecycle policy applied. |

---

## 4. Operational and runbook audit

| # | Check | Result | Notes |
|---|--------|--------|--------|
| 4.1 | Idempotency | **Pass** | provision.sh checks "already exists" for RG, ACR, Postgres, Redis, Storage, KV, CA env. |
| 4.2 | Deploy pre-flight | **Fixed** | deploy.sh now checks ACR and Container Apps environment in addition to RG and Key Vault. |
| 4.3 | Rollback | **Pass** | rollback.sh uses image tag; updates API, frontend, Celery; DB migrations are not auto-rolled back (document in runbook). |
| 4.4 | Health and readiness | **Pass** | Post-deploy curl to /health and frontend; default TCP probes on target port; optional HTTP probe via Portal. |
| 4.5 | Logging and monitoring | **Recommend** | README updated with one-line guidance for Container Apps logs and Azure Monitor alerts. |

---

## 5. Prioritized action list

### Implemented (must-fix)

- **1.1** PostgreSQL firewall restricted to Azure services (`0.0.0.0-0.0.0.0`).
- **2.2** Key Vault purge protection enabled in provision.sh.
- **4.2** ACR and Container Apps environment checks added to deploy.sh pre-flight.

### Implemented (recommend)

- **1.5** Secret rotation documented in README (Secrets and monitoring).
- **4.5** Container Apps logs and alerts documented in README.

### Open (recommend)

- 1.3 Document Key Vault RBAC vs access policy choice.
- 2.1 Document IaC approach; optionally add Bicep/Terraform later.
- 2.4 Document or add deployment validation step (e.g. run in dev first).

### Verified

- 2.7 API port 8000 and frontend port 3000 confirmed in Dockerfiles and deploy.sh.
- 4.3 Rollback behavior confirmed; migration rollback policy noted above.
- 3.5 Blob prefix `amcas-uploads/` matches usage.

---

## 6. References

- [infra/provision.sh](provision.sh) – Infrastructure provisioning
- [infra/deploy.sh](deploy.sh) – Application deployment and pre-flight checks
- [infra/rollback.sh](rollback.sh) – Rollback procedure
- [infra/README.md](README.md) – Cost, scaling, secrets and monitoring

---

## 7. Audit references (Context7 / Microsoft Learn)

This section cross-checks the audit against **Context7**-queried Microsoft Learn documentation to confirm alignment with official Azure guidance.

### Key Vault

- **Purge protection:** Microsoft Learn recommends creating Key Vault with `--enable-purge-protection true` (and soft delete) for data recovery and security. Our provision.sh now sets `--enable-purge-protection true` at create time.  
  Ref: [Key Vault recovery](https://learn.microsoft.com/en-us/azure/key-vault/general/key-vault-recovery), [Service Bus / Event Hubs configure-customer-managed-key](https://learn.microsoft.com/en-us/azure/service-bus-messaging/configure-customer-managed-key_tabs=Key-Vault).

### PostgreSQL Flexible Server firewall

- **Allow Azure services only:** Official docs show allowing “all Azure services” via firewall rule with `--start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0` (rule name e.g. `AllowAllAzureServices`). Our provision uses `--public-access 0.0.0.0-0.0.0.0` at server create, which achieves the same effect (no public internet; Azure services can connect).  
  Ref: [PostgreSQL firewall rule – allow Azure services](https://learn.microsoft.com/en-us/azure/developer/java/ee/how-to-configure-passwordless-datasource-websphere), [Deploy Python to Container Apps](https://learn.microsoft.com/en-us/azure/developer/python/tutorial-deploy-python-web-app-azure-container-apps-02).

### Container Apps – secrets and identity

- **Key Vault references:** Learn docs show using `keyvaultref:<KEY_VAULT_SECRET_URI>` with `identityref:<USER_ASSIGNED_IDENTITY_ID>` or system identity. Our deploy.sh uses `keyvaultref:$DATABASE_URL_REF,identityref:system` (and same pattern for other secrets), which matches the recommended pattern.  
  Ref: [Manage secrets in Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/manage-secrets).

### Container Apps – health probes

- **Probe types:** Learn documents Liveness, Readiness, and Startup probes (HTTP GET or TCP), with success = HTTP 200–399 or TCP connection. We rely on default TCP probes on the ingress target port; optional custom HTTP probe on `/health` (e.g. for API port 8000) can be added via Portal or YAML/ARM as in [Health probes in Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/health-probes).
