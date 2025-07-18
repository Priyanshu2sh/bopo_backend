#!/bin/bash

set -e  # Exit on error

# Timestamped log file
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
LOG_FILE="build_${TIMESTAMP}.log"
echo "📄 Logging build to $LOG_FILE"
exec > >(tee -a "$LOG_FILE") 2>&1

# Load .env variables
ENV_FILE=".env"
if [[ ! -f $ENV_FILE ]]; then
  echo "❌ .env file not found!"
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

if [[ -z "$IMAGE" ]]; then
  echo "❌ IMAGE not set in .env"
  exit 1
fi

if [[ -z "$DOCKER_HUB_USERNAME" || -z "$DOCKER_HUB_TOKEN" ]]; then
  echo "❌ DOCKER_HUB_USERNAME or DOCKER_HUB_TOKEN not set in .env"
  exit 1
fi

echo "📦 Building Docker image: $IMAGE"
BUILD_START=$(date +%s)
sudo docker build -t "$IMAGE" .
BUILD_END=$(date +%s)
echo "✅ Build complete (⏱️ $((BUILD_END - BUILD_START)) seconds)"

echo "🔐 Logging into Docker Hub..."
echo "$DOCKER_HUB_TOKEN" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin

echo "🚀 Pushing image to Docker Hub..."
PUSH_START=$(date +%s)
sudo docker push "$IMAGE"
PUSH_END=$(date +%s)
echo "✅ Push complete (⏱️ $((PUSH_END - PUSH_START)) seconds)"
echo "🎉 Image $IMAGE successfully built and pushed!"
echo "🧹 Cleaning up dangling images..."
sudo docker image prune -f
echo "✅ Cleanup complete. 🚀 Done!"
