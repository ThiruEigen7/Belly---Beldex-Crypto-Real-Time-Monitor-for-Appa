#!/bin/bash

# 🚀 BELLY - Cloud Deployment Helper
# Choose and deploy to your preferred cloud platform

set -e

echo ""
echo "████████████████████████████████████████"
echo "🚀 BELLY - Cloud Deployment"
echo "████████████████████████████████████████"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Menu
echo -e "${BLUE}Choose your deployment platform:${NC}"
echo ""
echo "1) 🚂 Railway (RECOMMENDED - Easiest, $5-50/month)"
echo "2) 🎨 Vercel (Frontend only, Free-$20/month)"
echo "3) 🏗️  AWS ECS (Advanced, pay-as-you-go)"
echo "4) 🌩️  Google Cloud Run (Advanced, $0.00002/request)"
echo "5) 🔵 Azure Container Instances (Advanced, $15-50/month)"
echo "6) 🐳 Docker Local/VPS (Full control)"
echo "7) 📖 Show Deployment Guide"
echo "8) ❌ Exit"
echo ""
read -p "Enter choice (1-8): " choice

case $choice in
    1)
        echo -e "${BLUE}🚂 Railway Deployment${NC}"
        echo ""
        echo -e "${YELLOW}Steps:${NC}"
        echo "1. Go to https://railway.app"
        echo "2. Sign up with GitHub"
        echo "3. Click 'New Project' → 'Deploy from GitHub'"
        echo "4. Select your repository"
        echo "5. Add environment variables from .env.production"
        echo "6. Railway auto-deploys!"
        echo ""
        read -p "Have you completed the steps above? (y/n): " confirm
        if [[ $confirm == "y" || $confirm == "Y" ]]; then
            echo -e "${GREEN}✅ Your app will be available soon!${NC}"
            echo -e "${BLUE}📊 Monitor your deployment:${NC}"
            echo "   Dashboard: https://railway.app/dashboard"
            echo ""
        fi
        ;;
    2)
        echo -e "${BLUE}🎨 Vercel Deployment (Frontend)${NC}"
        echo ""
        echo -e "${YELLOW}Steps:${NC}"
        echo "1. Go to https://vercel.com"
        echo "2. Sign up with GitHub"
        echo "3. Click 'New Project' → 'Import Git Repository'"
        echo "4. Select your repository"
        echo "5. Set environment variable: BACKEND_API_URL"
        echo "6. Deploy!"
        echo ""
        echo -e "${YELLOW}Note:${NC} You'll need API deployed first (use Railway)"
        echo ""
        read -p "Ready to deploy to Vercel? (y/n): " confirm
        if [[ $confirm == "y" || $confirm == "Y" ]]; then
            echo -e "${GREEN}✅ Frontend will be deployed soon!${NC}"
        fi
        ;;
    3)
        echo -e "${BLUE}🏗️  AWS ECS Deployment${NC}"
        echo ""
        echo -e "${YELLOW}Prerequisites:${NC}"
        echo "- AWS Account with ECR and ECS access"
        echo "- AWS CLI installed and configured"
        echo "- Docker installed"
        echo ""
        read -p "Do you have all prerequisites? (y/n): " confirm
        if [[ $confirm == "y" || $confirm == "Y" ]]; then
            echo ""
            echo -e "${BLUE}Steps:${NC}"
            echo "1. Create ECR repository:"
            echo "   aws ecr create-repository --repository-name belly-api --region us-east-1"
            echo ""
            echo "2. Build and push Docker image:"
            echo "   docker build -t belly-api:latest ."
            echo "   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI"
            echo "   docker tag belly-api:latest YOUR_ECR_URI/belly-api:latest"
            echo "   docker push YOUR_ECR_URI/belly-api:latest"
            echo ""
            echo "3. Create ECS task definition and service in AWS Console"
            echo ""
        fi
        ;;
    4)
        echo -e "${BLUE}🌩️  Google Cloud Run Deployment${NC}"
        echo ""
        echo -e "${YELLOW}Prerequisites:${NC}"
        echo "- Google Cloud Account"
        echo "- gcloud CLI installed"
        echo "- Docker installed"
        echo ""
        read -p "Do you have all prerequisites? (y/n): " confirm
        if [[ $confirm == "y" || $confirm == "Y" ]]; then
            echo ""
            echo -e "${BLUE}Steps:${NC}"
            echo "1. Authenticate with gcloud:"
            echo "   gcloud auth login"
            echo ""
            echo "2. Build and deploy:"
            echo "   gcloud run deploy belly-api --source . --platform managed --region us-central1 --allow-unauthenticated"
            echo ""
            echo "3. Set environment variables in Cloud Run console"
            echo ""
        fi
        ;;
    5)
        echo -e "${BLUE}🔵 Azure Container Instances${NC}"
        echo ""
        echo -e "${YELLOW}Prerequisites:${NC}"
        echo "- Azure Account"
        echo "- Azure CLI installed"
        echo "- Docker installed"
        echo ""
        read -p "Do you have all prerequisites? (y/n): " confirm
        if [[ $confirm == "y" || $confirm == "Y" ]]; then
            echo ""
            echo -e "${BLUE}Steps:${NC}"
            echo "1. Create resource group:"
            echo "   az group create --name belly-rg --location eastus"
            echo ""
            echo "2. Create container registry:"
            echo "   az acr create --resource-group belly-rg --name bellyregistry --sku Basic"
            echo ""
            echo "3. Build and push:"
            echo "   az acr build --registry bellyregistry --image belly-api:latest ."
            echo ""
            echo "4. Deploy:"
            echo "   az container create --resource-group belly-rg --name belly-api --image bellyregistry.azurecr.io/belly-api:latest --environment-variables SUPABASE_URL=your_url"
            echo ""
        fi
        ;;
    6)
        echo -e "${BLUE}🐳 Docker Deployment${NC}"
        echo ""
        echo -e "${YELLOW}Option A: Local Testing${NC}"
        echo "  docker-compose -f docker-compose.prod.yml up -d"
        echo ""
        echo -e "${YELLOW}Option B: VPS Deployment (DigitalOcean, Linode, etc.)${NC}"
        echo "  1. SSH into your VPS"
        echo "  2. Install Docker and Docker Compose"
        echo "  3. Clone repository: git clone your-repo-url"
        echo "  4. Create .env.production with credentials"
        echo "  5. Run: docker-compose -f docker-compose.prod.yml up -d"
        echo "  6. Access at: http://your-vps-ip:8000"
        echo ""
        read -p "Which option? (A/B): " docker_choice
        if [[ $docker_choice == "A" || $docker_choice == "a" ]]; then
            echo -e "${GREEN}Starting local Docker deployment...${NC}"
            docker-compose -f docker-compose.prod.yml up -d
            echo -e "${GREEN}✅ Containers started!${NC}"
            echo "   API: http://localhost:8000"
            echo "   Frontend: http://localhost:3000"
            echo "   Airflow: http://localhost:8080"
            docker-compose -f docker-compose.prod.yml logs -f
        fi
        ;;
    7)
        echo ""
        echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"
        echo ""
        cat DEPLOYMENT_GUIDE.md
        ;;
    8)
        echo -e "${GREEN}Goodbye! 👋${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════"
echo -e "${GREEN}🎉 Deployment Helper Complete!${NC}"
echo "════════════════════════════════════════"
echo ""
echo -e "${BLUE}📚 Resources:${NC}"
echo "• Deployment Guide: DEPLOYMENT_GUIDE.md"
echo "• Security Guide: SECURITY.md"
echo "• Config Template: .env.example"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "• Rotate all credentials BEFORE going public (see SECURITY.md)"
echo "• Never commit .env or .env.production files"
echo "• Always use HTTPS in production"
echo "• Monitor your resource usage and costs"
echo ""
