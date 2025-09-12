#!/bin/bash

# Development Setup Script for MeetWhenAh
# This script helps set up local HTTPS development environment

echo "🚀 Setting up MeetWhenAh development environment..."

# Check if mkcert is installed
if ! command -v mkcert &> /dev/null; then
    echo "❌ mkcert is not installed. Please install it first:"
    echo "   macOS: brew install mkcert"
    echo "   Windows: choco install mkcert"
    echo "   Linux: See docs/development-setup.md"
    exit 1
fi

# Navigate to webapp directory
cd webapp

# Install local CA if not already installed
echo "📜 Installing local CA..."
mkcert -install

# Generate certificates
echo "🔐 Generating HTTPS certificates..."
mkcert localhost 127.0.0.1 ::1

# Check if certificates were created
if [ ! -f "localhost+2.pem" ] || [ ! -f "localhost+2-key.pem" ]; then
    echo "❌ Failed to generate certificates"
    exit 1
fi

echo "✅ Certificates generated successfully!"

# Go back to root directory
cd ..

# Check if .env.development exists
if [ ! -f "bot/.env.development" ]; then
    echo "📝 Creating .env.development file..."
    cat > bot/.env.development << EOF
ENVIRONMENT=development
BOT_USERNAME=your_dev_bot_username
TOKEN=your_dev_bot_token_here
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=true
LOCALHOST_PORT=3000
EOF
    echo "⚠️  Please edit bot/.env.development with your bot credentials"
else
    echo "✅ .env.development already exists"
fi

# Install dependencies
echo "📦 Installing dependencies..."

# Install webapp dependencies
cd webapp
if [ ! -d "node_modules" ]; then
    echo "Installing webapp dependencies..."
    npm install
fi
cd ..

# Install bot dependencies
cd bot
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing bot dependencies..."
pip install -r requirements.txt

cd ..

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit bot/.env.development with your bot credentials"
echo "2. Configure your bot in BotFather:"
echo "   - Go to @BotFather"
echo "   - /mybots → Your Bot → Mini App"
echo "   - Set URL to: https://localhost:3000"
echo ""
echo "3. Start development servers:"
echo "   Terminal 1: cd webapp && npm run dev"
echo "   Terminal 2: cd bot && source venv/bin/activate && python main.py"
echo ""
echo "📚 For detailed instructions, see docs/development-setup.md"
