# 🎯 Docker Deployment - Visual Architecture & Guides

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERNET (USERS)                         │
└─────────────────────────────────────────────────────────────────┘
                             ↓
                      app.preqly.com
                             ↓
        ┌────────────────────┴────────────────────┐
        ↓                                          ↓
   HTTP (Port 80)                         HTTPS (Port 443)
   Redirect to HTTPS                      SSL/TLS Encrypted
        │                                         │
        └─────────────────┬──────────────────────┘
                         ↓
         ┌───────────────────────────────────┐
         │      NGINX Reverse Proxy          │
         │      (Nginx Docker Container)     │
         │                                   │
         │  • SSL/TLS Termination           │
         │  • Security Headers              │
         │  • Request Routing               │
         │  • Static File Serving (/static/)|
         │  • Media File Serving (/media/)  │
         │  • Request Logging               │
         │  • Gzip Compression              │
         │  • Load Balancing                │
         └───────────────────┬───────────────┘
                             │
                    (Port 8005 - Internal)
                             │
         ┌───────────────────────────────────┐
         │     DJANGO Application Server     │
         │    (Gunicorn Docker Container)    │
         │                                   │
         │  • Python 3.11                   │
         │  • Gunicorn WSGI Server          │
         │  • 4 Worker Processes            │
         │  • Auto Database Migrations      │
         │  • Static File Collection        │
         │  • Request Processing            │
         │  • Business Logic                │
         └───────────────────┬───────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │     PERSISTENT VOLUMES (Storage)       │
        │                                        │
        │  • db.sqlite3 (Database)              │
        │  • /staticfiles/ (Static Files)       │
        │  • /media/ (User Uploads)             │
        └────────────────────────────────────────┘
```

## Request Flow Sequence

```
1. User Types URL
   https://app.preqly.com
        ↓
2. DNS Lookup
   app.preqly.com → 123.456.789.012 (Your Server IP)
        ↓
3. TCP Connection
   Connect to port 443 (HTTPS)
        ↓
4. SSL/TLS Handshake
   • Browser receives certificate (cert.pem)
   • Verifies certificate validity
   • Verifies domain name
   • Establishes encrypted connection
        ↓
