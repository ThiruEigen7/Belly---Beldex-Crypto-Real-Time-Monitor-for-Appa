#!/bin/bash
# ============================================
# BELLY - Stop All Services
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}🛑 Stopping BELLY services...${NC}"

# Stop Producer
if [ -f "logs/producer.pid" ]; then
    PID=$(cat logs/producer.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo -e "${GREEN}✅ Producer stopped (PID: $PID)${NC}"
    fi
    rm logs/producer.pid
fi

# Stop Consumer
if [ -f "logs/consumer.pid" ]; then
    PID=$(cat logs/consumer.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo -e "${GREEN}✅ Consumer stopped (PID: $PID)${NC}"
    fi
    rm logs/consumer.pid
fi

# Stop Frontend
if [ -f "logs/frontend.pid" ]; then
    PID=$(cat logs/frontend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo -e "${GREEN}✅ Frontend stopped (PID: $PID)${NC}"
    fi
    rm logs/frontend.pid
fi

# Stop Airflow
if command -v docker &> /dev/null; then
    cd belly/airflow
    if docker-compose -f docker-compose.production.yml ps | grep -q belly-airflow; then
        docker-compose -f docker-compose.production.yml down
        echo -e "${GREEN}✅ Airflow stopped${NC}"
    fi
    cd ../..
fi

echo -e "${GREEN}✅ All services stopped${NC}"
