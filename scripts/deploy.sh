
#!/bin/bash

# Deployment script for YouTube Downloader App
set -e

echo "🚀 Deploying YouTube Downloader App..."

# Configuration
APP_NAME="youtube-downloader"
IMAGE_NAME="youtube-downloader:latest"
CONTAINER_NAME="youtube-downloader-app"

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t $IMAGE_NAME .

# Stop existing container if running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "🛑 Stopping existing container..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Run new container
echo "🚀 Starting new container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p 8501:8501 \
    -v $(pwd)/downloads:/app/downloads \
    -v $(pwd)/logs:/app/logs \
    --restart unless-stopped \
    $IMAGE_NAME

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Check if container is running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "✅ Container is running successfully!"
    echo "🌐 App is available at: http://localhost:8501"
    
    # Show container logs
    echo "📋 Container logs:"
    docker logs $CONTAINER_NAME --tail 20
else
    echo "❌ Container failed to start"
    docker logs $CONTAINER_NAME
    exit 1
fi

echo "🎉 Deployment complete!"
