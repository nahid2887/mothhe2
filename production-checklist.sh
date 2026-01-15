#!/bin/bash

# Production Deployment Checklist

echo "🔒 Production Deployment Checklist for app.preqly.com"
echo "====================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_item() {
    echo -e "${YELLOW}□${NC} $1"
}

complete_item() {
    echo -e "${GREEN}✓${NC} $1"
}

echo "📋 PRE-DEPLOYMENT CHECKS"
echo ""

# Check 1: Docker installed
check_item "Docker installed and running"
if command -v docker &> /dev/null; then
    complete_item "Docker installed and running"
fi

# Check 2: Docker Compose installed
check_item "Docker Compose installed"
if command -v docker-compose &> /dev/null; then
    complete_item "Docker Compose installed"
fi

# Check 3: SSL certificates
check_item "SSL certificates in ./ssl/ directory"
if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
    complete_item "SSL certificates present"
else
    echo -e "${RED}✗ Missing SSL certificates${NC}"
    echo "  Generate with: openssl req -x509 -newkey rsa:4096 -nodes -out ssl/cert.pem -keyout ssl/key.pem -days 365"
fi

# Check 4: .env.production
check_item ".env.production configured"
if [ -f ".env.production" ]; then
    complete_item ".env.production exists"
fi

# Check 5: Static files directory
check_item "Staticfiles directory created"
if [ -d "staticfiles" ]; then
    complete_item "Staticfiles directory exists"
fi

echo ""
echo "📦 CONFIGURATION STEPS"
echo ""

# Step 1: Review settings
check_item "Review .env.production"
echo "   - DEBUG should be False"
echo "   - SECRET_KEY should be long and random"
echo "   - ALLOWED_HOSTS should include app.preqly.com"

# Step 2: DNS
check_item "Configure DNS records"
echo "   - app.preqly.com → your-server-ip"
echo "   - www.app.preqly.com → your-server-ip (optional)"

# Step 3: Firewall
check_item "Open firewall ports"
echo "   - Port 80 (HTTP)"
echo "   - Port 443 (HTTPS)"
echo "   - Port 22 (SSH - for your access only)"

# Step 4: SSL Certificates
check_item "Install SSL certificates"
echo "   Option 1: Let's Encrypt (recommended)"
echo "     certbot certonly --standalone -d app.preqly.com"
echo "     cp /etc/letsencrypt/live/app.preqly.com/fullchain.pem ssl/cert.pem"
echo "     cp /etc/letsencrypt/live/app.preqly.com/privkey.pem ssl/key.pem"
echo ""
echo "   Option 2: Commercial certificate"
echo "     Place cert.pem and key.pem in ssl/ directory"

echo ""
echo "🚀 DEPLOYMENT"
echo ""

# Deployment steps
echo "1. Build Docker image:"
echo "   docker-compose build"
echo ""
echo "2. Start containers:"
echo "   docker-compose up -d"
echo ""
echo "3. Verify:"
echo "   docker-compose ps"
echo "   docker-compose logs -f web"
echo ""
echo "4. Create superuser:"
echo "   docker-compose exec web python manage.py createsuperuser"
echo ""
echo "5. Test at:"
echo "   https://app.preqly.com"

echo ""
echo "📊 MONITORING"
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo "  docker-compose logs -f web"
echo "  docker-compose logs -f nginx"
echo ""
echo "Check status:"
echo "  docker-compose ps"
echo "  docker ps"
echo ""
echo "Restart services:"
echo "  docker-compose restart web"
echo "  docker-compose restart nginx"

echo ""
echo "🔐 SECURITY"
echo ""
echo "✓ Keep Django DEBUG=False in production"
echo "✓ Use strong SECRET_KEY (generate random 50+ char string)"
echo "✓ Install SSL certificates"
echo "✓ Configure ALLOWED_HOSTS correctly"
echo "✓ Enable CSRF protection"
echo "✓ Keep Docker images updated: docker pull python:3.11-slim"
echo "✓ Backup database regularly: docker-compose exec web python manage.py dumpdata > backup.json"
echo "✓ Monitor logs for errors"
echo "✓ Set up log rotation"
echo "✓ Use strong database passwords"

echo ""
echo "🔄 MAINTENANCE"
echo ""
echo "Daily:"
echo "  - Check logs: docker-compose logs"
echo "  - Monitor resources: docker stats"
echo ""
echo "Weekly:"
echo "  - Backup database: docker-compose exec web python manage.py dumpdata > backup.json"
echo "  - Review error logs"
echo ""
echo "Monthly:"
echo "  - Update dependencies"
echo "  - Check SSL certificate expiration"
echo "  - Rebuild Docker image: docker-compose build"
echo ""
echo "Quarterly:"
echo "  - Security audit"
echo "  - Performance review"
echo "  - Backup verification"

echo ""
echo "✅ Ready to deploy!"
