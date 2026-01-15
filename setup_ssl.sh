#!/bin/bash

echo "========================================="
echo "Setting up SSL certificates with certbot"
echo "========================================="

# Stop nginx to free port 80 for certbot
echo "Stopping nginx container..."
docker-compose stop nginx

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot
fi

# Generate SSL certificate for app.preqly.com
echo "Generating SSL certificate for app.preqly.com..."
sudo certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email admin@preqly.com \
    --domains app.preqly.com \
    --preferred-challenges http

# Check if certificate was generated
if [ -f /etc/letsencrypt/live/app.preqly.com/fullchain.pem ]; then
    echo "✓ SSL certificate generated successfully!"
    echo "Certificate location: /etc/letsencrypt/live/app.preqly.com/"
    
    # List certificate files
    sudo ls -la /etc/letsencrypt/live/app.preqly.com/
    
    echo ""
    echo "Now restart Docker containers with: docker-compose up -d"
else
    echo "✗ Failed to generate SSL certificate"
    echo "Please check certbot logs for errors"
    exit 1
fi
