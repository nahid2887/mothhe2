# Docker Deployment Guide for app.preqly.com

## Quick Start

### 1. Prerequisites
- Docker & Docker Compose installed
- Domain app.preqly.com configured with DNS pointing to your server
- SSL certificates (or use Let's Encrypt)

### 2. Build and Run

```bash
# Build and start containers
docker-compose up -d --build

# View logs
docker-compose logs -f web

# Stop containers
docker-compose down

# Restart containers
docker-compose restart
```

### 3. Run Migrations Manually (if needed)

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 4. Access the Application

- Application: https://app.preqly.com
- Admin Panel: https://app.preqly.com/admin/

## Configuration

### Environment Variables
Edit `.env.production` to configure:
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: List of allowed domains
- `SECRET_KEY`: Django secret key (generate a new one!)

### SSL Certificates

#### Option A: Using Let's Encrypt (Recommended)

1. Install Certbot:
```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. Generate certificates:
```bash
sudo certbot certonly --standalone -d app.preqly.com -d www.app.preqly.com
```

3. Copy to ssl directory:
```bash
mkdir -p ssl
sudo cp /etc/letsencrypt/live/app.preqly.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/app.preqly.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*
```

4. Auto-renewal with cron:
```bash
# Edit crontab
sudo crontab -e

# Add: 0 3 * * * certbot renew --post-hook "docker-compose -f /path/to/docker-compose.yml restart nginx"
```

#### Option B: Self-signed Certificate (Development Only)

```bash
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -nodes -out ssl/cert.pem -keyout ssl/key.pem -days 365
```

## Project Structure

```
.
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Multi-container orchestration
├── nginx.conf          # Nginx reverse proxy config
├── entrypoint.sh       # Auto-migration & startup script
├── .dockerignore       # Files to exclude from build
├── .env.production     # Production environment variables
└── manage.py           # Django management
```

## Database

### SQLite (Current Setup)
- Database file: `db.sqlite3`
- Persisted via Docker volumes
- Suitable for small apps

### PostgreSQL (Recommended for Production)

To use PostgreSQL instead:

1. Update `docker-compose.yml`:
```yaml
  db:
    image: postgres:15
    container_name: postgres_db
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app_network

  web:
    # ... existing config ...
    environment:
      - DATABASE_URL=postgresql://myuser:mypassword@db:5432/myapp
    depends_on:
      - db
```

2. Update `requirements.txt`:
```
psycopg2-binary==2.9.9
```

3. Update `core/settings.py`:
```python
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://user:password@localhost/dbname',
        conn_max_age=600
    )
}
```

## Common Issues

### 1. Migrations not running
- Check logs: `docker-compose logs web`
- Manual migration: `docker-compose exec web python manage.py migrate`

### 2. Static files not showing
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### 3. Permission denied
```bash
sudo chown -R $USER:$USER .
sudo chmod -R 755 .
```

### 4. Port already in use
Change port in `docker-compose.yml`:
```yaml
ports:
  - "8005:8005"  # Change first number to different port
```

## Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx
```

### Container Status
```bash
docker-compose ps
```

### Restart Services
```bash
docker-compose restart web
docker-compose restart nginx
```

## Performance Tuning

### Gunicorn Workers
Edit `entrypoint.sh`:
```bash
gunicorn core.wsgi:application \
    --bind 0.0.0.0:8005 \
    --workers 8 \
    --worker-class sync
```

Formula: `workers = (2 × CPU cores) + 1`

### Nginx Caching
Add to `nginx.conf`:
```nginx
location /api/ {
    proxy_cache_valid 200 10m;
    proxy_cache_key "$scheme$request_method$host$request_uri";
}
```

## Security Checklist

- [ ] Generate new SECRET_KEY for production
- [ ] Set DEBUG=False
- [ ] Configure SSL certificates
- [ ] Set secure ALLOWED_HOSTS
- [ ] Use strong database password
- [ ] Enable CSRF protection
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Regular backups of db.sqlite3
- [ ] Keep Docker images updated

## Backup & Restore

### Backup Database
```bash
docker-compose exec -T web python manage.py dumpdata > backup.json
cp db.sqlite3 db.sqlite3.backup
```

### Restore Database
```bash
docker-compose exec web python manage.py loaddata backup.json
```

## Update Application

1. Pull latest code
2. Rebuild image:
```bash
docker-compose up -d --build
```

3. Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

4. Restart:
```bash
docker-compose restart
```

## Support

For issues, check:
1. Docker logs: `docker-compose logs -f`
2. Django logs in container
3. Nginx error logs: `docker-compose logs nginx`
4. Django debug page (if DEBUG=True)
