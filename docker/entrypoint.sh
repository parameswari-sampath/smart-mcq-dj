#!/bin/bash

# Docker entrypoint script for Smart MCQ Platform
set -e

echo "🚀 Starting Smart MCQ Platform..."

# Create postgres user directories with proper ownership
mkdir -p /var/lib/postgresql/15/main
chown -R postgres:postgres /var/lib/postgresql

# Initialize PostgreSQL if needed
if [ ! -f "/var/lib/postgresql/15/main/PG_VERSION" ]; then
    echo "📦 Initializing PostgreSQL database..."
    sudo -u postgres /usr/lib/postgresql/15/bin/initdb -D /var/lib/postgresql/15/main
    echo "✅ PostgreSQL initialized!"
fi

# Start PostgreSQL service
echo "⏳ Starting PostgreSQL..."
service postgresql start

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until sudo -u postgres psql -c "SELECT 1" >/dev/null 2>&1; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "✅ PostgreSQL is ready!"

# Create database and user if they don't exist
echo "🔧 Setting up database and user..."
sudo -u postgres psql -c "SELECT 1 FROM pg_user WHERE usename = 'mcq_user';" | grep -q 1 || \
sudo -u postgres psql -c "CREATE USER mcq_user WITH PASSWORD 'mcq_secure_password_2024';"

sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname = 'smart_mcq_db';" | grep -q 1 || \
sudo -u postgres psql -c "CREATE DATABASE smart_mcq_db OWNER mcq_user;"

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE smart_mcq_db TO mcq_user;"

# Run Django setup
echo "🔧 Setting up Django application..."
export DJANGO_SETTINGS_MODULE=smart_mcq.production_settings

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist
echo "👤 Creating superuser if needed..."
python -c "
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
gunicorn smart_mcq.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60 &

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