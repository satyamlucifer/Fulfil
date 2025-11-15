#!/bin/bash

# Product Importer Setup Script
# This script automates the initial setup process

set -e

echo "🚀 Product Importer Setup Script"
echo "================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3.11+ is installed
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check if PostgreSQL is installed
echo "Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL found${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL not found. You'll need to install it or use a remote database.${NC}"
fi

# Check if Redis is installed
echo "Checking Redis..."
if command -v redis-cli &> /dev/null; then
    echo -e "${GREEN}✅ Redis found${NC}"
else
    echo -e "${YELLOW}⚠️  Redis not found. You'll need to install it or use a remote Redis instance.${NC}"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Create .env file if it doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    
    # Generate SECRET_KEY
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    
    # Update .env with generated secret key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here/$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
    fi
    
    echo -e "${GREEN}✅ .env file created with generated SECRET_KEY${NC}"
    echo -e "${YELLOW}⚠️  Please update DATABASE_URL and REDIS_URL in .env file${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p static staticfiles media/uploads
echo -e "${GREEN}✅ Directories created${NC}"

# Run migrations
echo ""
echo "Running database migrations..."
read -p "Have you configured your DATABASE_URL in .env? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py migrate
    echo -e "${GREEN}✅ Migrations completed${NC}"
    
    # Create superuser
    echo ""
    read -p "Do you want to create a superuser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python manage.py createsuperuser
    fi
else
    echo -e "${YELLOW}⚠️  Skipping migrations. Run 'python manage.py migrate' after configuring database.${NC}"
fi

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo -e "${GREEN}✅ Static files collected${NC}"

# Generate sample CSV
echo ""
read -p "Do you want to generate a sample CSV file for testing? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "How many records? (default: 1000) " NUM_RECORDS
    NUM_RECORDS=${NUM_RECORDS:-1000}
    python generate_sample_csv.py -n $NUM_RECORDS
fi

echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo "Next steps:"
echo "1. Update .env file with your database and Redis URLs"
echo "2. Start Redis: redis-server"
echo "3. Start Celery worker: celery -A config worker --loglevel=info"
echo "4. Start Django server: python manage.py runserver"
echo "   Or for WebSocket support: daphne -b 0.0.0.0 -p 8000 config.asgi:application"
echo ""
echo "5. Access the application at: http://localhost:8000"
echo ""
echo "For Docker setup, run: docker-compose up --build"
echo ""

