# Task: Integrate PostgreSQL Service into Docker Compose

**Status:** Completed  
**Date:** 2026-09-11  
**Target:** `Dockerfile`, `docker-compose.yml`

## 1. Problem Statement
Default deployment runs on local SQLite. User requested combining PostgreSQL image directly into `docker-compose.yml` for unified setup and faster testing.

## 2. Requirements & Scope
1. Update `Dockerfile` to install optional PostgreSQL driver: `pip install --no-cache-dir ".[postgres]"`.
2. Update `docker-compose.yml`:
   - Add `postgres` service using `postgres:16-alpine`.
   - Setup healthcheck, environment credentials (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`).
   - Configure `lambda-erp` service to `depends_on: postgres: condition: service_healthy`.
   - Configure `LAMBDA_ERP_DB: postgresql://postgres:postgres@postgres:5432/lambda_erp`.
   - Add volume `postgres-data` for data persistence.

## 3. Verification Results
- `Dockerfile`: Added `".[postgres]"` with timeout/retry settings.
- `docker-compose.yml`: Added `postgres:16-alpine` service, healthcheck `pg_isready`, `postgres-data` volume, and linked `LAMBDA_ERP_DB`.
- Healthcheck verification: Both `lambda-erp-postgres` and `lambda-erp-lambda-erp-1` report status `(healthy)`.
- Backend verification: `GET http://localhost:8000/api/health` returned `{"status": "ok", "version": "0.8.33"}`.
- Data verification: Connected to PostgreSQL container; 67 relations created, simulation bootstrapped successfully (1 Company, 328 Sales Invoices).
