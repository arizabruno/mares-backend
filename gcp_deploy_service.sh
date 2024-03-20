#!/bin/bash

# Variables
PROJECT_ID="le-wagon-march2024"
REPOSITORY_NAME="mares"
REGION="europe-west1"
SERVICE_NAME="api"
TYPE="prod"
GAR_NAME="$PROJECT_ID/$REPOSITORY_NAME/$SERVICE_NAME:$TYPE"
DOCKERFILE_PATH="docker/Dockerfile"
IMAGE_URI="$REGION-docker.pkg.dev/$GAR_NAME"
MEMORY="2Gi"

# Configure Docker for Google Artifact Registry
echo "Configuring Docker for Google Artifact Registry..."
gcloud auth configure-docker $REGION-docker.pkg.dev

# Check for existing Google Artifact Repository and create if necessary
echo "Checking for existing Google Artifact Repository..."
if gcloud artifacts repositories describe $REPOSITORY_NAME --location=$REGION 2>/dev/null; then
    echo "Repository $REPOSITORY_NAME already exists in location $REGION."
else
    echo "Creating repository $REPOSITORY_NAME in location $REGION."
    gcloud artifacts repositories create $REPOSITORY_NAME --repository-format=docker --location=$REGION --description="Mares API"
fi

# Build Docker image
echo "Building Docker image..."
docker build --platform linux/amd64 -f $DOCKERFILE_PATH -t $IMAGE_URI .

# Push Docker image to Google Artifact Registry
echo "Pushing Docker image to Google Artifact Registry..."
docker push $IMAGE_URI

# Deploy to Google Cloud Run
echo "Deploying to Google Cloud Run..."
gcloud run deploy $SERVICE_NAME --image $IMAGE_URI --memory $MEMORY --region $REGION --allow-unauthenticated
