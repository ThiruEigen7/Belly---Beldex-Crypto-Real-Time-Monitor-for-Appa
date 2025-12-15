# 🚀 BELLY - Cloud Deployment Guide

Deploy BELLY to production and make it available for everyone!

## ☁️ Recommended Cloud Platforms

### Option 1: **Railway (RECOMMENDED - Easiest)**
Best for: Fast deployment, minimal configuration

**Pros:**
- Auto-deploys from GitHub
- Free tier available
- Environment variables via dashboard
- Built-in databases

**Steps:**
1. Push code to GitHub (already done ✅)
2. Go to https://railway.app
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Add environment variables:
   - SUPABASE_URL
   - SUPABASE_ANON_KEY
   - REDIS_URL
   - REDIS_TOKEN
   - KAFKA_BROKERS, KAFKA_USERNAME, KAFKA_PASSWORD
6. Railway auto-deploys on every push

---

### Option 2: **Render**
Best for: Production workloads, good scaling

**Steps:**
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python -m uvicorn belly.zebra.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in dashboard
6. Deploy

---

### Option 3: **Vercel (for Reflex Frontend)**
Best for: Frontend UI hosting

**Steps:**
1. Go to https://vercel.com
2. Import project from GitHub
3. Deploy automatically

---

### Option 4: **Docker + AWS/GCP/Azure**
Best for: Maximum control, complex setups

**Docker Deployment:**
```bash
# Build image
docker build -f belly/airflow/Dockerfile.airflow.nodumb -t belly-api:latest .

# Push to registry
docker push your-registry/belly-api:latest

# Deploy on AWS ECS, GCP Cloud Run, Azure Container Instances
```

---

## 📋 Step-by-Step: Railway Deployment

### 1. **Prepare Your Code**
```bash
cd /home/thiru/belly

# Ensure all changes are committed
git add -A
git commit -m "final: Ready for production deployment"
git push origin main
```

### 2. **Create Railway Account**
- Visit https://railway.app
- Sign up with GitHub (recommended)
- Authorize Railway to access your repositories

### 3. **Create New Project**
```
Dashboard → New Project → Deploy from GitHub
```

### 4. **Configure Project**
- Select repository: `Belly---Beldex-Crypto-Real-Time-Monitor-for-Appa`
- Choose branch: `main`
- Railway auto-detects Python project

### 5. **Set Environment Variables**

In Railway Dashboard → Variables:

```env
# Supabase
SUPABASE_URL=https://bcioieesyhilfrfgogpq.supabase.co
SUPABASE_ANON_KEY=your_key_here

# Redis
REDIS_URL=https://settling-locust-8886.upstash.io
REDIS_TOKEN=your_token_here

# Kafka
KAFKA_BROKERS=d4qn7d0e5lrisl4hsue0.any.us-central1.gc.prd.cloud.redpanda.com:9092
KAFKA_TOPIC=belly-price
KAFKA_CONSUMER_GROUP=belly-consumers
KAFKA_USERNAME=crypto
KAFKA_PASSWORD=your_password_here

# Airflow
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=strong_password_here
AIRFLOW_EMAIL=admin@belly.cloud
AIRFLOW_SQL_ALCHEMY_CONN=sqlite:////app/airflow.db

# App Config
APP_ENV=production
LOG_LEVEL=INFO
TZ=UTC
BACKEND_API_URL=https://your-railway-domain.up.railway.app
REFLEX_HOST=0.0.0.0
REFLEX_PORT=3000
```

### 6. **Configure Services**

Create `railway.toml` in project root:

```toml
[build]
builder = "dockerfile"
dockerfile = "./Dockerfile"

[deploy]
startCommand = "python -m uvicorn belly.zebra.main:app --host 0.0.0.0 --port $PORT"
```

### 7. **Deploy**
- Railway automatically deploys when you push to GitHub
- Monitor deployment in Railway Dashboard
- Your app will be available at: `https://your-project.up.railway.app`

---

## 🐳 Docker Deployment (Advanced)

### Build Docker Image

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create airflow directory
RUN mkdir -p /app/belly/airflow/logs

# Expose ports
EXPOSE 8000 3000 8080

