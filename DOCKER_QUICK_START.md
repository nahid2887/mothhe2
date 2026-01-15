# Docker & Nginx Deployment - Quick Reference

## 📁 Files Created

```
Dockerfile              # Docker image definition (Python 3.11, Gunicorn)
docker-compose.yml      # Multi-container setup (Django + Nginx)
nginx.conf             # Nginx reverse proxy with SSL/TLS
entrypoint.sh          # Auto-runs migrations & starts app
.dockerignore          # Excludes unnecessary files from build
.env.production        # Production environment config
ssl/                   # SSL certificates directory
deploy.sh              # Linux/Mac deployment script
deploy.bat             # Windows deployment script
DOCKER_DEPLOYMENT_GUIDE.md  # Detailed guide
```

## 🚀 Quick Start

### Linux/Mac:
```bash
chmod +x deploy.sh
./deploy.sh
```

### Windows:
```cmd
deploy.bat
```

## 📋 Manual Steps

### 1. Build Docker Image
```bash
docker-compose build
```

### 2. Generate SSL Certificates (Choose one)

**Option A: Let's Encrypt (Recommended)**
```bash
sudo certbot certonly --standalone -d app.preqly.com
sudo cp /etc/letsencrypt/live/app.preqly.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/app.preqly.com/privkey.pem ssl/key.pem
```

**Option B: Self-signed (Testing)**
```bash
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -nodes -out ssl/cert.pem -keyout ssl/key.pem -days 365
```

### 3. Start Application
```bash
docker-compose up -d
```

### 4. Verify Running
```bash
docker-compose ps
docker-compose logs -f web
```

## ✨ Features

✅ **Port 8005** - Django Gunicorn server  
✅ **Auto Migrations** - Runs on container startup  
✅ **Nginx Reverse Proxy** - SSL/TLS termination  
✅ **Static Files** - Served by Nginx at `/static/`  
✅ **Media Files** - Served by Nginx at `/media/`  
✅ **Health Checks** - Container monitoring  
✅ **Logging** - Full request/error logging  
✅ **Security Headers** - HSTS, X-Frame-Options, etc.  
✅ **Gzip Compression** - Automatic response compression  
✅ **Volume Persistence** - Database survives restarts  

## 🔐 Configuration

Edit `.env.production`:
```env
DEBUG=False
ALLOWED_HOSTS=app.preqly.com,www.app.preqly.com,localhost
SECRET_KEY=your-secure-random-key-here
```

## 📊 Gunicorn Workers

Current: **4 workers**  
Formula: `(2 × CPU cores) + 1`

For 8 CPU cores: use 17 workers
Edit `entrypoint.sh`:
```bash
gunicorn core.wsgi:application \
    --bind 0.0.0.0:8005 \
    --workers 17
```

## 🛠️ Common Commands

```bash
# View logs
docker-compose logs -f web
docker-compose logs -f nginx

# Execute commands
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput

# Restart services
docker-compose restart web
docker-compose restart nginx

# Stop all
docker-compose down

# Rebuild & restart
docker-compose up -d --build
```

## 📍 Domain Setup

1. Point DNS to your server IP:
   - `app.preqly.com` → your-server-ip
   - `www.app.preqly.com` → your-server-ip

2. Wait for DNS propagation (5-48 hours)

3. Get SSL certificate (Let's Encrypt recommended)

4. Access at: `https://app.preqly.com`

## 🔄 Auto-Migration Flow

When container starts:
1. ✅ Runs `python manage.py migrate`
2. ✅ Runs `python manage.py collectstatic`
3. ✅ Starts Gunicorn on port 8005
4. ✅ Nginx proxies requests from port 80/443

## 📦 Ports

- **80**: HTTP (Nginx - redirects to HTTPS)
- **443**: HTTPS (Nginx - your app)
- **8005**: Django Gunicorn (internal, not exposed)

## 🗄️ Database Options

**Current: SQLite** (db.sqlite3)
- Good for: Small apps, testing
- File is persisted via Docker volume

**Recommended for production: PostgreSQL**
See DOCKER_DEPLOYMENT_GUIDE.md for PostgreSQL setup

## 🔄 Updating Your App

```bash
# 1. Pull latest code
git pull

# 2. Rebuild & restart
docker-compose up -d --build

# 3. Run migrations
docker-compose exec web python manage.py migrate
```

## 🔍 Troubleshooting

**App not accessible**
```bash
docker-compose ps  # Check if containers are running
docker-compose logs -f  # View error logs
```

**Migrations not running**
```bash
docker-compose exec web python manage.py migrate --noinput
```

**Static files not showing**
```bash
docker-compose exec web python manage.py collectstatic --noinput
docker-compose restart nginx
```

**Port in use**
- Change host port in `docker-compose.yml`
- Restart: `docker-compose restart`

## 🛡️ Security Checklist

- [ ] Generate new SECRET_KEY for production
- [ ] Set DEBUG=False
- [ ] Install SSL certificate
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable CSRF protection
- [ ] Configure CORS properly
- [ ] Backup db.sqlite3 regularly
- [ ] Keep Docker images updated
- [ ] Use strong admin passwords
- [ ] Monitor logs regularly

## 📚 Documentation

- Full guide: See `DOCKER_DEPLOYMENT_GUIDE.md`
- Nginx config: See `nginx.conf`
- Dockerfile: See `Dockerfile`
- Startup script: See `entrypoint.sh`
- Docker Compose: See `docker-compose.yml`

## 💡 Tips

- Use `--build` flag to rebuild: `docker-compose up -d --build`
- Use `-f` flag to follow logs: `docker-compose logs -f`
- Use `-e` flag to stop on error: `set -e` in entrypoint.sh
- Use volumes for persistence: SQLite file, static files, media files
- Use networks for container communication: app_network

## 🎯 Next Steps

1. ✅ Files are created
2. ⏳ Generate SSL certificates
3. ⏳ Configure DNS
4. ⏳ Run `docker-compose up -d --build`
5. ⏳ Access at `https://app.preqly.com`

---

**Ready to deploy?** Start with: `docker-compose up -d --build`
