# ☁️ Cloud Deployment Environment Variables

This file shows exactly what environment variables to set in your cloud platform dashboard.

## 🚂 Railway Dashboard → Variables

Copy and paste each variable in Railway's dashboard:

```
# ==========================================
# Supabase (Database & API)
# ==========================================
SUPABASE_URL=https://bcioieesyhilfrfgogpq.supabase.co
SUPABASE_ANON_KEY=your_actual_anon_key_here

# ==========================================
# Redis Upstash (Cache)
# ==========================================
REDIS_URL=https://settling-locust-8886.upstash.io
REDIS_TOKEN=your_actual_token_here

# ==========================================
# Kafka / Redpanda (Streaming)
# ==========================================
KAFKA_BROKERS=d4qn7d0e5lrisl4hsue0.any.us-central1.gc.prd.cloud.redpanda.com:9092
KAFKA_TOPIC=belly-price
KAFKA_CONSUMER_GROUP=belly-consumers
KAFKA_USERNAME=crypto
KAFKA_PASSWORD=your_actual_password_here

# ==========================================
# Airflow (DAG Orchestration)
# ==========================================
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=strong_secure_password_here
AIRFLOW_EMAIL=admin@belly.cloud
AIRFLOW_SQL_ALCHEMY_CONN=sqlite:////app/airflow/airflow.db

# ==========================================
# Application Settings
# ==========================================
APP_ENV=production
LOG_LEVEL=INFO
TZ=UTC
PYTHONUNBUFFERED=1

# ==========================================
# API Configuration
# ==========================================
BACKEND_API_URL=https://your-domain.com
API_PORT=8000

# ==========================================
# Frontend Configuration
# ==========================================
REFLEX_HOST=0.0.0.0
REFLEX_PORT=3000
REFLEX_SKIP_COMPILE=False
```

---

## 📝 How to Set Variables in Each Platform

### 🚂 Railway
1. Go to https://railway.app/dashboard
2. Select your project
3. Click "Variables" tab
4. Click "New Variable"
5. Paste each KEY=VALUE pair
6. Changes deploy automatically

### 🎨 Vercel
1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add each variable
5. Select which environments (Production, Preview, Development)
6. Redeploy

### 🌩️ Google Cloud Run
1. Go to https://console.cloud.google.com/run
2. Click your service
3. Click "Edit & Deploy New Revision"
4. Expand "Runtime settings"
5. Add environment variables
6. Deploy

### 🔵 Azure Container Instances
```bash
az container create --resource-group belly-rg \
  --name belly-api \
  --environment-variables SUPABASE_URL=xxx REDIS_URL=yyy
```

### 🐳 Docker / VPS
Create `.env.production` in project root:
```bash
cat > .env.production << EOF
SUPABASE_URL=https://bcioieesyhilfrfgogpq.supabase.co
SUPABASE_ANON_KEY=xxx
# ... (paste all variables above)
EOF
```

---

## 🔑 Where to Find Each Value

### Supabase
1. Go to https://supabase.com/dashboard
2. Select your project
3. Settings → API
4. Copy Project URL (SUPABASE_URL)
5. Copy Anon Public Key (SUPABASE_ANON_KEY)

### Redis Upstash
1. Go to https://console.upstash.com
2. Select your Redis database
3. Copy REST URL (REDIS_URL)
4. Copy TOKEN (REDIS_TOKEN)

### Redpanda / Kafka
1. Go to https://cloud.redpanda.com (or your Kafka provider)
2. Copy Brokers
3. Copy Username & Password
4. Copy Topic Name

### Airflow
- Choose your own AIRFLOW_USERNAME & AIRFLOW_PASSWORD
- Use strong passwords (min 12 chars, mix of upper/lower/numbers)

---

## 🎯 Copy-Paste Template

Ready to deploy? Here's the template with placeholders:

```bash
# === SUPABASE ===
SUPABASE_URL=https://bcioieesyhilfrfgogpq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# === REDIS ===
REDIS_URL=https://settling-locust-8886.upstash.io
REDIS_TOKEN=ABEa...

# === KAFKA ===
KAFKA_BROKERS=d4qn7d0e5lrisl4hsue0.any.us-central1.gc.prd.cloud.redpanda.com:9092
KAFKA_TOPIC=belly-price
KAFKA_CONSUMER_GROUP=belly-consumers
KAFKA_USERNAME=crypto
KAFKA_PASSWORD=your_password

# === AIRFLOW ===
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=MySecurePassword123!
AIRFLOW_EMAIL=admin@belly.cloud
AIRFLOW_SQL_ALCHEMY_CONN=sqlite:////app/airflow/airflow.db

# === APP ===
APP_ENV=production
LOG_LEVEL=INFO
TZ=UTC
PYTHONUNBUFFERED=1
BACKEND_API_URL=https://your-domain.com
API_PORT=8000
REFLEX_HOST=0.0.0.0
REFLEX_PORT=3000
```

---

## ✅ Pre-Flight Checklist

Before pasting variables:

- [ ] You have Supabase project running
- [ ] You have Redis Upstash database created
- [ ] You have Kafka brokers configured
- [ ] You have strong Airflow password
- [ ] You have rotated all credentials (see SECURITY.md)
- [ ] All values are correct (no typos)

---

## 🚨 SECURITY REMINDER

### DO ✅
- Store credentials in cloud platform dashboard
- Use environment variables for ALL secrets
- Rotate credentials monthly
- Use strong passwords (12+ chars)
- Enable 2FA on your accounts

### DON'T ❌
- Never paste credentials in public
- Never commit .env files
- Never share passwords in Slack/Email
- Never use default passwords
- Never hardcode secrets in code

---

## 🔄 How to Update Variables

### Railway
```bash
railway variables set KEY new_value
```

### Vercel
1. Dashboard → Settings → Environment Variables
2. Click variable name
3. Update value
4. Redeploy

### Docker / VPS
```bash
# Edit .env.production
nano .env.production

# Restart container
docker-compose -f docker-compose.prod.yml restart
```

---

## 📊 Cost-Free Way to Test

Deploy to Railway with free tier:
```bash
# 1. Sign up at railway.app
# 2. Deploy from GitHub (this guide)
# 3. Get $5/month free credit
# 4. Test everything for free
# 5. Upgrade if needed
```

---

## 🎯 Next Steps

1. **Collect all values** - From Supabase, Redis, Kafka
2. **Copy this template** - And fill in your values
3. **Set in cloud dashboard** - Or create `.env.production`
4. **Deploy** - Using `./deploy_cloud.sh`
5. **Test endpoints** - `curl https://your-domain.com/health`
6. **Share URL** - Everyone can access now! 🎉

---

## 🆘 Troubleshooting

### "Error: Environment variable not found"
- Check variable name is EXACTLY correct (case-sensitive)
- Make sure you saved it in platform dashboard
- Redeploy after adding variables

### "Connection refused"
- Verify all URLs are correct
- Check IP addresses are whitelisted
- Test from local: `python -c "import redis; redis.from_url(...)"`

### "Authentication failed"
- Double-check credentials
- Verify credentials haven't expired
- Rotate credentials if needed

---

**Ready to deploy? Let's go! 🚀**

```bash
./deploy_cloud.sh
```
