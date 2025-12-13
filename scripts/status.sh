#!/bin/bash
# ============================================
# BELLY - Status Check
# ============================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          BELLY - System Status                               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Producer
echo -e "${YELLOW}📡 Streaming Layer:${NC}"
if [ -f "logs/producer.pid" ]; then
    PID=$(cat logs/producer.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Producer: Running (PID: $PID)${NC}"
        echo -e "     Last 3 log lines:"
        tail -n 3 logs/producer.log | sed 's/^/     /'
    else
        echo -e "  ${RED}❌ Producer: Not running${NC}"
    fi
else
    echo -e "  ${RED}❌ Producer: Not started${NC}"
fi

echo ""

# Check Consumer
if [ -f "logs/consumer.pid" ]; then
    PID=$(cat logs/consumer.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Consumer: Running (PID: $PID)${NC}"
        echo -e "     Last 3 log lines:"
        tail -n 3 logs/consumer.log | sed 's/^/     /'
    else
        echo -e "  ${RED}❌ Consumer: Not running${NC}"
    fi
else
    echo -e "  ${RED}❌ Consumer: Not started${NC}"
fi

echo ""

# Check Airflow
echo -e "${YELLOW}🔧 Airflow:${NC}"
if command -v docker &> /dev/null; then
    if docker ps | grep -q belly-airflow-webserver; then
        echo -e "  ${GREEN}✅ Airflow Webserver: Running${NC}"
        echo -e "     URL: http://localhost:8080"
    else
        echo -e "  ${RED}❌ Airflow Webserver: Not running${NC}"
    fi
    
    if docker ps | grep -q belly-airflow-scheduler; then
        echo -e "  ${GREEN}✅ Airflow Scheduler: Running${NC}"
    else
        echo -e "  ${RED}❌ Airflow Scheduler: Not running${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠️  Docker not available${NC}"
fi

echo ""

# Check Frontend
echo -e "${YELLOW}🎨 Frontend:${NC}"
if [ -f "logs/frontend.pid" ]; then
    PID=$(cat logs/frontend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Frontend: Running (PID: $PID)${NC}"
        echo -e "     URL: http://localhost:3000"
    else
        echo -e "  ${RED}❌ Frontend: Not running${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠️  Frontend: Not started${NC}"
fi

echo ""

# Resource usage
echo -e "${YELLOW}💻 Resource Usage:${NC}"
if [ -f "logs/producer.pid" ] || [ -f "logs/consumer.pid" ]; then
    echo -e "  Memory:"
    ps aux | grep -E "producer.py|consumer.py" | grep -v grep | awk '{print "   "$11": "$6/1024" MB"}' || echo "   N/A"
fi

echo ""
