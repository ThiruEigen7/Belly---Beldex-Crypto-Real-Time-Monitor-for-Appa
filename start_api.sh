#!/bin/bash
# Start BELLY FastAPI Backend Server

set -e

echo "🚀 Starting BELLY API Server..."
echo ""

# Check if we're in the right directory
if [ ! -f "belly/zebra/main.py" ]; then
    echo "❌ Error: Please run this from the belly root directory"
    exit 1
fi

# Activate virtual environment
if [ -f "env/bin/activate" ]; then
    echo "✅ Activating virtual environment..."
    source env/bin/activate
else
    echo "⚠️  Warning: Virtual environment not found"
fi

# Check if required packages are installed
python3 -c "import fastapi" 2>/dev/null || {
    echo "⚠️  FastAPI not installed. Installing..."
    pip install fastapi uvicorn
}

# Set environment variables (if .env.production exists)
if [ -f ".env.production" ]; then
    echo "✅ Loading environment variables from .env.production"
    export $(cat .env.production | grep -v '^#' | xargs)
fi

# Check if Supabase credentials are set
if [ -z "$SUPABASE_URL" ]; then
    echo "⚠️  Warning: SUPABASE_URL not set"
    echo "   Set it in .env or export SUPABASE_URL=your_url"
fi

if [ -z "$SUPABASE_ANON_KEY" ]; then
    echo "⚠️  Warning: SUPABASE_ANON_KEY not set"
    echo "   Set it in .env or export SUPABASE_ANON_KEY=your_key"
fi

# Start server
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  BELLY API Server Starting"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 API URL:  http://localhost:8000"
echo "📖 Docs:     http://localhost:8000/docs"
echo "📚 Redoc:    http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run from project root with proper module path
python3 -m uvicorn belly.zebra.main:app --host 0.0.0.0 --port 8000 --reload
