#!/bin/bash

# 🚀 BELLY - Railway Deployment Script
# Automates deployment to Railway cloud platform

set -e

echo "🚀 BELLY - Railway Deployment Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}📦 Railway CLI not found. Installing...${NC}"
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -L https://railway.app/install.sh | bash
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install railway
    else
        echo -e "${RED}❌ Unsupported OS. Please install Railway CLI manually from https://railway.app${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Railway CLI installed${NC}"

# Check if git is clean
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  You have uncommitted changes. Please commit them first:${NC}"
    echo "  git add -A"
    echo "  git commit -m 'Ready for deployment'"
    exit 1
fi

echo -e "${GREEN}✅ Git repository is clean${NC}"

# Login to Railway
echo -e "${BLUE}🔐 Logging into Railway...${NC}"
railway login

# Create new project (or link existing)
echo -e "${BLUE}📝 Creating/Linking Railway project...${NC}"
railway init

# Set environment variables
echo -e "${BLUE}🔧 Setting environment variables...${NC}"
echo -e "${YELLOW}Enter your environment variables (or press Enter to skip if already set):${NC}"

read -p "SUPABASE_URL (press Enter to skip): " SUPABASE_URL
if [ ! -z "$SUPABASE_URL" ]; then
    railway variables set SUPABASE_URL "$SUPABASE_URL"
fi

read -p "SUPABASE_ANON_KEY (press Enter to skip): " SUPABASE_ANON_KEY
if [ ! -z "$SUPABASE_ANON_KEY" ]; then
    railway variables set SUPABASE_ANON_KEY "$SUPABASE_ANON_KEY"
fi

read -p "REDIS_URL (press Enter to skip): " REDIS_URL
if [ ! -z "$REDIS_URL" ]; then
    railway variables set REDIS_URL "$REDIS_URL"
fi

read -p "REDIS_TOKEN (press Enter to skip): " REDIS_TOKEN
if [ ! -z "$REDIS_TOKEN" ]; then
    railway variables set REDIS_TOKEN "$REDIS_TOKEN"
fi

read -p "KAFKA_BROKERS (press Enter to skip): " KAFKA_BROKERS
if [ ! -z "$KAFKA_BROKERS" ]; then
    railway variables set KAFKA_BROKERS "$KAFKA_BROKERS"
fi

read -p "KAFKA_USERNAME (press Enter to skip): " KAFKA_USERNAME
if [ ! -z "$KAFKA_USERNAME" ]; then
    railway variables set KAFKA_USERNAME "$KAFKA_USERNAME"
fi

read -p "KAFKA_PASSWORD (press Enter to skip): " KAFKA_PASSWORD
if [ ! -z "$KAFKA_PASSWORD" ]; then
    railway variables set KAFKA_PASSWORD "$KAFKA_PASSWORD"
fi

echo -e "${GREEN}✅ Environment variables set${NC}"

# Deploy
echo -e "${BLUE}🚀 Deploying to Railway...${NC}"
railway up

# Get deployment URL
echo -e "${BLUE}📋 Fetching deployment information...${NC}"
PROJECT_ID=$(railway info --json | jq -r '.project.id' 2>/dev/null || echo "")
ENVIRONMENT_ID=$(railway info --json | jq -r '.environment.id' 2>/dev/null || echo "")

if [ ! -z "$PROJECT_ID" ]; then
    echo -e "${GREEN}✅ Project ID: $PROJECT_ID${NC}"
    echo -e "${GREEN}✅ Environment ID: $ENVIRONMENT_ID${NC}"
    echo -e "${BLUE}📱 Your app will be available at:${NC}"
    echo -e "${YELLOW}https://\$(railway info --json | jq -r '.service.url')${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Visit your Railway dashboard: https://railway.app/dashboard"
echo "2. Configure a custom domain (optional)"
echo "3. Check your application logs: railway logs"
echo "4. Test your API: curl https://your-domain.com/health"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  railway logs              - View application logs"
echo "  railway variables set KEY VALUE  - Set environment variables"
echo "  railway up                - Deploy again"
echo "  railway status            - Check deployment status"
echo ""
