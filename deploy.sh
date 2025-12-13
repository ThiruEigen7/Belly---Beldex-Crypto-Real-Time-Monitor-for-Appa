#!/bin/bash
# ============================================
# BELLY - Production Deployment Script
# ============================================
# This script deploys the complete BELLY system:
# 1. Streaming Layer (Producer + Consumer)
# 2. Airflow (Stats + Prediction DAGs)
# 3. Reflex Frontend (optional)
# ============================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          BELLY - Production Deployment                      ║"
echo "║          Beldex Crypto Real-Time Monitor                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================
# Check prerequisites
# ============================================
check_prerequisites() {
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        if [ -f ".env.production" ]; then
            echo -e "${YELLOW}⚠️  .env not found. Copying from .env.production...${NC}"
            cp .env.production .env
            echo -e "${GREEN}✅ Created .env file${NC}"
        else
            echo -e "${RED}❌ .env file not found. Please create it from .env.production${NC}"
            exit 1
        fi
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 not found. Please install Python 3.11+${NC}"
        exit 1
    fi
    
    # Check virtual environment
    if [ ! -d "env" ]; then
        echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
        python3 -m venv env
        source env/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    fi
    
    # Check Docker (optional, for Airflow)
    if command -v docker &> /dev/null; then
        DOCKER_AVAILABLE=true
        echo -e "${GREEN}✅ Docker available${NC}"
    else
        DOCKER_AVAILABLE=false
        echo -e "${YELLOW}⚠️  Docker not available (Airflow will not be deployed)${NC}"
    fi
    
    echo -e "${GREEN}✅ Prerequisites checked${NC}\n"
}

# ============================================
# Apply database migrations
# ============================================
apply_migrations() {
    echo -e "${YELLOW}🗄️  Applying database migrations...${NC}"
    
    # Note: For Supabase, migrations need to be run through SQL Editor
    echo -e "${BLUE}ℹ️  Please run the following migration in Supabase SQL Editor:${NC}"
    echo -e "${BLUE}   belly/zebra/migrations/001_update_predictions_schema.sql${NC}"
    echo -e "${YELLOW}Press any key to continue after running migration...${NC}"
    read -n 1 -s
    echo -e "${GREEN}✅ Migrations applied${NC}\n"
}

# ============================================
# Start Streaming Layer
# ============================================
start_streaming() {
    echo -e "${YELLOW}🚀 Starting Streaming Layer...${NC}"
    
    # Activate virtual environment
    source env/bin/activate
    
    # Create logs directory
    mkdir -p logs
    
    # Start Producer
    echo -e "${BLUE}▶️  Starting Producer...${NC}"
    nohup python belly/streaming/producer.py > logs/producer.log 2>&1 &
    PRODUCER_PID=$!
    echo $PRODUCER_PID > logs/producer.pid
    echo -e "${GREEN}✅ Producer started (PID: $PRODUCER_PID)${NC}"
    
    # Wait a moment
    sleep 2
    
    # Start Consumer
    echo -e "${BLUE}▶️  Starting Consumer...${NC}"
    nohup python belly/streaming/consumer.py > logs/consumer.log 2>&1 &
    CONSUMER_PID=$!
    echo $CONSUMER_PID > logs/consumer.pid
    echo -e "${GREEN}✅ Consumer started (PID: $CONSUMER_PID)${NC}"
    
    echo -e "${GREEN}✅ Streaming Layer started${NC}\n"
}

# ============================================
# Start Airflow
# ============================================
start_airflow() {
    if [ "$DOCKER_AVAILABLE" = false ]; then
        echo -e "${YELLOW}⚠️  Skipping Airflow (Docker not available)${NC}\n"
        return
    fi
    
    echo -e "${YELLOW}🔧 Starting Airflow...${NC}"
    
    cd belly/airflow
    
    # Build and start Airflow
    docker-compose -f docker-compose.production.yml up -d
    
    cd ../..
    
    echo -e "${GREEN}✅ Airflow started${NC}"
    echo -e "${BLUE}ℹ️  Airflow UI: http://localhost:8080${NC}"
    echo -e "${BLUE}   Username: admin${NC}"
    echo -e "${BLUE}   Password: admin123${NC}\n"
}

# ============================================
# Start Frontend (Optional)
# ============================================
start_frontend() {
    echo -e "${YELLOW}🎨 Do you want to start the Reflex frontend? (y/n)${NC}"
    read -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}▶️  Starting Reflex frontend...${NC}"
        source env/bin/activate
        nohup reflex run > logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > logs/frontend.pid
        echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
        echo -e "${BLUE}ℹ️  Frontend UI: http://localhost:3000${NC}\n"
    else
        echo -e "${YELLOW}⏭️  Skipping frontend${NC}\n"
    fi
}

# ============================================
# Health Check
# ============================================
health_check() {
    echo -e "${YELLOW}🏥 Running health checks...${NC}"
    
    # Check Producer
    if [ -f "logs/producer.pid" ]; then
        PID=$(cat logs/producer.pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Producer running (PID: $PID)${NC}"
        else
            echo -e "${RED}❌ Producer not running${NC}"
        fi
    fi
    
    # Check Consumer
    if [ -f "logs/consumer.pid" ]; then
        PID=$(cat logs/consumer.pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Consumer running (PID: $PID)${NC}"
        else
            echo -e "${RED}❌ Consumer not running${NC}"
        fi
    fi
    
    # Check Airflow
    if [ "$DOCKER_AVAILABLE" = true ]; then
        if docker ps | grep -q belly-airflow-webserver; then
            echo -e "${GREEN}✅ Airflow running${NC}"
        else
            echo -e "${YELLOW}⚠️  Airflow not running${NC}"
        fi
    fi
    
    echo ""
}

# ============================================
# Display Status
# ============================================
display_status() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║          ✅ BELLY Deployment Complete!                       ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo -e "${BLUE}📊 Services Status:${NC}"
    echo -e "  • Producer: Fetching prices every 10 minutes"
    echo -e "  • Consumer: Writing to Redis + Supabase"
    echo -e "  • Airflow: http://localhost:8080 (admin/admin123)"
    echo ""
    
    echo -e "${BLUE}📁 Log Files:${NC}"
    echo -e "  • Producer: logs/producer.log"
    echo -e "  • Consumer: logs/consumer.log"
    echo -e "  • Frontend: logs/frontend.log"
    echo ""
    
    echo -e "${BLUE}🛠️  Management Commands:${NC}"
    echo -e "  • Stop all: ./scripts/stop.sh"
    echo -e "  • View logs: tail -f logs/producer.log"
    echo -e "  • Status: ./scripts/status.sh"
    echo ""
}

# ============================================
# Main Deployment Flow
# ============================================
main() {
    check_prerequisites
    apply_migrations
    start_streaming
    start_airflow
    start_frontend
    health_check
    display_status
}

# Run main function
main
