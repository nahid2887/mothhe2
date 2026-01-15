# 🐘 PostgreSQL + Docker + Django - Quick Setup

## What Changed

Your deployment now includes **PostgreSQL 15** as a Docker service alongside your Django application.

✅ PostgreSQL runs in its own container
✅ Data persists in Docker volumes
✅ Automatic health checks
✅ Django auto-migration support
✅ Easy backup/restore

---

## 🚀 Deploy with PostgreSQL (3 Steps)

### Step 1: Create `.env` File

Create a file named `.env` in your project root:

```env
DB_NAME=app_db
DB_USER=app_user
DB_PASSWORD=secure_password_change_me_12345
DEBUG=False
ALLOWED_HOSTS=app.preqly.com,localhost
SECRET_KEY=django-insecure-your-random-50-char-key-here
```

**Important:** Add `.env` to `.gitignore`
```bash
echo ".env" >> .gitignore
```

### Step 2: Build & Deploy

```bash
# Build Docker image
docker-compose build

# Start all containers (PostgreSQL + Django + Nginx)
docker-compose up -d

# Wait a moment for database to initialize
sleep 5

# View logs
docker-compose logs -f

# When you see "Gunicorn started successfully", you're good!
```

### Step 3: Access Your App

```
https://app.preqly.com
Admin: https://app.preqly.com/admin/
```

Create admin user:
```bash
docker-compose exec web python manage.py createsuperuser
```

---

## 🗄️ Database Architecture

```
┌─────────────────────────────────┐
│      Docker Compose Network     │
│                                 │
│  ┌──────────────┐   ┌────────┐ │
│  │ PostgreSQL   │   │ Django │ │
│  │   Port 5432  │───│ Port   │ │
│  │              │   │ 8005   │ │
│  │ Persistent   │   │        │ │
│  │ Volume       │   │        │ │
│  └──────────────┘   └────────┘ │
│                                 │
└─────────────────────────────────┘
         ↓
    Nginx (80/443)
         ↓
   Internet Users
```

---

## 📊 Services in docker-compose.yml

### PostgreSQL Service
```yaml
db:
  image: postgres:15
  environment:
    POSTGRES_DB: app_db
    POSTGRES_USER: app_user
    POSTGRES_PASSWORD: secure_password_change_me_12345
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

### Django Service
```yaml
web:
  depends_on:
    db:
      condition: service_healthy
  environment:
    DATABASE_URL=postgresql://app_user:secure_password_change_me_12345@db:5432/app_db
```

The `depends_on` with `service_healthy` ensures:
1. PostgreSQL starts first
2. Health check passes
3. Then Django starts and runs migrations

---

## 🔧 Common Commands

### Database Management

```bash
# Connect to PostgreSQL CLI
docker-compose exec db psql -U app_user -d app_db

# Backup database
docker-compose exec db pg_dump -U app_user -d app_db > backup.sql

# Restore database
docker-compose exec -T db psql -U app_user -d app_db < backup.sql

# View database size
docker-compose exec db psql -U app_user -d app_db -c "SELECT pg_size_pretty(pg_database_size('app_db'));"
```

### Django Management

```bash
# Create admin user
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate

# Backup Django data
docker-compose exec web python manage.py dumpdata > django_backup.json

# Restore Django data
docker-compose exec web python manage.py loaddata django_backup.json
```

### Container Management

```bash
# View all containers
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx

# Restart services
docker-compose restart
docker-compose restart db
docker-compose restart web

# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 📋 Configuration Files Changed

### `docker-compose.yml`
- Added PostgreSQL service with health checks
- Added `depends_on` for Django
- Added database environment variables
- Added `postgres_data` volume for persistence

### `requirements.txt`
- Added `psycopg2-binary==2.9.9` (PostgreSQL driver)
- Added `dj-database-url==2.1.0` (for DATABASE_URL)

### `Dockerfile`
- Added `libpq-dev` system dependency (for psycopg2)

### `entrypoint.sh`
- Added PostgreSQL wait logic
- Waits for database port 5432 to be ready
- Then runs migrations and starts Django

### `.env.example`
- Template for environment variables
- Copy to `.env` and fill in your values

### `.env.production`
- Updated with PostgreSQL variables

---

## 🔐 Update Django Settings (IMPORTANT)

Edit `core/settings.py` and update the DATABASES section:

**Option 1: Using DATABASE_URL (Recommended)**

```python
import dj_database_url
import os

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

**Option 2: Using Environment Variables**

```python
import os

