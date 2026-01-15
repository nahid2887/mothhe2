# 🌐 Port & Domain Configuration Guide

## External Access (Internet)

```
┌─────────────────────────────────────────────────────┐
│              app.preqly.com (Your Domain)           │
│                                                      │
│  HTTP (Port 80):                                    │
│  └─→ app.preqly.com → Redirects to HTTPS           │
│      301 Permanent Redirect                         │
│      ↓                                              │
│  HTTPS (Port 443):                                 │
│  └─→ app.preqly.com:443                            │
│      ✓ SSL/TLS Encrypted                           │
│      ✓ Certificate: cert.pem                       │
│      ✓ Key: key.pem                                │
│      ↓                                              │
│  Nginx Reverse Proxy (Inside Docker)               │
│  └─→ Forwards to Django on port 8005               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Internal Docker Network

```
┌─────────────────────────────────────────────────────┐
│         Docker Compose Network (app_network)        │
│                                                     │
│  ┌──────────────────────┐   ┌────────────────────┐ │
│  │   NGINX Container    │   │  DJANGO Container  │ │
│  │                      │   │                    │ │
│  │  Listens on:         │   │  Listens on:       │ │
│  │  • Port 80 (HTTP)    │   │  • Port 8005       │ │
│  │  • Port 443 (HTTPS)  │───→  (Gunicorn)       │ │
│  │                      │   │                    │ │
│  │  Serves:             │   │  Runs:             │ │
│  │  • Static files      │   │  • Django app      │ │
│  │  • Media files       │   │  • Migrations      │ │
│  │  • Security headers  │   │  • WSGI server     │ │
│  │                      │   │                    │ │
│  │  TLS/SSL             │   │  Process:          │ │
│  │  • Terminates HTTPS  │   │  • entrypoint.sh   │ │
│  │  • Verifies cert     │   │  • manage.py       │ │
│  │  • Adds headers      │   │  • Gunicorn        │ │
│  │                      │   │                    │ │
│  └──────────────────────┘   └────────────────────┘ │
│                                                     │
│  Shared Storage (Volumes):                         │
│  • static_volume → /app/staticfiles                │
│  • media_volume → /app/media                       │
│  • db.sqlite3 (persisted)                          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Port Mapping

| Port | Service | Direction | Purpose |
|------|---------|-----------|---------|
| **80** | Nginx | ← External Users | HTTP (Redirects to 443) |
| **443** | Nginx | ← External Users | HTTPS (Your App) |
| **8005** | Gunicorn | Internal (Nginx→Django) | Application Server |

## Request Journey

```
Internet User
     │
     ↓
┌─────────────────────────┐
│ app.preqly.com:80       │  (HTTP Request)
└─────────────────────────┘
     │
     ├─ Matches: location / in nginx.conf
     ├─ Returns: 301 redirect to HTTPS
     ↓
┌─────────────────────────┐
│ app.preqly.com:443      │  (HTTPS Request)
└─────────────────────────┘
     │
     ├─ Nginx receives on port 443
     ├─ Verifies SSL certificate (cert.pem, key.pem)
     ├─ Adds security headers:
     │  ├─ Strict-Transport-Security
     │  ├─ X-Frame-Options
     │  ├─ X-Content-Type-Options
     │  └─ X-XSS-Protection
     ├─ Routes to appropriate location block:
     │  ├─ /static/ → Serves from staticfiles volume
     │  ├─ /media/ → Serves from media volume
     │  └─ / → Proxies to Django via proxy_pass
     ↓
┌─────────────────────────┐
│ proxy_pass              │
│ http://django_app:8005  │  (Internal Port)
└─────────────────────────┘
     │
     ├─ Sets X-Forwarded-For header
     ├─ Sets X-Forwarded-Proto header
     ├─ Sets X-Forwarded-Host header
     ↓
┌─────────────────────────┐
│ Gunicorn (Django)       │
│ Port 8005               │  (Worker Process)
└─────────────────────────┘
     │
     ├─ Receives request from Nginx
     ├─ Routes to Django application
     ├─ Processes view
     ├─ Queries database (if needed)
     ├─ Generates response
     ↓
┌─────────────────────────┐
│ Response sent back      │
│ through Nginx           │  (Reverse path)
└─────────────────────────┘
     │
     ├─ Nginx adds Cache-Control headers
     ├─ Compresses with Gzip (if applicable)
     ├─ Logs request
     ↓
Internet User
(Receives encrypted response)
```

