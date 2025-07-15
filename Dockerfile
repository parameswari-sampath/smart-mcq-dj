# Production Dockerfile for Smart MCQ Platform
# Multi-stage build optimized for uv and production deployment

FROM python:3.13-slim AS builder

# Set working directory for build
WORKDIR /app

# Copy requirements file
COPY requirements.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /app/.venv \
    && /app/.venv/bin/pip install --upgrade pip \
    && /app/.venv/bin/pip install -r requirements.txt

# Production stage
FROM python:3.13-slim

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app user for security
RUN useradd --create-home --shell /bin/bash app

# Copy virtual environment from builder and set ownership
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Add venv to path
ENV PATH="/app/.venv/bin:$PATH"

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
    && chmod +x /app/docker/entrypoint.simple.sh \
    && find /app/.venv/bin -type f -executable -exec chmod +x {} \;

# Switch back to root for service management (static files will be collected at runtime)
USER root

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost/health/ || exit 1

# Use simple entrypoint (external database)
CMD ["/app/docker/entrypoint.simple.sh"]