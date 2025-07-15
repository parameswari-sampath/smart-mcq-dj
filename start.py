#!/usr/bin/env python3
import subprocess
import os
import sys

def check_database_connection():
    """Check if database connection is working with Neon DB"""
    try:
        print("🔍 Checking database connection...")
        result = subprocess.run([
            "uv", "run", "python", "-c",
            """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_mcq.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
print('✅ Database connection successful!')
            """
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Neon DB connection verified!")
            return True
        else:
            print(f"❌ Database connection failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def run_migrations():
    """Run Django migrations"""
    print("📦 Running migrations...")
    result = subprocess.run(["uv", "run", "python", "manage.py", "migrate"])
    if result.returncode == 0:
        print("✅ Migrations completed successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1)

def create_superuser():
    """Create superuser if it doesn't exist"""
    print("👤 Checking for superuser...")
    try:
        result = subprocess.run([
            "uv", "run", "python", "-c",
            """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_mcq.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@smartmcq.com', 'admin123')
    print('✅ Superuser admin created with password admin123')
else:
    print('ℹ️ Superuser already exists')
            """
        ], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Warning: Could not create superuser: {e}")

if __name__ == "__main__":
    print("🚀 Smart MCQ Platform - Starting with Neon DB")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found! Please create .env with DATABASE_URL")
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        print("❌ Cannot connect to database. Please check your .env file and DATABASE_URL")
        sys.exit(1)
    
    # Run migrations
    run_migrations()
    
    # Create superuser if needed
    create_superuser()
    
    print("")
    print("🎉 Setup complete! Starting Django server...")
    print("📱 Access: http://localhost:8000")
    print("👤 Login: admin / admin123")
    print("")
    
    # Start Django server
    subprocess.run(["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"])