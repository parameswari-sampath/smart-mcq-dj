#!/bin/bash

# Smart MCQ Platform - Build and Deploy Script
set -e

# Configuration
DOCKER_USERNAME="your-dockerhub-username"  # Change this to your Docker Hub username
IMAGE_NAME="smart-mcq"
VERSION="v1.4.1"
LATEST_TAG="latest"

echo "🚀 Smart MCQ Platform - Build and Deploy"
echo "========================================"

# Function to build image
build_image() {
    echo "📦 Building Docker image..."
    docker build --no-cache -t ${IMAGE_NAME}:${VERSION} .

    docker tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:${LATEST_TAG}
    echo "✅ Image built successfully!"
}

# Function to test image locally
test_local() {
    echo "🧪 Testing image locally..."
    docker run -d --name smart_mcq_test -p 8080:80 ${IMAGE_NAME}:${LATEST_TAG}
    
    echo "⏳ Waiting for application to start..."
    sleep 30
    
    # Test health endpoint
    if curl -f http://localhost:8080/health/ > /dev/null 2>&1; then
        echo "✅ Health check passed!"
    else
        echo "❌ Health check failed!"
        exit 1
    fi
    
    # Cleanup test container
    docker stop smart_mcq_test
    docker rm smart_mcq_test
    echo "✅ Local test completed!"
}

# Function to push to Docker Hub
push_to_hub() {
    echo "📤 Pushing to Docker Hub..."
    
    # Tag for Docker Hub
    docker tag ${IMAGE_NAME}:${VERSION} ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}
    docker tag ${IMAGE_NAME}:${LATEST_TAG} ${DOCKER_USERNAME}/${IMAGE_NAME}:${LATEST_TAG}
    
    # Push images
    echo "🔐 Please login to Docker Hub..."
    docker login
    
    echo "📤 Pushing version ${VERSION}..."
    docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}
    
    echo "📤 Pushing latest..."
    docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${LATEST_TAG}
    
    echo "✅ Images pushed to Docker Hub!"
    echo "📋 Available tags:"
    echo "   - ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"
    echo "   - ${DOCKER_USERNAME}/${IMAGE_NAME}:${LATEST_TAG}"
}

# Function to deploy production
deploy_production() {
    echo "🌐 Deploying to production..."
    
    # Stop existing container if running
    docker-compose -f docker-compose.prod.yml down || true
    
    # Pull latest image
    docker pull ${DOCKER_USERNAME}/${IMAGE_NAME}:${LATEST_TAG} || echo "Using local image"
    
    # Start production deployment
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "✅ Production deployment started!"
    echo "🌐 Access: https://smartmcq.meikuraledutech.in"
}

# Function to deploy local test
deploy_local() {
    echo "🏠 Deploying for local testing..."
    
    # Stop existing container if running
    docker-compose -f docker-compose.local.yml down || true
    
    # Start local deployment
    docker-compose -f docker-compose.local.yml up -d
    
    echo "✅ Local deployment started!"
    echo "🏠 Access: http://localhost:8080"
}

# Main menu
show_menu() {
    echo ""
    echo "Select deployment option:"
    echo "1) Build image only"
    echo "2) Build and test locally"
    echo "3) Build, test, and push to Docker Hub"
    echo "4) Deploy production (your VPS)"
    echo "5) Deploy local testing"
    echo "6) Full pipeline (build → test → push → deploy production)"
    echo "7) Exit"
    echo ""
}

# Main execution
main() {
    while true; do
        show_menu
        read -p "Enter your choice (1-7): " choice
        
        case $choice in
            1)
                build_image
                ;;
            2)
                build_image
                test_local
                ;;
            3)
                build_image
                test_local
                push_to_hub
                ;;
            4)
                deploy_production
                ;;
            5)
                deploy_local
                ;;
            6)
                build_image
                test_local
                push_to_hub
                deploy_production
                ;;
            7)
                echo "👋 Goodbye!"
                exit 0
                ;;
            *)
                echo "❌ Invalid option. Please try again."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Update Docker username reminder
if [ "$DOCKER_USERNAME" = "your-dockerhub-username" ]; then
    echo "⚠️  Please update DOCKER_USERNAME in this script with your Docker Hub username"
    read -p "Enter your Docker Hub username: " DOCKER_USERNAME
fi

# Run main function
main