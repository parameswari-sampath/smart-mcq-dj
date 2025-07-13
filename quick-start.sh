#!/bin/bash

# Smart MCQ Platform - One Command Deployment
echo "🚀 Smart MCQ Platform - Quick Start"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install it and try again."
    exit 1
fi

echo "📦 Starting Smart MCQ Platform..."
echo "This will:"
echo "  - Download and start PostgreSQL database"
echo "  - Build and start Django application"
echo "  - Set up everything automatically"
echo ""

# Start the application
docker-compose -f docker-compose.all-in-one.yml up -d

echo ""
echo "⏳ Starting services (this may take a minute)..."

# Wait for the application to be ready
echo "⏳ Waiting for application to be ready..."
sleep 30

# Check if the application is responding
if curl -f http://localhost:8080/health/ > /dev/null 2>&1; then
    echo ""
    echo "🎉 SUCCESS! Smart MCQ Platform is ready!"
    echo ""
    echo "📱 Access the application:"
    echo "   🌐 Web: http://localhost:8080"
    echo "   📱 Mobile/Tablet: http://YOUR-IP:8080"
    echo ""
    echo "👤 Login credentials:"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo ""
    echo "⚠️  IMPORTANT: Change the admin password immediately!"
    echo ""
    echo "🎓 Features available:"
    echo "   ✅ Create multiple choice tests"
    echo "   ✅ Student test-taking interface"
    echo "   ✅ Result management and viewing"
    echo "   ✅ Timer-based test controls"
    echo "   ✅ Answer visibility settings"
    echo ""
    echo "🛑 To stop the platform:"
    echo "   docker-compose -f docker-compose.all-in-one.yml down"
else
    echo ""
    echo "⚠️  Application is starting but not ready yet..."
    echo "   Please wait a few more minutes and try: http://localhost:8080"
    echo ""
    echo "🔍 To check status:"
    echo "   docker-compose -f docker-compose.all-in-one.yml logs"
fi

echo ""
echo "📖 For more information, see DOCKER_DEPLOYMENT.md"