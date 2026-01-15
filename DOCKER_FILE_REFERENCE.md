# 🐳 Docker Deployment - Complete File Reference

## 📑 Quick Navigation

### 🚀 Start Here
1. **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Overview & architecture
2. **[DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)** - Step-by-step quick start
3. **[DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md)** - Detailed guide

### 🛠️ Configuration Files
- **[Dockerfile](Dockerfile)** - Docker image definition
- **[docker-compose.yml](docker-compose.yml)** - Container orchestration
- **[nginx.conf](nginx.conf)** - Web server & reverse proxy
- **[entrypoint.sh](entrypoint.sh)** - Container startup & migrations
- **[.env.production](.env.production)** - Production environment
- **[.dockerignore](.dockerignore)** - Files to exclude from build

### 📁 Directories
- **[ssl/](ssl/)** - SSL certificates (you provide these)
- **[static/](static/)** - Static files (created by Django)

### 🔧 Helper Scripts
- **[deploy.sh](deploy.sh)** - Linux/Mac deployment
- **[deploy.bat](deploy.bat)** - Windows deployment
- **[health-check.sh](health-check.sh)** - Monitoring & diagnostics
- **[production-checklist.sh](production-checklist.sh)** - Pre-deployment checklist

---

## 📊 File Descriptions

### Core Docker Files

#### Dockerfile
**What it does:** Defines the Docker image
- Uses Python 3.11 slim image
- Installs system dependencies
- Installs Python packages from requirements.txt
- Installs Gunicorn
- Exposes port 8005
- Runs entrypoint.sh on startup

**Key features:**
- Minimal, optimized image
- Production-ready
- Security best practices

#### docker-compose.yml
**What it does:** Orchestrates multiple containers
- Django web service (Gunicorn on port 8005)
- Nginx service (reverse proxy on ports 80/443)
- Volumes for persistence (staticfiles, media, database)
- Networks for container communication
- Environment variables
- Auto-restart policy

**Services:**
```
web: Django Gunicorn server
nginx: Reverse proxy with SSL/TLS
```

#### nginx.conf
**What it does:** Web server configuration
- HTTP to HTTPS redirect
- SSL/TLS termination
- Reverse proxy to Django
- Static file serving (/static/)
- Media file serving (/media/)
- Gzip compression
- Security headers (HSTS, X-Frame-Options, etc.)
- Request logging

#### entrypoint.sh
**What it does:** Runs on container startup
1. Runs migrations: `python manage.py migrate`
2. Collects static files: `python manage.py collectstatic`
3. Starts Gunicorn: `gunicorn core.wsgi:application`

**Configuration:**
```bash
--bind 0.0.0.0:8005        # Listen on port 8005
--workers 4                 # 4 worker processes
--worker-class sync        # Sync workers
```

---

### Configuration Files

#### .env.production
**What it does:** Production environment variables

**Variables:**
- `DEBUG=False` - Disable debug mode
- `ALLOWED_HOSTS` - Allowed domain names
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - Database connection (SQLite)

#### .dockerignore
**What it does:** Excludes files from Docker build

**Excluded:**
- Python cache files (__pycache__, *.pyc)
- Virtual environments
- Database files
- .git directory
- .env files
- Documentation (*.md)

#### requirements.txt
**What it does:** Python package list

**Added for deployment:**
- `gunicorn==21.2.0` - Application server
- `whitenoise==6.6.0` - Static file serving

---

### SSL Directory

#### ssl/cert.pem
- Your SSL certificate
- Get from Let's Encrypt or purchase from CA
- Path: `ssl/cert.pem`

#### ssl/key.pem
- Your SSL private key
- Keep secure!
- Path: `ssl/key.pem`

#### ssl/README.md
- Instructions for obtaining certificates

---

### Helper Scripts

#### deploy.sh (Linux/Mac)
**What it does:** Automated deployment setup
1. Checks Docker installation
2. Checks Docker Compose installation
3. Builds Docker image
4. Prints next steps

**Run with:**
```bash
chmod +x deploy.sh
./deploy.sh
```

#### deploy.bat (Windows)
**What it does:** Same as deploy.sh but for Windows

**Run with:**
```cmd
deploy.bat
```

#### health-check.sh
**What it does:** Monitor container health & status
- Check if containers running
- View resource usage
- View recent logs
- Check database
- Check SSL certificates
- List running users
- Show quick commands

**Run with:**
```bash
chmod +x health-check.sh
./health-check.sh
```

#### production-checklist.sh
**What it does:** Pre-deployment verification
- Verify Docker installed
- Verify SSL certificates
- Verify configuration
- Show deployment steps
- Show security checklist
- Show maintenance tasks

**Run with:**
```bash
chmod +x production-checklist.sh
./production-checklist.sh
```

---

### Documentation Files

#### DEPLOYMENT_SUMMARY.md
**What it does:** High-level overview
- What's been created
- Quick start (4 steps)
- Architecture diagram
- Security features
- Performance stats
- Useful commands
- Port configuration
- Database info
- Update procedures

#### DOCKER_QUICK_START.md
**What it does:** Quick reference guide
- File structure overview
- Quick start commands
- Configuration details
- Common commands
- Domain setup
- Troubleshooting

#### DOCKER_DEPLOYMENT_GUIDE.md
**What it does:** Comprehensive deployment guide
- Detailed instructions
- Let's Encrypt setup
- Self-signed certificates
- Database options
- PostgreSQL setup
- Common issues
- Monitoring
- Performance tuning
- Security checklist
- Backup/restore
- Update procedures

