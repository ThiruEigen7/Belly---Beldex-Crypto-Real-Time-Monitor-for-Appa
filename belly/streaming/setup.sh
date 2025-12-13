#!/bin/bash
# Setup script for Belly streaming layer

echo "=================================================="
echo "BELLY Streaming Layer - Setup"
echo "=================================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with required configuration"
    exit 1
fi

echo "✅ .env file found"
echo ""

# Check Python environment
echo "Checking Python environment..."
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 installed: $(python3 --version)"
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=================================================="
echo "✅ Setup complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Run tests:"
echo "   python test_streaming_end_to_end.py"
echo ""
echo "2. Start producer:"
echo "   python belly/streaming/producer.py"
echo ""
echo "3. Start consumer (in another terminal):"
echo "   python belly/streaming/consumer.py"
echo ""
echo "=================================================="
