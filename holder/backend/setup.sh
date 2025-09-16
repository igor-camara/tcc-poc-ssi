#!/bin/bash

# Script to initialize the SSI Holder Backend

echo "🚀 Starting SSI Holder Backend Setup..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your actual values"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r ../config/requirements.txt

echo "✅ Setup complete! You can now start the development server with:"
echo "   python run.py"
echo ""
echo "🔧 Make sure ACA-Py is running on port 8031 for SSI functionality"
echo "📊 The API will be available at http://localhost:8000"