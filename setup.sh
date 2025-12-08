#!/bin/bash

# Setup script for Room Availability Service
# This script helps you get started quickly with local development

set -e

echo "=========================================="
echo "Room Availability Service - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Check pip
echo "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi
echo "✅ pip3 is installed"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env to set your timezone!"
else
    echo "ℹ️  .env file already exists"
fi
echo ""

# Make test script executable
chmod +x test_service.py
echo "✅ Made test_service.py executable"
echo ""

# Summary
echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file to set your timezone:"
echo "   nano .env"
echo ""
echo "2. Start the development server:"
echo "   source venv/bin/activate  # If not already activated"
echo "   python3 room_availability_service.py"
echo ""
echo "3. In another terminal, test the service:"
echo "   source venv/bin/activate"
echo "   ./test_service.py"
echo ""
echo "4. When you have an ICS URL, test it:"
echo "   curl 'http://localhost:5000/room-status?ics_url=YOUR_ICS_URL&room_name=Test%20Room'"
echo ""
echo "For deployment instructions, see:"
echo "  - QUICKSTART.md (10-minute guide)"
echo "  - README.md (detailed instructions)"
echo "  - DEPLOYMENT_CHECKLIST.md (step-by-step)"
echo ""
echo "=========================================="
