# Use official Python runtime as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Set work directory
WORKDIR /app

# Install system dependencies (including PostgreSQL client)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn==21.2.0

# Copy project
COPY . .

# Create directory for static files and media
RUN mkdir -p /app/staticfiles /app/media

# Copy entrypoint script
COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8005

# Run entrypoint script with bash to avoid permission issues on Windows
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
