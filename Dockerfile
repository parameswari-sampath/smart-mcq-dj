# Multi-stage build for optimized production image
FROM python:3.11-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-15 \
    postgresql-client-15 \
    postgresql-contrib-15 \
    nginx \
    curl \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Configure PostgreSQL
RUN service postgresql start && \
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';" && \
    service postgresql stop

# Configure PostgreSQL settings
RUN echo "listen_addresses = '*'" >> /etc/postgresql/15/main/postgresql.conf && \
    echo "shared_buffers = 256MB" >> /etc/postgresql/15/main/postgresql.conf && \
    echo "max_connections = 100" >> /etc/postgresql/15/main/postgresql.conf && \
    echo "work_mem = 8MB" >> /etc/postgresql/15/main/postgresql.conf

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy application code
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Copy configuration files
COPY docker/nginx.conf /etc/nginx/sites-available/default
COPY docker/production_settings.py /app/smart_mcq/production_settings.py

# Set permissions
RUN chown -R app:app /app
RUN chmod +x /app/docker/entrypoint.sh

# Collect static files
USER app
RUN python manage.py collectstatic --noinput --settings=smart_mcq.production_settings

# Switch back to root for supervisor
USER root

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/health/ || exit 1

# Start supervisor
CMD ["/app/docker/entrypoint.sh"]