---

## 🚀 Deployment Flow

```
1. Build Phase
   ├── Dockerfile creates image
   ├── Installs Python 3.11
   ├── Installs dependencies
   └── Configures for port 8005

2. Start Phase (docker-compose up)
   ├── web service starts
   │  ├── Runs entrypoint.sh
   │  ├── Runs migrations
   │  ├── Collects static files
   │  └── Starts Gunicorn on 8005
   └── nginx service starts
      ├── Loads nginx.conf
      ├── Listens on 80 & 443
      └── Proxies to port 8005

3. Request Flow
   ├── User: https://app.preqly.com
   ├── Nginx: Receives on 443
   ├── Nginx: Verifies SSL
   ├── Nginx: Adds headers
   ├── Nginx: Proxies to web:8005
   ├── Django: Processes request
   ├── Django: Returns response
   ├── Nginx: Sends to user
   └── User: Receives encrypted response
```

---

## 🔄 Container Architecture

```
┌─────────────────────────────────────┐
│      Docker Compose Network         │
│         (app_network)               │
│                                     │
│  ┌──────────────┐  ┌────────────┐  │
│  │    Nginx     │  │    Web     │  │
│  │ Container    │  │ Container  │  │
│  │              │  │            │  │
│  │ Ports:       │  │ Port:      │  │
│  │ 80 (HTTP)    │  │ 8005       │  │
│  │ 443 (HTTPS)  │  │ (Internal) │  │
│  │              │  │            │  │
│  │ TLS/SSL      │  │ Gunicorn   │  │
│  │ Reverse      │  │ Django     │  │
│  │ Proxy        │  │ Migrations │  │
│  │              │  │            │  │
│  │ Static Serving           │  │
│  │ Compression  │  │ WSGI App   │  │
│  │ Logging      │  │            │  │
│  └──────────────┘  └────────────┘  │
│         ↑                  ↓        │
│         └──────────────────┘        │
│                                     │
│  Volumes: (Persistence)            │
│  • static_volume (staticfiles)      │
│  • media_volume (media files)       │
│  • db.sqlite3 (database)            │
│                                     │
└─────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│    External Network (Internet)       │
│                                      │
│  HTTP (Port 80) → Redirect to HTTPS  │
│  HTTPS (Port 443) → Your App         │
│                                      │
│  app.preqly.com                      │
│  www.app.preqly.com                  │
└──────────────────────────────────────┘
```

---

## 📋 Command Reference

### Build & Deploy
```bash
docker-compose build              # Build image
docker-compose up -d              # Start services
docker-compose up -d --build      # Rebuild & start
docker-compose down               # Stop services
docker-compose restart            # Restart services
```

### View Status
```bash
docker-compose ps                 # List containers
docker-compose logs -f            # View logs
docker-compose logs -f web        # Django logs
docker-compose logs -f nginx      # Nginx logs
docker stats                       # Resource usage
```

### Execute Commands
```bash
# Database
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Static files
docker-compose exec web python manage.py collectstatic

# Django shell
docker-compose exec web python manage.py shell

# Backup
docker-compose exec web python manage.py dumpdata > backup.json
```

### Maintenance
```bash
# Restart specific service
docker-compose restart web
docker-compose restart nginx

# Remove everything
docker-compose down -v

# Rebuild specific service
docker-compose build web

# Clean up unused resources
docker system prune
```

---

## 🔐 Security Configuration

### SSL/TLS
- HTTPS on port 443
- HTTP redirect to HTTPS
- TLS 1.2 and 1.3
- Strong ciphers

### Security Headers
- HSTS (Strict-Transport-Security)
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Referrer-Policy

### Django Security
- DEBUG=False
- CSRF protection enabled
- CORS configured
- Secret key (long random string)

### Best Practices
- Regular backups
- Log monitoring
- Security updates
- Strong passwords
- Certificate renewal

---

## 🎯 Deployment Checklist

- [ ] SSL certificates obtained
- [ ] Domain DNS configured
- [ ] .env.production updated
- [ ] SECRET_KEY generated
- [ ] Requirements.txt reviewed
- [ ] Dockerfile reviewed
- [ ] docker-compose.yml reviewed
- [ ] nginx.conf reviewed
- [ ] entrypoint.sh reviewed
- [ ] Firewall ports opened (80, 443)
- [ ] Docker & Docker Compose installed
- [ ] Health check passes
- [ ] App accessible at domain

---

## 🆘 Support Resources

### Documentation
- [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) - Start here
- [DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md) - Detailed guide
- [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) - Overview

### Helpful Commands
```bash
# Check everything
./health-check.sh

# Pre-deployment
./production-checklist.sh

# Quick start
./deploy.sh

# View docs
cat DOCKER_QUICK_START.md
```

### Troubleshooting
- Check logs: `docker-compose logs -f`
- Check containers: `docker-compose ps`
- Check resources: `docker stats`
- Check SSL: `docker-compose logs nginx`

---

## 🎉 You're Ready!

Your Django application is fully configured for Docker deployment to app.preqly.com

**Next Steps:**
1. Generate SSL certificates
2. Configure DNS
3. Run: `docker-compose up -d --build`
4. Access: `https://app.preqly.com`

**Questions?** Check the documentation files or review the configuration files directly.

---

**Last Updated:** January 15, 2026
**Docker Image:** Python 3.11 + Gunicorn
**Port:** 8005
**Domain:** app.preqly.com