5. Nginx Receives Request (Port 443)
   • Decrypts using private key (key.pem)
   • Parses HTTP request
   • Adds security headers
   • Routes based on URL path:
        │
        ├─ /static/* → Serve static files (Nginx)
        ├─ /media/*  → Serve media files (Nginx)
        └─ /*        → Proxy to Django (Port 8005)
        ↓
6. Django Application (Port 8005)
   • Receives request from Nginx
   • Routes to appropriate view/API
   • Processes business logic
   • Queries database (if needed)
   • Generates response
        ↓
7. Response Sent Back
   Django → Nginx → Encrypt → Browser
        ↓
8. Browser Receives Response
   • Decrypts encrypted content
   • Renders page or displays data
   • Loads static files (JS, CSS, images)
```

## File Organization

```
Your Project Directory
│
├── 📦 DOCKER CORE
│   ├── Dockerfile              ← Defines container image
│   ├── docker-compose.yml      ← Orchestrates containers
│   ├── entrypoint.sh           ← Startup script
│   └── .dockerignore           ← Build exclusions
│
├── 🌐 WEB SERVER
│   └── nginx.conf              ← Nginx configuration
│
├── ⚙️ CONFIGURATION
│   ├── .env.production         ← Production environment
│   └── requirements.txt        ← Python dependencies
│
├── 🔐 SSL/TLS
│   └── ssl/
│       ├── cert.pem            ← SSL certificate
│       ├── key.pem             ← Private key
│       └── README.md           ← Certificate instructions
│
├── 🔧 DEPLOYMENT SCRIPTS
│   ├── deploy.sh               ← Linux/Mac setup
│   ├── deploy.bat              ← Windows setup
│   ├── health-check.sh         ← Monitoring
│   └── production-checklist.sh ← Pre-deployment
│
├── 📚 DOCUMENTATION
│   ├── DEPLOYMENT_SUMMARY.md           ← Overview
│   ├── DOCKER_QUICK_START.md          ← Quick reference
│   ├── PORT_DOMAIN_GUIDE.md           ← Ports & domains
│   ├── DOCKER_DEPLOYMENT_GUIDE.md     ← Detailed guide
│   ├── DOCKER_FILE_REFERENCE.md       ← File descriptions
│   ├── DEPLOYMENT_COMPLETE.md         ← This summary
│   └── (This file)
│
└── 🐍 DJANGO PROJECT
    ├── manage.py               ← Django management
    ├── db.sqlite3             ← Database (auto-created)
    ├── staticfiles/            ← Static files (auto-created)
    ├── media/                  ← Media uploads (auto-created)
    ├── account/                ← Django app
    └── core/                   ← Django settings
```

## Deployment Step-by-Step

```
STEP 1: Generate SSL Certificates
┌──────────────────────────────────────────────────────┐
│ Certificate from Let's Encrypt or your CA            │
│ • cert.pem (public certificate)                      │
│ • key.pem (private key - keep secure!)              │
│ • Place in: ./ssl/ directory                         │
└──────────────────────────────────────────────────────┘
         ↓
STEP 2: Configure DNS
┌──────────────────────────────────────────────────────┐
│ A Record: app.preqly.com → your-server-ip            │
│ CNAME (optional): www.app.preqly.com → app.preqly.com
│ Wait for DNS propagation (5-48 hours)                │
└──────────────────────────────────────────────────────┘
         ↓
STEP 3: Configure Environment
┌──────────────────────────────────────────────────────┐
│ Edit .env.production:                                 │
│ • DEBUG=False                                         │
│ • SECRET_KEY=your-long-random-key                    │
│ • ALLOWED_HOSTS=app.preqly.com,www.app.preqly.com   │
└──────────────────────────────────────────────────────┘
         ↓
STEP 4: Build Docker Image
┌──────────────────────────────────────────────────────┐
│ $ docker-compose build                               │
│ • Builds image from Dockerfile                       │
│ • Installs Python 3.11                               │
│ • Installs dependencies (requirements.txt)           │
│ • Prepares Gunicorn & Nginx                          │
└──────────────────────────────────────────────────────┘
         ↓
STEP 5: Start Containers
┌──────────────────────────────────────────────────────┐
│ $ docker-compose up -d                               │
│ • Starts Nginx container (ports 80/443)              │
│ • Starts Django container (port 8005)                │
│ • Runs entrypoint.sh on Django startup:              │
│   - Runs migrations                                   │
│   - Collects static files                            │
│   - Starts Gunicorn                                  │
└──────────────────────────────────────────────────────┘
         ↓
STEP 6: Verify Deployment
┌──────────────────────────────────────────────────────┐
│ $ docker-compose logs -f                             │
│ • Check for errors                                    │
│ • Wait for "Gunicorn started"                        │
│ • Visit: https://app.preqly.com                      │
└──────────────────────────────────────────────────────┘
         ↓
STEP 7: Create Admin User
┌──────────────────────────────────────────────────────┐
│ $ docker-compose exec web python manage.py createsuperuser
│ • Create username, email, password                   │
│ • Access admin: https://app.preqly.com/admin/        │
└──────────────────────────────────────────────────────┘
         ↓
STEP 8: Monitor & Maintain
┌──────────────────────────────────────────────────────┐
│ • Check logs: docker-compose logs -f                 │
│ • Monitor: docker stats                              │
│ • Backup: docker-compose exec web python manage.py dumpdata > backup.json
│ • Update: docker-compose up -d --build               │
└──────────────────────────────────────────────────────┘
```

## Container Communication

```
┌─────────────────────────────────────────────┐
│         Docker Compose Network              │
│            (app_network)                    │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │        Nginx Container               │  │
│  │  Service Name: nginx                 │  │
│  │  Hostname: nginx                     │  │
│  │                                      │  │
│  │  Listens:                            │  │
│  │  • 0.0.0.0:80 (HTTP)                │  │
│  │  • 0.0.0.0:443 (HTTPS)              │  │
│  │                                      │  │
│  │  Proxies to: web:8005               │  │
│  │  (Using service name as hostname)    │  │
│  └──────────┬───────────────────────────┘  │
│             │                              │
│             │ (Uses service name "web"    │
│             │  to connect inside network) │
│             │                              │
│  ┌──────────▼───────────────────────────┐  │
│  │       Django Container               │  │
│  │  Service Name: web                   │  │
│  │  Hostname: web                       │  │
│  │                                      │  │
│  │  Listens:                            │  │
│  │  • 0.0.0.0:8005 (Gunicorn)          │  │
│  │                                      │  │
│  │  External access: NOT exposed        │  │
│  │  (Only accessible via Nginx proxy)   │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  Docker DNS Resolution:                    │
│  • web → 172.x.x.x (Django container)     │
│  • nginx → 172.x.x.x (Nginx container)    │
│                                             │
└─────────────────────────────────────────────┘
```

## Security Layers

```
Layer 1: SSL/TLS Encryption
┌─────────────────────────────────────┐
│ HTTPS (Port 443)                    │
│ • Certificate: cert.pem             │
│ • Private Key: key.pem              │
│ • Encrypts all traffic              │
│ • Prevents man-in-the-middle        │
└─────────────────────────────────────┘
         ↓
Layer 2: HTTP Security Headers
┌─────────────────────────────────────┐
│ Added by Nginx:                     │
│ • HSTS (1 year)                     │
│ • X-Frame-Options                   │
│ • X-Content-Type-Options            │
│ • X-XSS-Protection                  │
│ • Referrer-Policy                   │
└─────────────────────────────────────┘
         ↓
Layer 3: Django Security
┌─────────────────────────────────────┐
│ Django Features:                    │
│ • CSRF Protection                   │
│ • SQL Injection Prevention           │
│ • XSS Prevention                     │
│ • Authentication & Authorization    │
│ • Password Hashing                  │
└─────────────────────────────────────┘
         ↓
Layer 4: Network Isolation
┌─────────────────────────────────────┐
│ Docker Features:                    │
│ • Private Network (app_network)     │
│ • Container Isolation               │
│ • Port Binding Control              │
│ • Volume Isolation                  │
└─────────────────────────────────────┘
         ↓
Layer 5: Firewall Rules
┌─────────────────────────────────────┐
│ Server Firewall:                    │
│ • Port 80: OPEN (HTTP)              │
│ • Port 443: OPEN (HTTPS)            │
│ • Port 22: RESTRICTED (SSH)         │
│ • All others: CLOSED                │
└─────────────────────────────────────┘
```

## Volume Persistence

```
┌──────────────────────────────────┐
│     Docker Volumes               │
│    (Data Persists!)              │
│                                  │
│  static_volume                   │
│  ├─ /app/staticfiles             │
│  ├─ CSS, JS, Images              │
│  └─ Created by: collectstatic    │
│                                  │
│  media_volume                    │
│  ├─ /app/media                   │
│  ├─ User Uploads                 │
│  └─ Created by: Django           │
│                                  │
│  db.sqlite3                      │
│  ├─ Database File                │
│  ├─ Tables, Data                 │
│  └─ Persists Between Restarts    │
│                                  │
│  Mounted on Host System:         │
│  • Survives container restart    │
│  • Survives container rebuild    │
│  • Accessible on host for backup │
│                                  │
└──────────────────────────────────┘
```

## Performance Optimization

```
Gunicorn Workers (Concurrency)
│
├─ Worker 1 ─ Handles Request 1
├─ Worker 2 ─ Handles Request 2
├─ Worker 3 ─ Handles Request 3
├─ Worker 4 ─ Handles Request 4
└─ (Configurable in entrypoint.sh)

Formula: (2 × CPU_CORES) + 1
Example: 8 CPUs = 17 workers

Nginx Caching
│
├─ Static Files
│  ├─ Cache Control: 30 days
│  ├─ Served directly
│  └─ Browser caches locally
│
└─ Responses
   ├─ Varies by endpoint
   ├─ Default: 10 minutes
   └─ Reduces server load

Gzip Compression
│
├─ Compresses responses
├─ Reduces bandwidth
├─ Browser decompresses automatically
└─ Typical 70% size reduction

Request Flow Optimization
│
├─ Static Files → Nginx (No Django)
├─ API Requests → Django (Processed)
├─ Media Files → Nginx (No Django)
└─ All Paths → Https (Encrypted)
```

## Common Tasks

```
📊 MONITORING
│
├─ View logs: docker-compose logs -f
├─ Specific logs: docker-compose logs -f web
├─ Resource usage: docker stats
├─ Container status: docker-compose ps
└─ Health check: ./health-check.sh

🔧 MAINTENANCE
│
├─ Create superuser: docker-compose exec web python manage.py createsuperuser
├─ Migrations: docker-compose exec web python manage.py migrate
├─ Collect static: docker-compose exec web python manage.py collectstatic
├─ Django shell: docker-compose exec web python manage.py shell
└─ Backup database: docker-compose exec web python manage.py dumpdata > backup.json

🔄 UPDATES
│
├─ Rebuild: docker-compose build
├─ Restart: docker-compose restart
├─ Full restart: docker-compose up -d --build
├─ Pull latest: git pull
└─ Run migrations: docker-compose exec web python manage.py migrate

🛑 STOPPING
│
├─ Stop all: docker-compose stop
├─ Stop specific: docker-compose stop web
├─ Down (remove): docker-compose down
├─ Down with volumes: docker-compose down -v
└─ Hard stop: docker-compose kill

🧹 CLEANUP
│
├─ Remove images: docker rmi image_name
├─ Remove containers: docker rm container_name
├─ Prune system: docker system prune
├─ Prune volumes: docker volume prune
└─ View all: docker ps -a
```

## 📞 Support Resources

```
Documentation Files
├─ DEPLOYMENT_SUMMARY.md ..................... Overview (Read First!)
├─ DOCKER_QUICK_START.md ................... Quick Commands
├─ PORT_DOMAIN_GUIDE.md .................... Ports & Domains
├─ DOCKER_DEPLOYMENT_GUIDE.md ............ Detailed Instructions
├─ DOCKER_FILE_REFERENCE.md .............. File Descriptions
└─ DOCKER_VISUAL_GUIDE.md ................. This File!

Configuration Files
├─ Dockerfile .......................... Image Definition
├─ docker-compose.yml ................. Containers
├─ nginx.conf ......................... Web Server
├─ entrypoint.sh ...................... Startup Script
├─ .env.production .................... Environment
└─ requirements.txt ................... Dependencies

Helper Scripts
├─ deploy.sh .......................... Linux Setup
├─ deploy.bat ......................... Windows Setup
├─ health-check.sh .................... Monitoring
└─ production-checklist.sh ............ Verification
```

---

**Ready to deploy?** Start with the DEPLOYMENT_SUMMARY.md file! 🚀
