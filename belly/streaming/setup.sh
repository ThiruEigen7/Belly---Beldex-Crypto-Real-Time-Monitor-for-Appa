#!/bin/bash

# BELLY Streaming Layer Setup Script for Manjaro Linux

echo "🚀 Setting up BELLY Streaming Layer for Manjaro Linux..."
echo ""

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ Unable to detect Linux distribution"
    exit 1
fi

echo "📋 Detected OS: $OS"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    if [ "$OS" = "manjaro" ] || [ "$OS" = "arch" ]; then
        echo "📦 Installing Docker for Manjaro/Arch..."
        sudo pacman -Syu --noconfirm
        sudo pacman -S --noconfirm docker
        echo "✅ Docker installed. Enabling and starting service..."
        sudo systemctl enable docker
        sudo systemctl start docker
        sudo usermod -aG docker $USER
        echo "⚠️  Please log out and log back in for group permissions to take effect"
    else
        echo "Please install Docker manually for your distribution"
        exit 1
    fi
fi

# Check if docker-compose is installed (as docker plugin)
if ! docker compose version &> /dev/null; then
    echo "❌ docker-compose plugin is not installed."
    if [ "$OS" = "manjaro" ] || [ "$OS" = "arch" ]; then
        echo "📦 Installing docker-compose plugin for Manjaro/Arch..."
        sudo pacman -S --noconfirm docker-compose
        echo "✅ docker-compose installed"
    else
        echo "Please install docker-compose manually for your distribution"
        exit 1
    fi
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ Created .env file - please edit with your settings"
else
    echo "✅ .env file already exists"
fi

# Start Docker services
echo ""
echo "🐳 Starting Docker services..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo ""
echo "📊 Checking service status..."
docker compose ps

# Create Kafka topic
echo ""
echo "📝 Creating Kafka topic 'belly-price'..."
docker exec belly-redpanda rpk topic create belly-price \
    --partitions 3 \
    --replicas 1 2>/dev/null || echo "⚠️  Topic might already exist"

# List topics
echo ""
echo "📋 Available topics:"
docker exec belly-redpanda rpk topic list

# Test connections
echo ""
echo "🧪 Testing connections..."

# Test Redis
if docker exec belly-redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis is not responding"
fi

# Test Postgres
if docker exec belly-postgres pg_isready -U postgres | grep -q "accepting connections"; then
    echo "✅ Postgres is ready"
else
    echo "❌ Postgres is not responding"
fi

# Test Kafka
if docker exec belly-redpanda rpk cluster health | grep -q "Healthy"; then
    echo "✅ Kafka/Redpanda is ready"
else
    echo "❌ Kafka/Redpanda is not responding"
fi

echo ""
echo "="*60
echo "✅ Setup Complete!"
echo "="*60
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Edit .env with your settings (if needed)"
echo ""
echo "2. Test the setup:"
echo "   python test_streaming.py"
echo ""
echo "3. Run Producer (Terminal 1):"
echo "   python producer.py"
echo ""
echo "4. Run Consumer (Terminal 2):"
echo "   python consumer.py"
echo ""
echo "5. View Redpanda Console:"
echo "   http://localhost:8080"
echo ""
echo "6. Monitor with:"
echo "   docker compose logs -f"
echo ""
echo "="*60