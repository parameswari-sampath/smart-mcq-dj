#!/bin/bash

# Simple Build and Deploy Script for Smart MCQ Platform
set -e

echo "🚀 Smart MCQ Platform - Simple Deploy"
echo "====================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $(pwd)"

# Stop and remove existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans || true

# Remove all images related to this project
echo "🗑️ Removing old images..."
docker rmi $(docker images | grep smart_mcq | awk '{print $3}') 2>/dev/null || true
docker rmi $(docker images | grep smart-mcq | awk '{print $3}') 2>/dev/null || true

# Clean Docker system
echo "🧹 Cleaning Docker system..."
docker system prune -f

# Pull latest code from git
echo "📥 Pulling latest code from git..."
git stash || true
git pull origin main

# Build and deploy
echo "🔨 Building and deploying..."
docker-compose up --build -d --remove-orphans

echo ""
echo "🎉 Deployment complete!"
echo "📱 Access the application at:"
echo "   🌐 Production: https://smartmcq.meikuraledutech.in"
echo "   🏠 Local: http://localhost"
echo ""
echo "👤 Default login: admin / admin123"
echo "⚠️  Please change the default password immediately!"
echo ""