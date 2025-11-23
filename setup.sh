#!/bin/bash

# Setup script for Securing Web Application API
# This script helps set up the project for development

set -e

echo "🚀 Setting up Securing Web Application API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from env.example..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration!"
else
    echo "✅ .env file already exists"
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Run migrations
echo "🗄️  Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Create a superuser: python manage.py createsuperuser"
echo "3. Run the server: python manage.py runserver"
echo ""
echo "The API will be available at http://localhost:8000"