# Start API server
CMD ["python", "-m", "uvicorn", "belly.zebra.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build & Deploy

```bash
# Build
docker build -t belly-api:latest .

# Test locally
docker run -p 8000:8000 \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_ANON_KEY=your_key \
  belly-api:latest

# Push to registry
docker tag belly-api:latest your-registry/belly-api:latest
docker push your-registry/belly-api:latest

# Deploy to AWS ECS
aws ecs create-service \
  --cluster production \
  --service-name belly-api \
  --task-definition belly-api \
  --desired-count 1
```

---

## 🌍 Make It Available For Everyone

### 1. **Get a Custom Domain**
- Buy domain from GoDaddy, Namecheap, or Google Domains
- Point DNS to your Railway/Vercel deployment
- Railway shows instructions in dashboard

### 2. **Enable HTTPS**
- Railway provides free SSL certificate automatically
- Vercel includes free HTTPS

### 3. **Set Up Monitoring**
```bash
# Monitor logs
railway logs

# Monitor health
curl https://your-domain.com/health
```

### 4. **Share Your App**
```
Frontend: https://your-domain.com
API Docs: https://your-domain.com/docs
API: https://your-domain.com/api
```

---

## 📊 Multi-Container Deployment

For production, deploy each component separately:

### Docker Compose for Production

```yaml
version: '3.8'

services:
  api:
    image: your-registry/belly-api:latest
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    restart: always

  frontend:
    image: your-registry/belly-frontend:latest
    ports:
      - "3000:3000"
    environment:
      - BACKEND_API_URL=http://api:8000
    restart: always

  producer:
    image: your-registry/belly-producer:latest
    environment:
      - KAFKA_BROKERS=${KAFKA_BROKERS}
      - KAFKA_USERNAME=${KAFKA_USERNAME}
      - KAFKA_PASSWORD=${KAFKA_PASSWORD}
    restart: always

  consumer:
    image: your-registry/belly-consumer:latest
    environment:
      - KAFKA_BROKERS=${KAFKA_BROKERS}
      - REDIS_URL=${REDIS_URL}
      - SUPABASE_URL=${SUPABASE_URL}
    restart: always

  airflow-scheduler:
    image: your-registry/belly-airflow:latest
    command: airflow scheduler
    environment:
      - AIRFLOW_SQL_ALCHEMY_CONN=${AIRFLOW_SQL_ALCHEMY_CONN}
    restart: always

  airflow-webserver:
    image: your-registry/belly-airflow:latest
    command: airflow webserver
    ports:
      - "8080:8080"
    environment:
      - AIRFLOW_SQL_ALCHEMY_CONN=${AIRFLOW_SQL_ALCHEMY_CONN}
    restart: always
```

Deploy with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔒 Security Checklist

Before going public:

- [ ] Rotate all credentials (see SECURITY.md)
- [ ] Enable HTTPS (automatic on Railway/Vercel)
- [ ] Set strong Airflow password
- [ ] Enable API rate limiting
- [ ] Set up log monitoring
- [ ] Enable backup for Supabase
- [ ] Monitor Redis usage
- [ ] Set up alerting

---

## 💰 Cost Estimation

### Railway (Recommended)
- **Free Tier**: $5/month credits (sufficient for low traffic)
- **Pro Tier**: Pay as you go (~$0.02 per hour)
- **Estimate**: $10-50/month for small app

### Vercel (Frontend)
- **Free**: Unlimited deployments
- **Pro**: $20/month

### Supabase (Database)
- **Free**: 500MB storage, 2GB bandwidth
- **Pro**: $25/month (100GB storage)

### Redis Upstash
- **Free**: 10,000 commands/day
- **Pro**: $25/month (1M commands/day)

### Redpanda Cloud (Kafka)
- **Free**: 1 cluster, limited throughput
- **Pro**: $20-100/month

**Total Estimated Cost**: $50-200/month for production

---

## 🚀 Quick Start: Deploy to Railway in 5 Minutes

```bash
# 1. Ensure code is pushed
git push origin main

# 2. Go to railway.app → New Project → Deploy from GitHub

# 3. Select your repository

# 4. Add environment variables from .env.production

# 5. Railway auto-deploys!

# 6. Get your URL from Railway Dashboard
# Example: https://belly-production.up.railway.app
```

---

## ✅ Verify Deployment

After deployment, test these endpoints:

```bash
# Health check
curl https://your-domain.com/health

# API docs
curl https://your-domain.com/docs

# Current price
curl https://your-domain.com/current-price

# Stats
curl "https://your-domain.com/stats?period=7d"

# Predictions
curl https://your-domain.com/predict
```

---

## 📞 Support

For deployment issues:
- Railway Support: https://railway.app/support
- Vercel Support: https://vercel.com/support
- Supabase Docs: https://supabase.com/docs

---

## 🎯 Next Steps

1. **Deploy API**: Follow Railway steps above
2. **Deploy Frontend**: Push to Vercel or Railway
3. **Set up Domain**: Configure DNS for custom domain
4. **Monitor**: Set up logs and alerts
5. **Share**: Give everyone the URL!

Happy deploying! 🚀
