#!/bin/bash

# Markdown to PDF API Deployment Script

set -e

APP_NAME="markdown-pdf-api"
DOCKER_IMAGE="$APP_NAME:latest"

echo "Starting deployment of $APP_NAME..."

# Build Docker image
echo "Building Docker image..."
docker build -t $DOCKER_IMAGE .

# Stop existing container if running
echo "Stopping existing container..."
docker stop $APP_NAME 2>/dev/null || true
docker rm $APP_NAME 2>/dev/null || true

# Run new container
echo "Starting new container..."
docker run -d \
    --name $APP_NAME \
    --restart unless-stopped \
    -p 8000:8000 \
    -v $(pwd)/logs:/app/logs \
    -e API_ENV=production \
    -e DEBUG=false \
    -e LOG_LEVEL=INFO \
    $DOCKER_IMAGE

# Wait for container to start
echo "Waiting for container to start..."
sleep 10

# Health check
echo "Performing health check..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Health check passed"
    echo "✓ Deployment successful!"
    echo ""
    echo "API is running at: http://localhost:8000"
    echo "Documentation: http://localhost:8000/docs"
else
    echo "✗ Health check failed"
    echo "Container logs:"
    docker logs $APP_NAME
    exit 1
fi

# Clean up old images
echo "Cleaning up old Docker images..."
docker image prune -f

echo "Deployment completed successfully!"