if os.getenv('DB_ENGINE') == 'django.db.backends.postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'app_db'),
            'USER': os.getenv('DB_USER', 'app_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
            'HOST': os.getenv('DB_HOST', 'db'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    # SQLite fallback
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

---

## 🔄 Switching Between SQLite and PostgreSQL

### Use PostgreSQL (Production)

1. Set `.env` variables
2. Update `core/settings.py`
3. Run: `docker-compose up -d --build`

### Use SQLite (Development)

1. Keep default settings
2. PostgreSQL won't start (no damage)
3. Django uses SQLite automatically

---

## 🚨 Troubleshooting

### PostgreSQL won't start

```bash
# Check logs
docker-compose logs db

# Common causes:
# - Port 5432 in use: docker-compose down && docker-compose up -d
# - Permission issues: docker-compose down -v
# - Invalid password: Check .env file
```

### Django can't connect to database

```bash
# Verify database is running
docker-compose ps db

# Check database is healthy
docker-compose ps  # Look for "healthy"

# Wait longer and retry
sleep 10 && docker-compose exec web python manage.py migrate
```

### Migrations fail

```bash
# View detailed error
docker-compose exec web python manage.py migrate --verbosity 3

# Connect to database and check
docker-compose exec db psql -U app_user -d app_db -c "\dt"
```

### Out of memory

```bash
# Check usage
docker stats

# Clean up
docker system prune
docker volume prune
```

---

## 📈 Performance Tuning

### Gunicorn Workers

Default: 4 workers

For your CPU cores:
- 2 CPUs: 5 workers
- 4 CPUs: 9 workers
- 8 CPUs: 17 workers

Edit `entrypoint.sh`:
```bash
--workers 17
```

### PostgreSQL Optimization

For 4GB RAM server, add to docker-compose.yml:

```yaml
db:
  command: 
    - "postgres"
    - "-c"
    - "shared_buffers=1GB"
    - "-c"
    - "effective_cache_size=3GB"
    - "-c"
    - "work_mem=5242kB"
    - "-c"
    - "maintenance_work_mem=256MB"
    - "-c"
    - "max_connections=200"
```

---

## 💾 Backup Strategy

### Daily Backup (PostgreSQL)

Create `backup.sh`:

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U app_user -d app_db > backups/db_$TIMESTAMP.sql
docker-compose exec web python manage.py dumpdata > backups/data_$TIMESTAMP.json
echo "Backup completed: $TIMESTAMP"
```

### Cron Scheduling

```bash
# Edit crontab
crontab -e

# Add (daily at 2 AM)
0 2 * * * cd /path/to/project && bash backup.sh
```

---

## 📊 Monitoring

### Check Database Status

```bash
# Active connections
docker-compose exec db psql -U app_user -d app_db -c "SELECT count(*) FROM pg_stat_activity;"

# Database size
docker-compose exec db psql -U app_user -d app_db -c "SELECT pg_size_pretty(pg_database_size('app_db'));"

# Slow queries
docker-compose exec db psql -U app_user -d app_db -c "SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

---

## ✅ Production Checklist

- [ ] `.env` file created with strong password
- [ ] `.env` added to `.gitignore`
- [ ] Django settings updated for PostgreSQL
- [ ] `docker-compose build` successful
- [ ] `docker-compose up -d` successful
- [ ] Migrations ran without errors
- [ ] Database health check passing
- [ ] Static files collected
- [ ] Admin user created
- [ ] App accessible at domain
- [ ] HTTPS working (SSL certificate)
- [ ] Backup script created
- [ ] Monitoring enabled

---

## 🎯 Next Steps

1. ✅ Update Django `core/settings.py` (see above)
2. ✅ Create `.env` file with PostgreSQL details
3. ✅ Run: `docker-compose build`
4. ✅ Run: `docker-compose up -d`
5. ✅ Monitor: `docker-compose logs -f`
6. ✅ Access: `https://app.preqly.com`
7. ✅ Backup: Set up daily backups

---

## 📚 Additional Resources

- See: `POSTGRESQL_SETUP.md` for detailed guide
- See: `DOCKER_QUICK_START.md` for common commands
- See: `DEPLOYMENT_SUMMARY.md` for overview

---

**Your setup now includes:**
- ✅ Django application
- ✅ PostgreSQL 15 database
- ✅ Nginx reverse proxy
- ✅ SSL/TLS encryption
- ✅ Auto migrations
- ✅ Production-ready

Ready to deploy! 🚀
