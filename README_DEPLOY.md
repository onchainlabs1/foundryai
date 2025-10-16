# AIMS Readiness - Deployment Guide

This guide covers deploying the AIMS Readiness application to production using Render (backend) and Vercel (frontend).

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Storage       │
│   (Vercel)      │◄──►│   (Render)      │◄──►│   (S3/R2)       │
│   Next.js 14    │    │   FastAPI       │    │   Evidence      │
│   Port: 3000    │    │   Port: 10000   │    │   Files         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- [ ] GitHub repository with AIMS Readiness code
- [ ] Render account (free tier available)
- [ ] Vercel account (free tier available)
- [ ] S3-compatible storage (AWS S3, Cloudflare R2, etc.)
- [ ] Domain name (optional, for custom domains)

## 🚀 Deployment Steps

### Step 1: Backend API (Render)

1. **Connect Repository:**
   ```bash
   # Push code to GitHub
   git add .
   git commit -m "feat: add deployment configuration"
   git push origin main
   ```

2. **Create Render Service:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the repository and branch

3. **Configure Service:**
   - **Name:** `aims-api`
   - **Environment:** `Python`
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 10000`

4. **Set Environment Variables:**
   ```bash
   # Required
   DATABASE_URL=postgresql://user:pass@host:5432/aims_db
   ORG_NAME=Your Organization Name
   ORG_API_KEY=your-secure-api-key-here
   FRONTEND_ORIGIN=https://your-frontend.vercel.app
   
   # Storage (S3/R2)
   S3_ENDPOINT=https://your-bucket.s3.amazonaws.com
   S3_BUCKET=your-bucket-name
   S3_ACCESS_KEY=your-access-key
   S3_SECRET_KEY=your-secret-key
   S3_REGION=us-east-1
   S3_FORCE_PATH_STYLE=true
   
   # Optional
   EVIDENCE_LOCAL_STORAGE=false
   RATE_LIMIT=60
   DEBUG=false
   LOG_LEVEL=INFO
   ```

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for build to complete (~5-10 minutes)
   - Note the service URL: `https://aims-api.onrender.com`

### Step 2: Frontend (Vercel)

1. **Connect Repository:**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project:**
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

3. **Set Environment Variables:**
   ```bash
   # Required
   NEXT_PUBLIC_API_URL=https://aims-api.onrender.com
   
   # Optional
   NEXT_PUBLIC_APP_URL=https://your-frontend.vercel.app
   ```

4. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete (~3-5 minutes)
   - Note the deployment URL: `https://your-project.vercel.app`

### Step 3: Storage Setup (S3/R2)

1. **Create S3 Bucket:**
   ```bash
   # AWS S3
   aws s3 mb s3://your-aims-bucket
   aws s3api put-bucket-cors --bucket your-aims-bucket --cors-configuration file://cors.json
   ```

2. **CORS Configuration (`cors.json`):**
   ```json
   {
     "CORSRules": [
       {
         "AllowedOrigins": ["https://your-frontend.vercel.app"],
         "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
         "AllowedHeaders": ["*"],
         "MaxAgeSeconds": 3000
       }
     ]
   }
   ```

3. **Create IAM User:**
   ```bash
   # Create user with S3 permissions
   aws iam create-user --user-name aims-storage-user
   aws iam attach-user-policy --user-name aims-storage-user --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
   ```

### Step 4: Database Setup

1. **PostgreSQL on Render:**
   - Go to Render Dashboard
   - Click "New" → "PostgreSQL"
   - Name: `aims-database`
   - Plan: `Starter` (free tier)
   - Note the connection string

2. **Update Backend Environment:**
   ```bash
   DATABASE_URL=postgresql://user:pass@host:5432/aims_db
   ```

3. **Run Migrations:**
   ```bash
   # Connect to Render service shell
   render ssh aims-api
   
   # Run migrations
   python -m alembic upgrade head
   ```

## 🔧 Configuration Files

### `render.yaml` (Backend)
```yaml
services:
  - type: web
    name: aims-api
    env: python
    rootDir: backend
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port 10000"
    plan: starter
    envVars:
      - key: DATABASE_URL
        sync: false
      # ... other variables
```

### `vercel.json` (Frontend)
```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/.next",
  "framework": "nextjs",
  "env": {
    "NEXT_PUBLIC_API_URL": "@next_public_api_url"
  }
}
```

