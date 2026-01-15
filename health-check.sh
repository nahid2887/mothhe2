#!/bin/bash

# Health check and monitoring script for Docker deployment

echo "🏥 Health Check & Monitoring - app.preqly.com"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_status() {
    local service=$1
    local status=$(docker-compose ps $service --quiet)
    
    if [ -z "$status" ]; then
        echo -e "${RED}✗ $service: NOT RUNNING${NC}"
        return 1
    else
        echo -e "${GREEN}✓ $service: RUNNING${NC}"
        return 0
    fi
}

echo "📊 CONTAINER STATUS"
echo ""

# Check each service
check_status "web"
check_status "nginx"

echo ""
echo "📈 RESOURCE USAGE"
echo ""
docker stats --no-stream

echo ""
echo "📋 CONTAINER DETAILS"
echo ""
docker-compose ps

echo ""
echo "🔍 RECENT LOGS (Last 20 lines)"
echo ""
echo "--- Django Logs ---"
docker-compose logs --tail=10 web

echo ""
echo "--- Nginx Logs ---"
docker-compose logs --tail=10 nginx

echo ""
echo "🌐 API ENDPOINTS"
echo ""
echo "Main app: https://app.preqly.com"
echo "Admin: https://app.preqly.com/admin/"
echo ""

echo "🔗 TESTING"
echo ""
echo "Test HTTP redirect to HTTPS:"
echo "  curl -I http://localhost"
echo ""
echo "Test HTTPS connection (self-signed):"
echo "  curl -k https://localhost"
echo ""

echo "📊 DATABASE"
echo ""
if docker-compose exec -T web test -f db.sqlite3; then
    echo -e "${GREEN}✓ Database file exists${NC}"
    echo "  Location: /app/db.sqlite3"
    DB_SIZE=$(docker-compose exec -T web du -h db.sqlite3 | cut -f1)
    echo "  Size: $DB_SIZE"
else
    echo -e "${RED}✗ Database file not found${NC}"
fi

echo ""
echo "📁 VOLUMES"
echo ""
docker volume ls | grep -E "static_volume|media_volume"

echo ""
echo "🔐 SSL CERTIFICATES"
echo ""
if docker-compose exec -T nginx test -f /etc/nginx/ssl/cert.pem; then
    echo -e "${GREEN}✓ SSL certificate installed${NC}"
    docker-compose exec -T nginx openssl x509 -in /etc/nginx/ssl/cert.pem -noout -subject -dates 2>/dev/null || echo "  (Self-signed certificate)"
else
    echo -e "${RED}✗ SSL certificate not found${NC}"
fi

echo ""
echo "⚙️ CONFIGURATION"
echo ""
echo "Environment Variables:"
docker-compose exec -T web env | grep -E "DEBUG|ALLOWED_HOSTS|SECRET_KEY" || echo "  (Check .env.production)"

echo ""
echo "👤 DJANGO USERS"
echo ""
docker-compose exec -T web python manage.py shell -c "from django.contrib.auth.models import User; print('\\n'.join([f'  {u.username} (email: {u.email}, staff: {u.is_staff}, superuser: {u.is_superuser})' for u in User.objects.all()]))" 2>/dev/null || echo "  (No users or error)"

echo ""
echo "✨ QUICK COMMANDS"
echo ""
echo "View all logs:"
echo "  docker-compose logs -f"
echo ""
echo "Restart services:"
echo "  docker-compose restart"
echo ""
echo "Restart specific service:"
echo "  docker-compose restart web"
echo "  docker-compose restart nginx"
echo ""
echo "Rebuild and restart:"
echo "  docker-compose up -d --build"
echo ""
echo "Database backup:"
echo "  docker-compose exec web python manage.py dumpdata > backup.json"
echo ""
echo "Create admin user:"
echo "  docker-compose exec web python manage.py createsuperuser"
echo ""
echo "Run migrations:"
echo "  docker-compose exec web python manage.py migrate"
echo ""

echo "✅ Health check complete!"
