#!/bin/bash

# Script to run the application locally with all required services
# Usage: ./run_local.sh

set -e

echo "🚀 Starting Product Importer Application"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis is not running. Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi

echo "✅ Redis is running"

# Check if migrations are up to date
echo "Checking migrations..."
python manage.py migrate --check > /dev/null 2>&1 || {
    echo "Running pending migrations..."
    python manage.py migrate
}

echo "✅ Database is up to date"

# Create necessary directories
mkdir -p media/uploads staticfiles

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput > /dev/null 2>&1

echo "✅ Static files collected"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $CELERY_PID 2>/dev/null || true
    kill $SERVER_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Celery worker in background
echo ""
echo "Starting Celery worker..."
celery -A config worker --loglevel=info --concurrency=4 > celery.log 2>&1 &
CELERY_PID=$!
echo "✅ Celery worker started (PID: $CELERY_PID)"

# Wait for Celery to initialize
sleep 2

# Start Django server
echo ""
echo "Starting Django server..."
echo "========================================"
echo "📱 Application running at: http://localhost:8000"
echo "🔧 Admin panel at: http://localhost:8000/admin"
echo "🔗 API at: http://localhost:8000/api"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

daphne -b 0.0.0.0 -p 8000 config.asgi:application &
SERVER_PID=$!

# Wait for both processes
wait $SERVER_PID

