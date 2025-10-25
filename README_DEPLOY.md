# Production Deployment Guide - Hetzner + Cloudflare

This guide covers deploying the AIMS Readiness platform to production using Hetzner VPS and Cloudflare Pages.

## Architecture Overview

- **Backend**: Hetzner VPS (Docker + Traefik)
- **Frontend**: Cloudflare Pages
- **Storage**: MinIO on Hetzner
- **Database**: PostgreSQL on Hetzner
- **CDN**: Cloudflare (automatic with Pages)
- **SSL**: Let's Encrypt (via Traefik)

## Hetzner Setup

### 1. VPS Provisioning

**Recommended Configuration:**
- **Server Type**: CX21 (2 vCPU, 4GB RAM, 40GB SSD)
- **Location**: Nuremberg (DE) or Helsinki (FI)
- **OS**: Ubuntu 22.04 LTS
- **Cost**: €5.83/month

**Alternative Options:**
- **CX31**: 2 vCPU, 8GB RAM, 80GB SSD (€11.16/month)
- **CX41**: 4 vCPU, 16GB RAM, 160GB SSD (€22.32/month)

### 2. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt install git -y

# Logout and login to apply docker group changes
```

### 3. Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/aims-readiness.git
cd aims-readiness

# Create production environment file
cp .env.production.template .env.production
```

### 4. Configure Environment Variables

Edit `.env.production`:

```bash
# Security
SECRET_KEY=your-secret-key-32-chars-minimum
ORG_API_KEY=your-organization-api-key

# Database
DB_PASSWORD=your-secure-postgres-password

# Frontend
FRONTEND_ORIGIN=https://aims.yourdomain.com

# Storage (MinIO)
MINIO_ACCESS_KEY=your-minio-access-key
MINIO_SECRET_KEY=your-minio-secret-key-min-8-chars

# Domain
API_DOMAIN=api.aims.yourdomain.com
```

### 5. Generate Secure Keys

```bash
# Generate SECRET_KEY
openssl rand -base64 32

# Generate MinIO keys
openssl rand -base64 16  # Access key
openssl rand -base64 32  # Secret key

# Generate database password
openssl rand -base64 24
```

## Docker Compose Configuration

### 1. Production Docker Compose

Create `docker-compose.production.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/aims
      - SECRET_KEY=${SECRET_KEY}
      - ORG_API_KEY=${ORG_API_KEY}
      - FRONTEND_ORIGIN=${FRONTEND_ORIGIN}
      - MINIO_ENDPOINT=http://minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.aims-api.rule=Host(`api.aims.yourdomain.com`)"
      - "traefik.http.routers.aims-api.tls.certresolver=letsencrypt"
      - "traefik.http.routers.aims-api.tls=true"
    networks:
      - aims-network
    depends_on:
      - db
      - minio

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=aims
      - POSTGRES_USER=postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - aims-network
    restart: unless-stopped

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
    volumes:
      - minio-data:/data
    networks:
      - aims-network
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.minio.rule=Host(`minio.aims.yourdomain.com`)"
      - "traefik.http.routers.minio.tls.certresolver=letsencrypt"
      - "traefik.http.routers.minio.tls=true"

  traefik:
    image: traefik:v2.10
    command:
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@yourdomain.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik-certs:/letsencrypt
    networks:
      - aims-network
    restart: unless-stopped

volumes:
  postgres-data:
  minio-data:
  traefik-certs:

networks:
  aims-network:
    driver: bridge
```

### 2. Deploy Services

```bash
# Start services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

## Cloudflare Pages Setup

### 1. Connect GitHub Repository

1. Go to [Cloudflare Pages](https://pages.cloudflare.com/)
2. Click "Connect to Git"
3. Select your GitHub repository
4. Choose the repository containing the frontend

### 2. Build Configuration

**Build Settings:**
- **Framework preset**: Next.js
- **Build command**: `npm run build`
- **Build output directory**: `out`
- **Root directory**: `frontend`

### 3. Environment Variables

Add these environment variables in Cloudflare Pages:

```
NEXT_PUBLIC_API_URL=https://api.aims.yourdomain.com
NEXT_PUBLIC_APP_NAME=AIMS Readiness
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### 4. Custom Domain

1. Go to your domain settings in Cloudflare
2. Add a CNAME record:
   - **Name**: `aims`
   - **Target**: `your-pages-project.pages.dev`
   - **Proxy status**: Proxied (orange cloud)

## MinIO Bucket Setup

### 1. Create Buckets

```bash
# Access MinIO console
open https://minio.aims.yourdomain.com

# Login with your MinIO credentials
# Create buckets:
# - aims-evidence
# - aims-documents
# - aims-exports
```

### 2. Configure Bucket Policies

