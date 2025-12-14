# 🔐 Security & Environment Setup

## ⚠️ IMPORTANT: Exposed Secrets in Git History

If you see security warnings about exposed secrets, follow these steps:

### 1. **Rotate All Compromised Credentials**

Since the secrets were pushed to Git, you must rotate them immediately:

#### Supabase
1. Go to https://supabase.com/dashboard
2. Navigate to your project settings → API
3. Click "Reset anon key" or create a new service key
4. Update `.env.production` with the new key

#### Redis Upstash
1. Go to https://console.upstash.com
2. Select your Redis database
3. Click "Details" → "Reset Token"
4. Update `.env.production` with the new token

#### Redpanda Cloud
1. Go to your Redpanda console
2. Navigate to Security → Users
3. Delete the old user and create a new one
4. Update KAFKA_USERNAME and KAFKA_PASSWORD in `.env.production`

### 2. **Set Up Environment Files Correctly**

```bash
# Copy the example file
cp .env.example .env.production

# Edit with your NEW credentials (after rotation)
nano .env.production

# Verify .gitignore is working
git status  # Should NOT show .env.production
```

### 3. **Verify .gitignore**

Ensure these lines are in `.gitignore`:
```
.env
.env.production
.env.local
.env.*.local
*.env
```

### 4. **Clean Git History (Optional - Advanced)**

If you want to remove secrets from Git history:

```bash
# Use git-filter-repo (recommended)
pip install git-filter-repo
git filter-repo --path .env --invert-paths
git filter-repo --path .env.production --invert-paths

# Force push (⚠️ WARNING: This rewrites history)
git push origin main --force
```

**Note**: This will break any forks/clones. Coordinate with team members first.

### 5. **Enable Secret Scanning**

1. Go to your GitHub repository
2. Settings → Code security and analysis
3. Enable "Secret scanning"
4. Enable "Push protection" to prevent future leaks

## 📁 File Structure

```
.env.example          # Template with dummy values (SAFE to commit)
.env.production       # Real credentials (NEVER commit)
.env                  # Local development (NEVER commit)
.gitignore           # Must include all .env files
```

## ✅ Best Practices

1. **Never commit** `.env*` files with real credentials
2. **Always use** `.env.example` as a template
3. **Rotate secrets** immediately if exposed
4. **Use environment variables** in production (Railway, Vercel, etc.)
5. **Enable MFA** on all cloud services
6. **Review commits** before pushing

## 🚀 Production Deployment

For production deployments, use platform environment variables:

### Railway / Render / Vercel
Add environment variables in the dashboard, NOT in files:
- Go to Settings → Environment Variables
- Add each variable one by one
- Never use .env files in production

### Docker
Use `--env-file` flag:
```bash
docker run --env-file .env.production your-image
```

## 📞 Support

If you need help rotating credentials or removing secrets from history, contact your team lead.