## Domain Configuration

### Your Server

```
Your Domain Registrar
     │
     ├─ A Record
     │  └─ app.preqly.com → 123.456.789.012 (Your Server IP)
     │
     └─ CNAME Record (optional)
        └─ www.app.preqly.com → app.preqly.com

Your Server (123.456.789.012)
     │
     ├─ Firewall Rules:
     │  ├─ Port 80 (HTTP) - Open
     │  ├─ Port 443 (HTTPS) - Open
     │  └─ Port 22 (SSH) - Open to your IP only
     │
     └─ Docker Containers:
        ├─ Nginx:80 ← External HTTP traffic
        ├─ Nginx:443 ← External HTTPS traffic
        └─ Django:8005 ← Internal only
```

## SSL/TLS Configuration

### Certificate Files
```
Your Server
   │
   └─ /app/ssl/
      ├─ cert.pem (SSL Certificate)
      │  ├─ Downloaded from Let's Encrypt or CA
      │  ├─ Public certificate
      │  ├─ Contains domain name(s)
      │  └─ Valid for 90 days (Let's Encrypt)
      │
      └─ key.pem (Private Key)
         ├─ Generated on your server
         ├─ Keep secure and private!
         ├─ Required to decrypt HTTPS traffic
         └─ Do NOT share or commit to git
```

### Nginx SSL Configuration (nginx.conf)
```
HTTPS Server Block:
   │
   ├─ listen 443 ssl http2;
   │  └─ Listens on port 443 with SSL
   │
   ├─ ssl_certificate /etc/nginx/ssl/cert.pem;
   │  └─ Path to SSL certificate inside container
   │
   ├─ ssl_certificate_key /etc/nginx/ssl/key.pem;
   │  └─ Path to private key inside container
   │
   ├─ SSL Protocols:
   │  ├─ TLSv1.2 (Older clients)
   │  └─ TLSv1.3 (Modern clients)
   │
   └─ Security Headers:
      ├─ HSTS: Forces HTTPS for 1 year
      ├─ X-Frame-Options: Prevents clickjacking
      ├─ X-Content-Type-Options: Prevents MIME sniffing
      └─ X-XSS-Protection: Prevents XSS attacks

HTTP Server Block (Port 80):
   │
   └─ Redirects ALL traffic to HTTPS
      return 301 https://$server_name$request_uri;
```

## Static & Media File Serving

```
File Request from User
   │
   └─ Request path: /static/css/style.css
      │
      ├─ Nginx location block:
      │  location /static/ {
      │    alias /app/staticfiles/;
      │  }
      │
      └─ Nginx serves directly (No proxy)
         ├─ Fast (filesystem access)
         ├─ Cached (30 days)
         ├─ Compressed (Gzip)
         └─ Does NOT go through Django

File Request from User
   │
   └─ Request path: /media/uploads/image.jpg
      │
      ├─ Nginx location block:
      │  location /media/ {
      │    alias /app/media/;
      │  }
      │
      └─ Nginx serves directly (No proxy)
         ├─ Fast (filesystem access)
         ├─ Cached (7 days)
         ├─ Compressed (Gzip)
         └─ Does NOT go through Django

API Request from User
   │
   └─ Request path: /api/endpoint/
      │
      ├─ Nginx location block:
      │  location / {
      │    proxy_pass http://django_app;
      │  }
      │
      └─ Nginx proxies to Django:8005
         ├─ Sets headers
         ├─ Forwards request
         ├─ Waits for response
         └─ Returns to user
```