## 🧪 Testing Deployment

### 1. Health Check
```bash
# Backend
curl https://aims-api.onrender.com/health

# Expected: {"status": "healthy"}
```

### 2. API Test
```bash
# Test with API key
curl -H "X-API-Key: your-api-key" \
     https://aims-api.onrender.com/reports/summary

# Expected: JSON response with organization data
```

### 3. Frontend Test
```bash
# Visit frontend URL
open https://your-project.vercel.app

# Check browser console for errors
# Verify API calls are working
```

## 🔄 Staging → Production

### 1. Staging Environment
```bash
# Create staging branch
git checkout -b staging
git push origin staging

# Deploy to staging URLs
# Backend: https://aims-api-staging.onrender.com
# Frontend: https://aims-staging.vercel.app
```

### 2. Production Deployment
```bash
# Merge staging to main
git checkout main
git merge staging
git push origin main

# Production URLs
# Backend: https://aims-api.onrender.com
# Frontend: https://aims.vercel.app
```

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures:**
   ```bash
   # Check logs in Render/Vercel dashboard
   # Verify all dependencies are in requirements.txt
   # Check Python/Node.js versions
   ```

2. **Database Connection:**
   ```bash
   # Verify DATABASE_URL format
   # Check database is running
   # Verify network access
   ```

3. **CORS Errors:**
   ```bash
   # Update FRONTEND_ORIGIN in backend
   # Check S3 CORS configuration
   # Verify domain names match
   ```

4. **Storage Issues:**
   ```bash
   # Verify S3 credentials
   # Check bucket permissions
   # Test file upload manually
   ```

### Debug Commands

```bash
# Check backend logs
render logs aims-api

# Check frontend logs
vercel logs your-project

# Test API endpoints
curl -v https://aims-api.onrender.com/health

# Test database connection
render ssh aims-api
python -c "from app.database import engine; print(engine.url)"
```

## 📊 Monitoring

### Render Monitoring
- **CPU/Memory:** Available in Render dashboard
- **Logs:** Real-time logs in service dashboard
- **Uptime:** Built-in uptime monitoring

### Vercel Monitoring
- **Analytics:** Available in Vercel dashboard
- **Performance:** Core Web Vitals tracking
- **Functions:** Serverless function monitoring

### Custom Monitoring
```bash
# Add health check endpoint
GET /health

# Add metrics endpoint
GET /metrics

# Add status page
GET /status
```

## 🔒 Security Checklist

- [ ] API keys are secure and rotated regularly
- [ ] Database credentials are encrypted
- [ ] S3 bucket has proper permissions
- [ ] CORS is configured correctly
- [ ] HTTPS is enforced
- [ ] Rate limiting is enabled
- [ ] Input validation is working
- [ ] File uploads are sanitized

## 💰 Cost Optimization

### Render (Backend)
- **Free Tier:** 750 hours/month
- **Starter Plan:** $7/month (always-on)
- **Database:** $7/month for PostgreSQL

### Vercel (Frontend)
- **Free Tier:** 100GB bandwidth/month
- **Pro Plan:** $20/month (unlimited)
- **Functions:** 100GB-hours/month free

### S3 Storage
- **Free Tier:** 5GB storage, 20,000 requests
- **Standard:** $0.023/GB/month
- **Requests:** $0.0004/1,000 requests

## 🎯 Next Steps

1. **Custom Domain:**
   - Add custom domain in Vercel
   - Configure DNS records
   - Update CORS settings

2. **SSL Certificates:**
   - Automatic with Vercel/Render
   - Force HTTPS redirects
   - Update security headers

3. **CDN Setup:**
   - Vercel Edge Network (automatic)
   - S3 CloudFront (optional)
   - Image optimization

4. **Backup Strategy:**
   - Database backups (Render automatic)
   - S3 versioning enabled
   - Code repository backups

## 📞 Support

- **Render Support:** [help.render.com](https://help.render.com)
- **Vercel Support:** [vercel.com/help](https://vercel.com/help)
- **AWS S3 Support:** [aws.amazon.com/support](https://aws.amazon.com/support)

---

**🎉 Congratulations!** Your AIMS Readiness application is now deployed and ready for production use.

For questions or issues, check the troubleshooting section above or contact the development team.
