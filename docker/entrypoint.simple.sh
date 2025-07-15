#!/bin/bash

# Simple entrypoint for Django + external DB
set -e

echo "🚀 Starting Smart MCQ Platform (with external DB)..."

export DJANGO_SETTINGS_MODULE=smart_mcq.production_settings

# Wait for database to be ready
echo "⏳ Waiting for database..."
until /app/.venv/bin/python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_mcq.production_settings')
import django
django.setup()
from django.db import connection
connection.ensure_connection()
print('Database connected!')
"; do
    echo "Database not ready, waiting..."
    sleep 2
done

# Collect static files
echo "📂 Collecting static files..."
/app/.venv/bin/python manage.py collectstatic --noinput

# Run migrations
echo "📦 Running database migrations..."
/app/.venv/bin/python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "👤 Creating superuser if needed..."
/app/.venv/bin/python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_mcq.production_settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@smartmcq.com', 'admin123')
    print('✅ Superuser admin created with password admin123')
else:
    print('ℹ️ Superuser already exists')
"

# Start Django with Gunicorn
echo "🔧 Starting Django application..."
/app/.venv/bin/gunicorn smart_mcq.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60 &

# Start Nginx
echo "🔧 Starting Nginx..."
nginx -g "daemon off;" &

echo ""
echo "🎉 Smart MCQ Platform is ready!"
echo "📱 Access the application at:"
echo "   🌐 Production: https://smartmcq.meikuraledutech.in"
echo "   🏠 Local: http://localhost:8080"
echo "   🏢 Network: http://YOUR-IP:8080"
echo ""
echo "👤 Default login: admin / admin123"
echo "⚠️  Please change the default password immediately!"
echo ""

# Keep the container running
wait