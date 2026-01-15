# PostgreSQL Configuration Guide

## Overview

Your Docker setup now includes **PostgreSQL 15** as the database service. This is recommended for production environments.

---

## 🗄️ Database Options

### SQLite (Current Default)
- ✅ Good for: Small apps, development, testing
- ✅ No setup required
- ❌ Limited for high concurrency
- Database file: `db.sqlite3`

### PostgreSQL (Recommended for Production)
- ✅ Good for: Production, high concurrency, scale
- ✅ Advanced features (transactions, JSONB, etc.)
- ✅ Robust backup/restore
- ❌ Requires setup
- Database: Inside Docker container

---

## 🚀 Quick Start with PostgreSQL

### 1. Environment Configuration

Create `.env` file in project root:

```env
# Database Configuration
DB_NAME=app_db
DB_USER=app_user
DB_PASSWORD=secure_password_change_me_12345
DB_HOST=db
DB_PORT=5432

# Django Configuration
DEBUG=False
ALLOWED_HOSTS=app.preqly.com,localhost,127.0.0.1
SECRET_KEY=django-insecure-%x$m-99gefp!$jt)*v1p_r$mgiqx3wnub^9@nqx0r=9g2(p2!x
```

### 2. Update Django Settings

Edit `core/settings.py`:

```python
import dj_database_url
import os

# Database configuration
if os.getenv('DB_ENGINE') == 'django.db.backends.postgresql':
    # PostgreSQL configuration
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
    # SQLite configuration (default)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

Or use the simpler approach with dj-database-url:

```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

### 3. Build & Deploy

```bash
# Build with PostgreSQL support
docker-compose build

# Start containers (PostgreSQL + Django)
docker-compose up -d

# Check PostgreSQL is healthy
docker-compose ps

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

---

## 📊 PostgreSQL Services

In `docker-compose.yml`:

```yaml
db:
  image: postgres:15
  container_name: postgres_db
  environment:
    POSTGRES_DB: app_db
    POSTGRES_USER: app_user
    POSTGRES_PASSWORD: secure_password_change_me
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U app_user"]
    interval: 10s
    timeout: 5s
    retries: 5
  networks:
    - app_network
```

### Health Check

PostgreSQL includes automatic health checks:
- Checks every 10 seconds
- Timeout: 5 seconds
- Retries: 5 attempts
- Django waits for database to be healthy before starting

---

## 🔐 Security Configuration

### Strong Passwords

Generate a secure password:

```bash
# Linux/Mac
openssl rand -base64 32

# Or use Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Environment Variables

Store sensitive data in `.env` file:

```bash
# Never commit .env to git
echo ".env" >> .gitignore

# Use for Docker
docker-compose --env-file .env up -d
```

### Database Access Control

By default:
- PostgreSQL only accessible from Django container
- Not exposed to external network (internal Docker network)
- SSH access to server still required for backups

---

## 🛠️ Common PostgreSQL Commands

### Access PostgreSQL Command Line

```bash
# Connect to PostgreSQL container
docker-compose exec db psql -U app_user -d app_db

# Common commands inside psql
\l                    # List databases
\du                   # List users
\dt                   # List tables
SELECT * FROM auth_user;  # Query example
\q                    # Quit
```

### Backup Database

```bash
# Backup to file
docker-compose exec db pg_dump -U app_user -d app_db > backup.sql

# Backup with compression
docker-compose exec db pg_dump -U app_user -d app_db -F c > backup.dump
```

### Restore Database

```bash
# Restore from SQL file
docker-compose exec -T db psql -U app_user -d app_db < backup.sql

# Restore from compressed dump
docker-compose exec -T db pg_restore -U app_user -d app_db backup.dump
```

### Create Database Dump (Django style)

```bash
# Export all data to JSON
docker-compose exec web python manage.py dumpdata > backup.json

# Export specific app
docker-compose exec web python manage.py dumpdata account > account_backup.json

# Restore from JSON
docker-compose exec web python manage.py loaddata backup.json
```

---

## 🔄 Migration Guide: SQLite → PostgreSQL

### Step 1: Backup Current Data

```bash
# Export from SQLite
docker-compose exec web python manage.py dumpdata > data_backup.json
```

### Step 2: Update Settings

Edit `core/settings.py` to use PostgreSQL (see above)

### Step 3: Update docker-compose.yml

Already includes PostgreSQL service (see above)

### Step 4: Build & Start

```bash
# Build new image with PostgreSQL support
docker-compose build

# Start containers with PostgreSQL
docker-compose up -d

# Wait for database to be healthy
docker-compose exec web python manage.py migrate --noinput

# Load backed up data
docker-compose exec web python manage.py loaddata data_backup.json
```

### Step 5: Verify Migration

