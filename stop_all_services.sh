#!/bin/bash
# Stop all BELLY services

PROJECT_ROOT="/home/thiru/belly"
cd "$PROJECT_ROOT"

echo "🛑 Stopping BELLY - All Services"
echo "================================="

# Stop PIDs from files
if [ -f logs/reflex.pid ]; then
    echo "Stopping Frontend (Reflex)..."
    kill $(cat logs/reflex.pid) 2>/dev/null || echo "   Already stopped"
    rm logs/reflex.pid
fi

if [ -f logs/consumer.pid ]; then
    echo "Stopping Kafka Consumer..."
    kill $(cat logs/consumer.pid) 2>/dev/null || echo "   Already stopped"
    rm logs/consumer.pid
fi

if [ -f logs/producer.pid ]; then
    echo "Stopping Kafka Producer..."
    kill $(cat logs/producer.pid) 2>/dev/null || echo "   Already stopped"
    rm logs/producer.pid
fi

if [ -f logs/api.pid ]; then
    echo "Stopping API Backend..."
    kill $(cat logs/api.pid) 2>/dev/null || echo "   Already stopped"
    rm logs/api.pid
fi

# Stop any remaining processes
echo "Stopping any remaining processes..."
pkill -f "uvicorn belly.zebra.main" 2>/dev/null || true
pkill -f "belly/streaming/producer.py" 2>/dev/null || true
pkill -f "belly/streaming/consumer.py" 2>/dev/null || true
pkill -f "reflex run" 2>/dev/null || true

# Stop Airflow Docker containers
echo "Stopping Airflow (Docker)..."
cd belly/airflow
docker-compose -f docker-compose.sqlite.yml down
cd "$PROJECT_ROOT"

echo ""
echo "✅ All services stopped!"
