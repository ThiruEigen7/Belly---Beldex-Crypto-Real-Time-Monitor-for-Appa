#!/bin/bash
# Start all BELLY services

set -e

PROJECT_ROOT="/home/thiru/belly"
cd "$PROJECT_ROOT"

echo "🚀 Starting BELLY - Complete System"
echo "===================================="

# Activate virtual environment
source env/bin/activate

# 1. Start Airflow (Docker)
echo ""
echo "📊 1. Starting Airflow (Docker)..."
cd belly/airflow
docker-compose -f docker-compose.sqlite.yml up -d
echo "   ✅ Airflow running: http://localhost:8080 (admin/admin123)"
cd "$PROJECT_ROOT"

# 2. Start API Backend
echo ""
echo "🔌 2. Starting Backend API..."
./start_api.sh &
API_PID=$!
echo "   ✅ API running: http://localhost:8000"
echo "   PID: $API_PID"

# 3. Start Kafka Producer
echo ""
echo "📡 3. Starting Kafka Producer..."
cd belly/streaming
python3 producer.py > ../../logs/producer.log 2>&1 &
PRODUCER_PID=$!
echo "   ✅ Producer running (fetches every 10 min)"
echo "   PID: $PRODUCER_PID"
cd "$PROJECT_ROOT"

# 4. Start Kafka Consumer
echo ""
echo "📥 4. Starting Kafka Consumer..."
cd belly/streaming
python3 consumer.py > ../../logs/consumer.log 2>&1 &
CONSUMER_PID=$!
echo "   ✅ Consumer running (writes to Redis + Supabase)"
echo "   PID: $CONSUMER_PID"
cd "$PROJECT_ROOT"

# 5. Start Frontend (Reflex)
echo ""
echo "🎨 5. Starting Frontend..."
reflex run > logs/reflex.log 2>&1 &
REFLEX_PID=$!
echo "   ✅ Frontend running: http://localhost:3000"
echo "   PID: $REFLEX_PID"

# Create logs directory if not exists
mkdir -p logs

# Save PIDs
echo "$API_PID" > logs/api.pid
echo "$PRODUCER_PID" > logs/producer.pid
echo "$CONSUMER_PID" > logs/consumer.pid
echo "$REFLEX_PID" > logs/reflex.pid

echo ""
echo "===================================="
echo "✅ All services started!"
echo ""
echo "📍 Service URLs:"
echo "   • Frontend:  http://localhost:3000"
echo "   • API:       http://localhost:8000"
echo "   • Airflow:   http://localhost:8080 (admin/admin123)"
echo ""
echo "📋 Process IDs saved in logs/*.pid"
echo "📝 Logs available in logs/*.log"
echo ""
echo "To stop all services, run: ./stop_all_services.sh"
