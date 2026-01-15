#!/bin/bash

echo "🚀 Docker Deployment Setup for app.preqly.com"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Build the image
echo "📦 Building Docker image..."
docker-compose build

echo ""
echo "🔧 Configuration Steps:"
echo "1. Generate SSL certificates:"
echo "   - Option A (Let's Encrypt): Follow DOCKER_DEPLOYMENT_GUIDE.md"
echo "   - Option B (Self-signed for testing):"
echo "     mkdir -p ssl"
echo "     openssl req -x509 -newkey rsa:4096 -nodes -out ssl/cert.pem -keyout ssl/key.pem -days 365"
echo ""
echo "2. Update .env.production with your settings"
echo ""
echo "3. Start the application:"
echo "   docker-compose up -d"
echo ""
echo "4. Check logs:"
echo "   docker-compose logs -f"
echo ""
echo "5. Access your app:"
echo "   https://app.preqly.com"
echo ""
echo "✅ Setup complete!"
