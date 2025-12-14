#!/bin/bash
# Quick guide to rotate exposed credentials

echo "🔐 BELLY - Security Credential Rotation Guide"
echo "=============================================="
echo ""
echo "⚠️  Your credentials were exposed in Git. Follow these steps:"
echo ""

echo "1️⃣  SUPABASE (Database)"
echo "   → Go to: https://supabase.com/dashboard"
echo "   → Project Settings → API"
echo "   → Click 'Reset' for anon key"
echo "   → Update SUPABASE_ANON_KEY in .env.production"
echo ""

echo "2️⃣  REDIS UPSTASH (Cache)"
echo "   → Go to: https://console.upstash.com/redis"
echo "   → Select your database"
echo "   → Details → Reset Token"
echo "   → Update REDIS_TOKEN in .env.production"
echo ""

echo "3️⃣  REDPANDA CLOUD (Kafka)"
echo "   → Go to your Redpanda console"
echo "   → Security → Users"
echo "   → Delete old user, create new one"
echo "   → Update KAFKA_USERNAME and KAFKA_PASSWORD"
echo ""

echo "4️⃣  VERIFY SETUP"
echo "   → Run: git status"
echo "   → Should NOT see .env.production"
echo "   → If you see it, check .gitignore"
echo ""

echo "✅ After rotation:"
echo "   1. Update .env.production with NEW credentials"
echo "   2. Restart all services"
echo "   3. Test the system"
echo ""

read -p "Press Enter to continue..."
