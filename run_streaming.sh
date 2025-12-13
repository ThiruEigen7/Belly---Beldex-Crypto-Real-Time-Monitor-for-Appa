#!/bin/bash
# Run streaming services

echo "=================================================="
echo "BELLY Streaming - Starting Services"
echo "=================================================="
echo ""

# Activate virtual environment
source env/bin/activate

# Test connection first
echo "Testing Redpanda Cloud connection..."
python test_direct_producer.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Connection successful!"
    echo ""
    echo "Choose an option:"
    echo "1. Run producer only"
    echo "2. Run consumer only"  
    echo "3. Run both (producer in background)"
    echo "4. Run end-to-end test"
    echo ""
    read -p "Enter choice (1-4): " choice
    
    case $choice in
        1)
            echo "Starting producer..."
            python belly/streaming/producer.py
            ;;
        2)
            echo "Starting consumer..."
            python belly/streaming/consumer.py
            ;;
        3)
            echo "Starting producer in background..."
            python belly/streaming/producer.py &
            PRODUCER_PID=$!
            echo "Producer PID: $PRODUCER_PID"
            echo ""
            echo "Starting consumer..."
            python belly/streaming/consumer.py
            ;;
        4)
            echo "Running end-to-end test..."
            python test_streaming_end_to_end.py
            ;;
        *)
            echo "Invalid choice"
            exit 1
            ;;
    esac
else
    echo ""
    echo "❌ Connection failed. Check your .env configuration:"
    echo "   - KAFKA_BROKERS"
    echo "   - KAFKA_USERNAME"
    echo "   - KAFKA_PASSWORD"
fi
