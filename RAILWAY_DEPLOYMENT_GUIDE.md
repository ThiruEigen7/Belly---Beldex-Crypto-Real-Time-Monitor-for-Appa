# 🚂 Railway Deployment: Step-by-Step (5 minutes)

## Why Railway?
- ✅ Simplest setup (no coding required)
- ✅ Auto-deploys from GitHub (on every push)
- ✅ Free tier ($5/month credit)
- ✅ Perfect for production
- ✅ Automatic HTTPS
- ✅ One-click rollback

---

## 📋 Pre-Deployment Checklist

Before you start, make sure:

- [ ] Your code is pushed to GitHub
  ```bash
  git add -A
  git commit -m "Ready for Railway deployment"
  git push origin main
  ```

- [ ] You have Supabase project running
  - URL: `https://bcioieesyhilfrfgogpq.supabase.co`
  - Anon Key: Available in Supabase dashboard

- [ ] You have Redis Upstash running
  - URL: `https://settling-locust-8886.upstash.io`
  - Token: Available in Upstash console

- [ ] You have Kafka credentials
  - Brokers, Username, Password from Redpanda Cloud

- [ ] All credentials are **rotated** (see SECURITY.md)

---

## 🚀 Step 1: Create Railway Account

1. Go to https://railway.app
2. Click "Sign Up"
3. Choose "Sign up with GitHub" (recommended)
4. Authorize Railway to access GitHub
5. Create account

**Time: 2 minutes**

---

## 📝 Step 2: Create New Project

1. Click **"Create a New Project"** on Railway dashboard
2. Select **"Deploy from GitHub repo"**
3. Search for your repository: `Belly---Beldex-Crypto-Real-Time-Monitor-for-Appa`
4. Click your repository name
5. Click **"Deploy Now"**

**Time: 1 minute**

*Railway starts building your app automatically!*

---

## ⚙️ Step 3: Set Environment Variables

While Railway is building, set up your environment variables:

### Option A: Via Railway Dashboard (Easiest)

1. In Railway dashboard, click **Variables** tab
2. Click **"New Variable"**
3. Paste each variable (see below)

### Variables to Add

```
# === SUPABASE (Database) ===
SUPABASE_URL=https://bcioieesyhilfrfgogpq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# === REDIS (Cache) ===
REDIS_URL=https://settling-locust-8886.upstash.io
REDIS_TOKEN=ABEaXXXXXXXXXXXXXXXXXXXXXXXXXX...

# === KAFKA (Streaming) ===
KAFKA_BROKERS=d4qn7d0e5lrisl4hsue0.any.us-central1.gc.prd.cloud.redpanda.com:9092
KAFKA_TOPIC=belly-price
KAFKA_CONSUMER_GROUP=belly-consumers
KAFKA_USERNAME=crypto
KAFKA_PASSWORD=your_kafka_password

# === AIRFLOW (DAG Scheduler) ===
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=strong_password_here
AIRFLOW_EMAIL=admin@belly.cloud
AIRFLOW_SQL_ALCHEMY_CONN=sqlite:////app/airflow/airflow.db

# === APP CONFIG ===
APP_ENV=production
LOG_LEVEL=INFO
TZ=UTC
PYTHONUNBUFFERED=1
```

### Step-by-Step for Each Variable:

1. Click **"New Variable"** button
2. Enter **variable name** (e.g., `SUPABASE_URL`)
3. Enter **value** (e.g., `https://bcioieesyhilfrfgogpq.supabase.co`)
4. Click **checkmark** to save
5. Variable appears in list
6. Repeat for all variables

**Time: 3 minutes for all variables**

---

## 🐳 Step 4: Configure Build Settings

1. Click **"Settings"** tab (if available)
2. Make sure **Python** is selected
3. Confirm **requirements.txt** is detected
4. Set **start command** to:
   ```bash
   python -m uvicorn belly.zebra.main:app --host 0.0.0.0 --port $PORT
   ```

*Most of this is automatic - you may not need to change anything*

---

## ✅ Step 5: Wait for Deployment

Railway shows deployment progress:

```
📦 Building...        (2-3 minutes)
✅ Built successfully
🚀 Deploying...      (1 minute)
✅ Running           (Ready!)
```

When you see **"Running"**, your app is live!

**Time: 3-5 minutes**

---

## 🌐 Step 6: Get Your URL

1. Click **"Settings"** or **"Deployments"** tab
2. Look for **"Domains"** section
3. You'll see a URL like: `https://belly-production-abc123.up.railway.app`
4. This is your public URL!
5. Copy it

**Your app is now live at this URL!** 🎉

---

## 🧪 Step 7: Test Your Deployment

Test that everything works:

### Test 1: Health Check
```bash
curl https://belly-production-abc123.up.railway.app/health
```

Expected response:
```json
{"status": "ok"}
```

### Test 2: Current Price
```bash
curl https://belly-production-abc123.up.railway.app/current-price
```

Expected response:
```json
{"price": 8.13, "currency": "inr", "timestamp": "..."}
```

### Test 3: API Documentation
Open in browser:
```
https://belly-production-abc123.up.railway.app/docs
```

You should see interactive API documentation!

---

## 🔗 Step 8: Add Custom Domain (Optional)

If you want a custom domain (e.g., `belly.com`):