```bash
# Check data was restored
docker-compose exec db psql -U app_user -d app_db -c "SELECT COUNT(*) FROM auth_user;"
```

---

## 📈 Performance Tuning

### Connection Pooling

Add PgBouncer for connection pooling:

```yaml
pgbouncer:
  image: pgbouncer/pgbouncer:latest
  environment:
    DATABASES_HOST: db
    DATABASES_PORT: 5432
    DATABASES_USER: app_user
    DATABASES_PASSWORD: secure_password_change_me
    DATABASES_DBNAME: app_db
  ports:
    - "6432:6432"
  networks:
    - app_network
```

### Django Database Connection Settings

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'app_db',
        'USER': 'app_user',
        'PASSWORD': 'secure_password_change_me',
        'HOST': 'db',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'
        }
    }
}
```

### PostgreSQL Configuration

Create `postgresql.conf` for production tuning:

```conf
# In docker-compose.yml volumes
- ./postgresql.conf:/etc/postgresql/postgresql.conf

# Settings for 4GB RAM server
max_connections = 200
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 256MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 5242kB
min_wal_size = 1GB
max_wal_size = 4GB
```

---

## 🚨 Troubleshooting

### PostgreSQL Won't Start

```bash
# Check logs
docker-compose logs db

# Common issues:
# - Port 5432 already in use
# - Permission denied on volume
# - Password incorrect
```

### Connection Refused

```bash
# Verify database is running
docker-compose ps db

# Check it's healthy
docker-compose ps  # Look for "healthy" status

# Wait for startup
sleep 10 && docker-compose exec web python manage.py migrate
```

### Migrations Fail

```bash
# Check database connection
docker-compose exec web python manage.py dbshell

# Run migrations with verbose output
docker-compose exec web python manage.py migrate --verbosity 3

# Specific app migration
docker-compose exec web python manage.py migrate account
```

### Out of Disk Space

```bash
# Check volume usage
docker volume ls

# Clean up old data
docker system prune

# Vacuum PostgreSQL (reclaim space)
docker-compose exec db vacuumdb -U app_user -d app_db -a
```

---

## 📊 Monitoring PostgreSQL

### View Active Connections

```bash
docker-compose exec db psql -U app_user -d app_db -c "SELECT * FROM pg_stat_activity;"
```

### View Database Size

```bash
docker-compose exec db psql -U app_user -d app_db -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) FROM pg_database ORDER BY pg_database_size DESC;"
```

### View Table Sizes

```bash
docker-compose exec db psql -U app_user -d app_db -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables ORDER BY pg_total_relation_size DESC;"
```

### Slow Queries

```bash
# Enable slow query logging
docker-compose exec db psql -U app_user -d app_db -c "ALTER SYSTEM SET log_min_duration_statement = 1000;"

# View logs
docker-compose logs db | grep "duration:"
```

---

## 🔄 Backup Strategy

### Automated Backups

Create a backup script `backup-db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker-compose exec -T db pg_dump -U app_user -d app_db > "$BACKUP_FILE"

# Backup Django data
docker-compose exec web python manage.py dumpdata > "$BACKUP_DIR/data_$TIMESTAMP.json"

echo "Backup created: $BACKUP_FILE"

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

### Cron Job for Daily Backups

```bash
# Edit crontab
crontab -e

# Add (daily at 2 AM)
0 2 * * * cd /path/to/app && bash backup-db.sh

# Add (weekly to external storage)
0 3 * * 0 cd /path/to/app && tar -czf backups/full_backup_$(date +%Y%m%d).tar.gz backups/*.sql
```

---

## 🚀 Production Checklist

- [ ] Strong password set in `.env`
- [ ] `.env` added to `.gitignore`
- [ ] PostgreSQL health checks passing
- [ ] Migrations completed successfully
- [ ] Database backed up
- [ ] Connection limits configured
- [ ] Slow query logging enabled
- [ ] Regular backup schedule created
- [ ] Monitoring set up
- [ ] VACUUM scheduled regularly

---

## 📚 Additional Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Django PostgreSQL: https://docs.djangoproject.com/en/5.2/ref/databases/#postgresql-notes
- Docker PostgreSQL Image: https://hub.docker.com/_/postgres

---

## Summary

Your deployment now includes:
- ✅ PostgreSQL 15 database
- ✅ Automatic health checks
- ✅ Volume persistence
- ✅ Secure environment variables
- ✅ Django integration ready
- ✅ Backup/restore procedures
- ✅ Monitoring capabilities

**To use PostgreSQL:**
1. Set environment variables in `.env`
2. Update `core/settings.py`
3. Run: `docker-compose build`
4. Run: `docker-compose up -d`
5. Run: `docker-compose exec web python manage.py migrate`
