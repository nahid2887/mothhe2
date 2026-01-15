#!/bin/bash

# Exit on error
set -e

echo "Starting Django application..."

# Wait for PostgreSQL if configured
if [ -n "$DB_HOST" ]; then
    echo "Waiting for PostgreSQL database at $DB_HOST:$DB_PORT..."
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "${DB_USER:-postgres}" > /dev/null 2>&1; do
        sleep 1
    done
    echo "PostgreSQL is ready!"
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
# python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

# Start Gunicorn
echo "Starting Gunicorn server..."
gunicorn core.wsgi:application \
    --bind 0.0.0.0:8005 \
    --workers 4 \
    --worker-class sync \
    --access-logfile - \
    --error-logfile - \
    --log-level info
