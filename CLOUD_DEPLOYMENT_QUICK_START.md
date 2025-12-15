# ☁️ BELLY Cloud Deployment - Quick Start

## 🚀 Deploy in 3 Steps

### Step 1: Prepare Your Code
```bash
cd /home/thiru/belly
git add -A
git commit -m "Ready for cloud deployment"
git push origin main
```

### Step 2: Choose Your Platform & Deploy
```bash
# Interactive deployment helper
./deploy_cloud.sh

# OR if you prefer Railway (recommended):
./deploy_railway.sh
```

### Step 3: Make It Public
- Get your URL from the platform dashboard
- Configure a custom domain (optional)
- Share the URL with everyone!

---

## 🏆 Recommended: Railway (5 minutes)

**Why Railway?**
- ✅ Easiest setup
- ✅ Auto-deploys from GitHub
- ✅ Free tier ($5/month credits)
- ✅ No configuration files needed

**Deploy to Railway:**
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Add environment variables from `.env.production`
5. Railway auto-deploys!

**Your URL will be:** `https://your-project.up.railway.app`

---

## 📊 Quick Comparison

| Platform | Ease | Cost | Best For | Setup Time |
|----------|------|------|----------|-----------|
| **Railway** | ⭐⭐⭐⭐⭐ | $5-50/mo | Production | 5 min |
| Vercel | ⭐⭐⭐⭐ | Free-$20 | Frontend | 3 min |
| Google Cloud Run | ⭐⭐⭐ | Pay/request | Scalable | 15 min |
| AWS ECS | ⭐⭐ | Varies | Enterprise | 30 min |
| Docker VPS | ⭐⭐⭐ | $5-50/mo | Full control | 20 min |

---

## 📋 Complete Deployment Files

| File | Purpose |
|------|---------|
| `DEPLOYMENT_GUIDE.md` | 📖 Detailed guide for all platforms |
| `deploy_cloud.sh` | 🚀 Interactive deployment helper |
| `deploy_railway.sh` | 🚂 Automated Railway deployment |
| `Dockerfile` | 🐳 Docker image for containers |
| `docker-compose.prod.yml` | 🐳 Production multi-container setup |
| `.env.example` | 📝 Configuration template |

---

## 🔐 Pre-Deployment Checklist

- [ ] All code pushed to GitHub
- [ ] Credentials rotated (see `SECURITY.md`)
- [ ] Environment variables ready
- [ ] .env and .env.production in .gitignore ✅
- [ ] HTTPS enabled (automatic on Railway/Vercel)
- [ ] API tested locally: `curl http://localhost:8000/health`

---

## 🎯 What Gets Deployed

### Backend (FastAPI)
- ✅ 8 API endpoints
- ✅ Real-time price fetching
- ✅ Stats computation
- ✅ Predictions
- ✅ API documentation at `/docs`

### Frontend (Reflex)
- ✅ Dashboard UI
- ✅ Real-time data
- ✅ Refresh button
- ✅ Price charts

### Background Workers
- ✅ Kafka Producer (fetches prices)
- ✅ Kafka Consumer (stores to Redis + DB)
- ✅ Airflow DAGs (stats & predictions)

### Databases & Cache
- ✅ Supabase PostgreSQL
- ✅ Redis Upstash
- ✅ Airflow SQLite

---

## 🌍 After Deployment

### 1. Test Your API
```bash
# Health check
curl https://your-domain.com/health

# Get current price
curl https://your-domain.com/current-price

# Get predictions
curl https://your-domain.com/predict

# View API docs
https://your-domain.com/docs
```

### 2. Access Your Frontend
```
https://your-domain.com
```

### 3. Monitor Your App
- **Railway**: Dashboard → Logs
- **Vercel**: Dashboard → Deployments
- **Your VPS**: `docker logs belly-api`

### 4. Share With Everyone
Send them your URL:
```
🌐 BELLY - Beldex Price Monitor
📱 https://your-domain.com
📊 Real-time crypto tracking
```

---

## 💡 Cost Breakdown (Monthly)

### Minimum (Free Tier)
- Railway: $5 credit
- Supabase: Free tier
- Redis: Free tier (Upstash)
- **Total: Free (within limits)**

### Small Production ($50-100)
- Railway: $20-50
- Supabase Pro: $25
- Redis: $5-10
- Kafka: $20 (if needed)
- **Total: $70-105/month**

### Medium Production ($100-300)
- Railway: $50-100
- Supabase Pro: $25
- Redis Pro: $25
- Kafka Pro: $50
- Monitoring & backups: $25
- **Total: $175-225/month**

---

## 🆘 Troubleshooting

### App won't deploy
1. Check git is clean: `git status`
2. Check logs on platform dashboard
3. Verify environment variables are set
4. Check `.env.production` values

### Frontend not connecting to API
1. Verify `BACKEND_API_URL` is set correctly
2. Check CORS is enabled in `main.py`
3. Test API: `curl $BACKEND_API_URL/health`

### Streaming not working
1. Verify Kafka credentials
2. Check producer logs
3. Check consumer logs
4. Verify Redis connection

### Database errors
1. Check Supabase connection string
2. Verify API key has correct permissions
3. Check database is accessible from server

---

## 📞 Support Resources

| Issue | Resource |
|-------|----------|
| Railway issues | https://railway.app/support |
| Vercel issues | https://vercel.com/support |
| AWS issues | https://aws.amazon.com/support |
| Database issues | https://supabase.com/docs |
| Docker issues | https://docker.com/support |

---

## 🎓 Next Level: Auto Deployments

Enable auto-deployments on every git push:

**Railway** ✅ (automatic)
- Just push to GitHub, Railway deploys automatically

**Vercel** ✅ (automatic)
- Just push to GitHub, Vercel deploys automatically

**GitHub Actions** (for Docker deployments)
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy
        run: |
          # Your deployment commands here
          docker build -t belly-api:latest .
          docker push your-registry/belly-api:latest
```

---

## 🚀 You're Ready!

Everything is configured for cloud deployment:
- ✅ Dockerfile ready
- ✅ docker-compose ready
- ✅ Environment template ready
- ✅ Deployment guides ready
- ✅ Scripts ready

**Pick your platform and deploy in 5 minutes!**

```bash
# Start here:
./deploy_cloud.sh
```

---

## 📚 Additional Resources

- 📖 Full guide: `DEPLOYMENT_GUIDE.md`
- 🔐 Security: `SECURITY.md`
- ⚙️ Configuration: `.env.example`
- 🐳 Docker: `Dockerfile`, `docker-compose.prod.yml`
- 🚂 Railway: `deploy_railway.sh`

---

**Happy deploying! 🚀**

Questions? Check:
1. `DEPLOYMENT_GUIDE.md` - Complete guides
2. `.env.example` - Configuration
3. `SECURITY.md` - Credential management
4. Platform documentation links in this file
