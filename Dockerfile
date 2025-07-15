# Production Dockerfile for Smart MCQ Platform
# Multi-stage build optimized for uv and production deployment

FROM python:3.11-slim AS builder

# Install uv - fast Python package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory for build
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into /app/.venv
RUN uv sync --frozen --no-cache --no-dev

# Production stage
FROM python:3.11-slim

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Add venv to path
ENV PATH="/app/.venv/bin:$PATH"

# Create app user for security
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=app:app . .

# Copy production configuration
COPY --chown=app:app docker/nginx.conf /etc/nginx/sites-available/default
COPY --chown=app:app docker/production_settings.py /app/smart_mcq/production_settings.py

# Create necessary directories with proper permissions
RUN mkdir -p /app/staticfiles /app/media /app/logs \
    && chown -R app:app /app \
    && chmod +x /app/docker/entrypoint.simple.sh

# Collect static files as app user
USER app
RUN /app/.venv/bin/python manage.py collectstatic --noinput --settings=smart_mcq.production_settings

# Switch back to root for service management
USER root

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/health/ || exit 1

# Use simple entrypoint (external database)
CMD ["/app/docker/entrypoint.simple.sh"]