Set appropriate policies for each bucket:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::aims-evidence/*"
    }
  ]
}
```

## Domain Configuration

### 1. DNS Records

Configure these DNS records in Cloudflare:

```
# API endpoint
api.aims.yourdomain.com    A    YOUR_HETZNER_IP

# MinIO console
minio.aims.yourdomain.com  A    YOUR_HETZNER_IP

# Frontend (handled by Pages)
aims.yourdomain.com        CNAME your-pages-project.pages.dev
```

### 2. SSL Certificates

SSL certificates are automatically managed by:
- **Traefik** for backend services (Let's Encrypt)
- **Cloudflare** for frontend (automatic)

## Validation Commands

### 1. Health Checks

```bash
# Backend health
curl https://api.aims.yourdomain.com/health

# Expected response: {"status":"ok"}

# Backend readiness
curl https://api.aims.yourdomain.com/ready

# Expected response: {"status":"ready"}
```

### 2. API Tests

```bash
# Test API key authentication
curl -H "X-API-Key: your-api-key" https://api.aims.yourdomain.com/systems

# Test Annex IV export
curl -H "X-API-Key: your-api-key" https://api.aims.yourdomain.com/reports/annex-iv/1 -o test-export.zip
```

### 3. Frontend Tests

```bash
# Test frontend accessibility
curl https://aims.yourdomain.com

# Test API connectivity from frontend
curl https://aims.yourdomain.com/api/health
```

## Cost Breakdown

### Monthly Costs

- **Hetzner CX21**: €5.83
- **Cloudflare Pages**: Free (100GB/month)
- **Domain**: €10-15/year (€1-1.25/month)
- **Total**: ~€7-8/month

### Scaling Costs

- **CX31** (8GB RAM): €11.16/month
- **CX41** (16GB RAM): €22.32/month
- **Additional storage**: €0.04/GB/month

## Security Checklist

### 1. MinIO Security

- [ ] MinIO console accessible only via HTTPS
- [ ] Strong access keys (min 8 chars)
- [ ] Bucket policies configured
- [ ] No public read access to sensitive buckets

### 2. Database Security

- [ ] Strong PostgreSQL password
- [ ] Database not exposed to internet
- [ ] Regular backups configured
- [ ] Connection encryption enabled

### 3. Application Security

- [ ] SECRET_KEY is 32+ characters
- [ ] API keys are secure
- [ ] CORS properly configured
- [ ] Rate limiting enabled

### 4. Infrastructure Security

- [ ] Firewall configured (only ports 80, 443)
- [ ] SSH key authentication only
- [ ] Regular security updates
- [ ] Monitoring and logging enabled

## Monitoring and Maintenance

### 1. Log Monitoring

```bash
# View application logs
docker-compose -f docker-compose.production.yml logs -f backend

# View Traefik logs
docker-compose -f docker-compose.production.yml logs -f traefik
```

### 2. Backup Procedures

```bash
# Database backup
docker-compose -f docker-compose.production.yml exec db pg_dump -U postgres aims > backup_$(date +%Y%m%d).sql

# MinIO backup
docker-compose -f docker-compose.production.yml exec minio mc mirror /data s3://backup-bucket/
```

### 3. Updates

```bash
# Update application
git pull origin main
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d

# Update system
sudo apt update && sudo apt upgrade -y
```

## Troubleshooting

### Common Issues

1. **SSL Certificate Issues**
   - Check Traefik logs: `docker-compose logs traefik`
   - Verify DNS propagation
   - Check Let's Encrypt rate limits

2. **Database Connection Issues**
   - Verify database is running: `docker-compose ps`
   - Check connection string in environment
   - Verify network connectivity

3. **MinIO Access Issues**
   - Check MinIO console accessibility
   - Verify bucket policies
   - Check access key configuration

4. **Frontend API Connection Issues**
   - Verify `NEXT_PUBLIC_API_URL` environment variable
   - Check CORS configuration
   - Verify API endpoint accessibility

### Support

For deployment issues:
1. Check application logs
2. Verify environment configuration
3. Test individual components
4. Review security checklist
5. Contact support if needed

## Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_systems_org_id ON systems(org_id);
CREATE INDEX idx_evidence_system_id ON evidence(system_id);
CREATE INDEX idx_controls_system_id ON controls(system_id);
```

### 2. MinIO Optimization

```bash
# Configure MinIO for better performance
export MINIO_CACHE_DRIVES="/tmp/cache"
export MINIO_CACHE_EXCLUDE="*.pdf,*.zip"
```

### 3. Traefik Optimization

```yaml
# Add to traefik service
labels:
  - "traefik.http.middlewares.ratelimit.ratelimit.burst=100"
  - "traefik.http.middlewares.ratelimit.ratelimit.average=50"
```

This deployment guide provides a complete production setup for the AIMS Readiness platform using Hetzner and Cloudflare.