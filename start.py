#!/usr/bin/env python3
import subprocess
import time

def check_and_start_postgres():
    """Check if PostgreSQL container is running, start if not"""
    try:
        # Check if container is running
        result = subprocess.run("docker ps --filter name=smart_mcq_postgres --format '{{.Names}}'", 
                               shell=True, capture_output=True, text=True)
        
        if "smart_mcq_postgres" not in result.stdout:
            print("🐘 Starting PostgreSQL container...")
            subprocess.run("docker-compose up -d", shell=True)
            
            # Wait for PostgreSQL to be ready
            print("⏳ Waiting for PostgreSQL...")
            for _ in range(15):
                check = subprocess.run("docker exec smart_mcq_postgres pg_isready -U mcq_user", 
                                     shell=True, capture_output=True)
                if check.returncode == 0:
                    print("✅ PostgreSQL is ready!")
                    break
                time.sleep(1)
        else:
            print("✅ PostgreSQL is already running")
    except Exception as e:
        print(f"Warning: Could not check PostgreSQL status: {e}")

if __name__ == "__main__":
    check_and_start_postgres()
    print("🚀 Starting Django server...")
    subprocess.run("uv run python manage.py runserver 0.0.0.0:8000", shell=True)