1. Buy domain from GoDaddy, Namecheap, or Google Domains
2. In Railway dashboard → **Settings** → **Domains**
3. Click **"Add Domain"**
4. Enter your domain name
5. Copy DNS records from Railway
6. Add DNS records to your domain provider
7. Wait 15-30 minutes for DNS propagation

**Your app will be at: `https://belly.com` 🌐**

---

## 🔄 Step 9: Enable Auto-Deployments

Great news! Railway already auto-deploys on every git push:

```bash
# Every time you push...
git add -A
git commit -m "New feature"
git push origin main

# Railway automatically:
# 1. Detects new code
# 2. Builds new image
# 3. Deploys to production
# 4. No downtime!
```

**You don't need to do anything!** ✅

---

## 📊 Step 10: Monitor Your App

### View Logs
1. Railway Dashboard → **Logs**
2. See real-time application logs
3. Debug issues here

### View Metrics
1. Railway Dashboard → **Metrics**
2. CPU usage
3. Memory usage
4. Network traffic

### Set Alerts
1. Railway Dashboard → **Alerts**
2. Set spending limits
3. Get notified if something breaks

---

## 🚨 Troubleshooting

### "App won't start"
1. Check logs in Railway dashboard
2. Verify all environment variables are set
3. Check Python version is 3.13
4. Look for startup command errors

### "Can't connect to Supabase"
1. Verify `SUPABASE_URL` is correct
2. Verify `SUPABASE_ANON_KEY` is correct
3. Check Supabase API key permissions
4. Test locally first: `python -c "import supabase"`

### "Deployment failed"
1. Check git push was successful: `git log --oneline`
2. Check files were committed: `git status`
3. Review Railway logs for build errors
4. Try deploying again

### "Performance is slow"
1. Check API response time in logs
2. Monitor database queries
3. Enable Redis caching
4. Upgrade Railway plan if needed

---

## 💡 Pro Tips

### Tip 1: Rollback to Previous Version
1. Railway Dashboard → **Deployments**
2. See all previous deployments
3. Click one to view details
4. Click **"Rollback"** if something breaks

### Tip 2: Environment-Specific Variables
Set different variables for different environments:
- **Production**: `APP_ENV=production`
- **Staging**: `APP_ENV=staging`
- **Development**: `APP_ENV=development`

### Tip 3: Use Secrets for Sensitive Data
Instead of exposing credentials, use:
```
Railway UI → Variables → Mark as "Secret"
```

Then access in code:
```python
import os
db_password = os.environ.get('DB_PASSWORD')
```

### Tip 4: Monitor Costs
Railway charges based on resource usage:
- CPU time: ~$0.0002/hour
- Memory: $15/GB/month
- Network: Included (generous limits)
- Storage: $0.50/GB/month

**Set spending limits to avoid surprises!**

---

## 🎉 You're Done!

Your BELLY app is now:
- ✅ Running on Railway
- ✅ Publicly accessible
- ✅ Auto-deploying from GitHub
- ✅ Monitored and logged
- ✅ Available 24/7
- ✅ Scalable automatically
- ✅ Protected with HTTPS

---

## 📱 Share Your App!

Send everyone your URL:

```
🌐 BELLY - Beldex Real-Time Price Monitor
📱 https://belly-production-abc123.up.railway.app
📊 Real-time crypto price tracking
💰 Current Price: ₹8.13
```

Or with custom domain:
```
🌐 BELLY - Beldex Real-Time Price Monitor
📱 https://belly.com
📊 Real-time crypto price tracking
💰 Current Price: ₹8.13
```

---

## 🔐 Remember: Security

- [ ] All credentials are rotated (SECURITY.md)
- [ ] .env files are in .gitignore ✅
- [ ] No secrets in code
- [ ] No secrets in git history
- [ ] Enable 2FA on Railway account
- [ ] Enable 2FA on GitHub account
- [ ] Review Railway security settings

---

## 📚 Next Steps

1. ✅ App deployed on Railway
2. Next: Start Kafka producer/consumer for live data
   ```bash
   cd belly/streaming
   python producer.py  # In one terminal
   python consumer.py  # In another terminal
   ```

3. Next: Setup monitoring
   - Railway logs
   - Error tracking (Sentry)
   - Uptime monitoring (Pingdom)

4. Next: Setup CI/CD pipeline (optional)
   - Run tests before deploying
   - Automatic security scans
   - Performance testing

---

## 🆘 Need Help?

Resources:
- Railway Docs: https://docs.railway.app
- Railway Support: https://railway.app/support
- Our DEPLOYMENT_GUIDE.md: Detailed guide for other platforms

---

## ✨ Summary

| Step | Time | Action |
|------|------|--------|
| 1 | 2 min | Create Railway account |
| 2 | 1 min | Create new project |
| 3 | 3 min | Set environment variables |
| 4 | 1 min | Configure build settings |
| 5 | 5 min | Wait for deployment |
| 6 | 1 min | Get your URL |
| 7 | 2 min | Test endpoints |
| **TOTAL** | **~15 min** | **Live! 🚀** |

---

**Congratulations! Your app is live and available for everyone! 🎉**

Every time you push to GitHub, Railway automatically deploys your changes. You're all set!

---

*Last Updated: December 14, 2025*
*BELLY - Beldex Real-Time Price Monitor*