## Docker Compose Port Mapping

```yaml
services:
  web:
    ports:
      - "8005:8005"    # Host:Container
                       # External (unused) : Internal (Gunicorn)
                       # Only for development/debugging
                       # In production, only Nginx accesses port 8005

  nginx:
    ports:
      - "80:80"        # HTTP port
      - "443:443"      # HTTPS port
                       # These are exposed to external users
                       # Port 80 redirects to 443
```

## Let's Encrypt Certificate Files

```
Let's Encrypt Server
   │
   └─ After verification:
      │
      └─ /etc/letsencrypt/live/app.preqly.com/
         ├─ cert.pem (or fullchain.pem)
         │  └─ Copy to: ./ssl/cert.pem
         │
         ├─ privkey.pem
         │  └─ Copy to: ./ssl/key.pem
         │
         └─ Auto-renews before expiration
            └─ Add renewal task to cron
```

## Environment Variables (Port Info)

```bash
# In Dockerfile & entrypoint.sh:
EXPOSE 8005                    # Expose port 8005 in image

# In docker-compose.yml:
ports:
  - "8005:8005"              # Publish port for debugging

# In entrypoint.sh:
gunicorn --bind 0.0.0.0:8005  # Bind to port 8005

# In nginx.conf:
upstream django_app {
  server web:8005;           # Reference by service name
}
```

## Production Checklist

```
Port Configuration:
  ✓ Port 80 (HTTP) - Open to internet
  ✓ Port 443 (HTTPS) - Open to internet
  ✓ Port 8005 (Django) - Internal only, not exposed
  ✓ Port 22 (SSH) - Open to your IP only

Domain Configuration:
  ✓ DNS A record: app.preqly.com → server IP
  ✓ DNS CNAME (optional): www.app.preqly.com → app.preqly.com
  ✓ Domain resolves to server

SSL Configuration:
  ✓ SSL certificate obtained (Let's Encrypt or CA)
  ✓ Certificate copied to ./ssl/cert.pem
  ✓ Private key copied to ./ssl/key.pem
  ✓ Permissions: 644 for cert, 600 for key
  ✓ Certificate expires in > 30 days

Docker Configuration:
  ✓ Docker installed and running
  ✓ Docker Compose installed
  ✓ Dockerfile configured correctly
  ✓ docker-compose.yml configured correctly
  ✓ nginx.conf configured correctly
  ✓ entrypoint.sh configured correctly
  ✓ .env.production configured
  ✓ SSL files mounted in volumes

Firewall Rules:
  ✓ Port 80 open (HTTP)
  ✓ Port 443 open (HTTPS)
  ✓ Port 22 restricted (SSH)
  ✓ All other ports closed

Testing:
  ✓ HTTP redirects to HTTPS
  ✓ HTTPS connection works
  ✓ Certificate is valid
  ✓ Static files served correctly
  ✓ API endpoints working
  ✓ Admin panel accessible
```

## Quick Reference

```
External Access:
├─ HTTP: http://app.preqly.com:80 → Redirects to HTTPS
├─ HTTPS: https://app.preqly.com:443 → Your app
└─ Admin: https://app.preqly.com/admin/

Internal Services:
├─ Nginx: Listen on 80 & 443, Proxy to 8005
└─ Django: Listen on 8005, Process requests

Files:
├─ SSL Certificate: ./ssl/cert.pem
├─ SSL Private Key: ./ssl/key.pem
├─ Static Files: ./staticfiles/ (auto-created)
├─ Media Files: ./media/ (auto-created)
└─ Database: ./db.sqlite3 (auto-created)

Docker Compose:
├─ Build: docker-compose build
├─ Start: docker-compose up -d
├─ Logs: docker-compose logs -f
└─ Stop: docker-compose down
```

---

**Your app is ready for production!** 🚀
