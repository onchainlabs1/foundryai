# AIMS Readiness - Staging Deployment Guide

## Overview

This guide walks you through deploying AIMS Readiness to a production-like staging environment with:

- **PostgreSQL** database
- **Cloudflare R2** (S3-compatible) for evidence storage
- **Traefik** reverse proxy with automatic HTTPS
- **Security hardening** (CORS, CSP, rate limiting)
- **Health probes** for Kubernetes/Docker

## Prerequisites

- Docker & Docker Compose
- Domain with DNS configured
- Cloudflare R2 account (or any S3-compatible storage)
- SSL certificates (automatic via Let's Encrypt)

## Quick Start (7 Steps)

### 1. Clone and Configure

```bash
cd /Users/fabio/Desktop/foundry
cp env.staging.example .env.staging
```

### 2. Edit `.env.staging`

```bash
# Required changes:
DATABASE_URL=postgresql+psycopg://aims:STRONG_PASSWORD@db:5432/aims
SECRET_KEY=GENERATE_32_CHAR_SECRET
FRONTEND_ORIGIN=https://app.yourdomain.com
ORG_API_KEY=GENERATE_UNIQUE_KEY

# R2 Configuration
S3_ENDPOINT=https://ACCOUNT_ID.r2.cloudflarestorage.com
S3_BUCKET=aims-evidence
S3_ACCESS_KEY=YOUR_R2_ACCESS_KEY
S3_SECRET_KEY=YOUR_R2_SECRET_KEY
```

### 3. Generate Secrets

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ORG_API_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

### 4. Configure Cloudflare R2

1. Go to R2 dashboard: https://dash.cloudflare.com/?to=/:account/r2
2. Create bucket: `aims-evidence`
3. Generate API token with R2 Read & Write permissions
4. Note Account ID from bucket URL

### 5. Update DNS

Point your domain to the server:

```
api.yourdomain.com  → A    → SERVER_IP
app.yourdomain.com  → A    → SERVER_IP
```

### 6. Deploy

```bash
# Pull latest images
docker-compose -f docker-compose.staging.yml pull

# Start services
docker-compose -f docker-compose.staging.yml up -d

# Check logs
docker-compose -f docker-compose.staging.yml logs -f api
```

### 7. Verify Deployment

```bash
# Health check
curl https://api.yourdomain.com/health
# Expected: {"status":"ok"}

# Readiness probe
curl https://api.yourdomain.com/ready
# Expected: {"status":"ready","checks":{"database":true,"s3":true}}

# Test API
curl -H "X-API-Key: YOUR_ORG_API_KEY" https://api.yourdomain.com/systems
# Expected: []
```

## Architecture

```
┌─────────────┐
│   Traefik   │  ← HTTPS (443), HTTP→HTTPS redirect
│ (Let's Enc) │
└──────┬──────┘
       │
   ┌───┴────┐
   │  API   │  ← FastAPI + uvicorn
   │ (8000) │
   └───┬────┘
       │
   ┌───┴────┐
   │   DB   │  ← PostgreSQL 16
   │ (5432) │
   └────────┘

External:
   Cloudflare R2  ← Evidence files (S3)
```

## Security Features

### 1. CORS Restriction

Only `FRONTEND_ORIGIN` can make requests:

```python
# app/main.py
allow_origins=[settings.FRONTEND_ORIGIN]
```

### 2. Security Headers

All responses include:

- `Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`

### 3. Authentication

- Missing API key → `401 Unauthorized` with `WWW-Authenticate: API-Key` header
- Invalid API key → `403 Forbidden`
- Valid API key → `200 OK`

### 4. Rate Limiting

Expensive endpoints limited to 60 requests/minute per API key:

- `POST /evidence/*`
- `GET /reports/deck.pptx`
- `GET /reports/annex-iv.zip`

Exceeding limit returns `429 Too Many Requests` with `Retry-After` header.

### 5. Database Isolation

- All queries scoped by `org_id`
- No cross-organization data leakage
- SQL injection protected by SQLAlchemy ORM

## Health Checks

### `/health` - Liveness Probe

Simple static check:

```bash
curl https://api.yourdomain.com/health
# {"status":"ok"}
```

Use for:

- Kubernetes liveness probe
- Load balancer health check
- Uptime monitoring

### `/ready` - Readiness Probe

Comprehensive connectivity check:

```bash
curl https://api.yourdomain.com/ready
# {
#   "status": "ready",
#   "checks": {
#     "database": true,
#     "s3": true
#   }
# }
```

Returns `503 Service Unavailable` if:

- Database connection fails
- S3/R2 bucket not accessible

Use for:

- Kubernetes readiness probe
- Pre-deployment validation
- CI/CD health gates

## S3/R2 Evidence Storage

### Upload Flow

1. Client computes SHA-256 checksum of file
2. Client calls `POST /evidence/{system_id}` with metadata
3. Server generates presigned URL (1-hour expiry)
4. Client uploads directly to R2 via presigned URL
5. R2 validates checksum server-side

### Benefits

- No file passes through API server
- Server-side checksum validation
- Reduced API bandwidth
- Better scalability

### Local Development Fallback

Set `EVIDENCE_LOCAL_STORAGE=true` to use local filesystem:

```bash
# .env.local
EVIDENCE_LOCAL_STORAGE=true
S3_ENDPOINT=  # Leave empty
```

Files stored in `./evidence/org_{id}/system_{id}/`

## Monitoring

### Logs

```bash
# API logs
docker-compose -f docker-compose.staging.yml logs -f api

# Database logs
docker-compose -f docker-compose.staging.yml logs -f db

# Traefik logs
docker-compose -f docker-compose.staging.yml logs -f traefik
```

### Metrics

Health endpoints suitable for:

- **Prometheus** scraping
- **Datadog** synthetic monitors
- **UptimeRobot** / **Pingdom**

Example Prometheus scrape config:

```yaml
scrape_configs:
  - job_name: 'aims-api'
    metrics_path: '/ready'
    static_configs:
      - targets: ['api.yourdomain.com:443']
        labels:
          env: 'staging'
```

## Backup & Recovery

### Database Backups

```bash
# Backup
docker-compose -f docker-compose.staging.yml exec db \
  pg_dump -U aims aims > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20240115.sql | docker-compose -f docker-compose.staging.yml exec -T db \
  psql -U aims aims
```

### R2 Evidence Backups

Cloudflare R2 provides:

- 11 nines durability
- Optional lifecycle policies
- R2 Replication (cross-region)

No manual backup needed.

## Troubleshooting

### API Won't Start

```bash
# Check logs
docker-compose -f docker-compose.staging.yml logs api

# Common issues:
# 1. DB not ready → Wait 10s for healthcheck
# 2. Wrong DATABASE_URL → Check .env.staging
# 3. Missing SECRET_KEY → Generate new one
```

### Database Connection Failed

```bash
# Test DB directly
docker-compose -f docker-compose.staging.yml exec db \
  psql -U aims aims -c "SELECT 1"

# Check password
grep DATABASE_URL .env.staging
```

### S3/R2 Not Working

```bash
# Test S3 connectivity
curl -H "X-API-Key: YOUR_KEY" https://api.yourdomain.com/ready

# Check response:
# "s3": false  → R2 credentials wrong
# "s3": true   → Working
```

### HTTPS Not Working

```bash
# Check Traefik dashboard
docker-compose -f docker-compose.staging.yml logs traefik

# Verify DNS
dig api.yourdomain.com +short
# Should return SERVER_IP

# Check Let's Encrypt rate limits
# https://letsencrypt.org/docs/rate-limits/
```

## Scaling

### Horizontal Scaling

Add more API containers:

```yaml
# docker-compose.staging.yml
api:
  deploy:
    replicas: 3  # Scale to 3 instances
```

Traefik automatically load balances.

### Database Scaling

For production, consider:

- **Amazon RDS for PostgreSQL**
- **Google Cloud SQL**
- **Azure Database for PostgreSQL**

Update `DATABASE_URL` accordingly.

### R2 Scaling

Cloudflare R2 auto-scales:

- No capacity limits
- Global distribution
- Zero egress fees

## Cost Estimate (Monthly)

- **DigitalOcean Droplet** (2 vCPU, 4GB RAM): $24/mo
- **Cloudflare R2** (100GB storage + uploads): ~$1.50/mo
- **Domain** (yourdomain.com): ~$12/year
- **Total**: ~$26/month

## Next Steps

1. Set up frontend (Next.js) deployment
2. Configure monitoring (Datadog/Sentry)
3. Add backup automation
4. Set up staging→production promotion workflow
5. Configure CI/CD pipeline

## Support

- **Documentation**: `/docs/ARCHITECTURE.md`
- **API Docs**: `https://api.yourdomain.com/docs`
- **GitHub Issues**: `https://github.com/yourorg/aims-readiness/issues`

---

**Deployed successfully?** ✅

Test the full flow:

```bash
# 1. Create system
curl -X POST https://api.yourdomain.com/systems \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test System","purpose":"Testing"}'

# 2. Run assessment
curl -X POST https://api.yourdomain.com/systems/1/assess \
  -H "X-API-Key: YOUR_KEY"

# 3. Get compliance score
curl https://api.yourdomain.com/reports/score \
  -H "X-API-Key: YOUR_KEY"
```

**You're production-ready!** 🚀

