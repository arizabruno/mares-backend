#!/bin/bash

# Variables
REGION="sa-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
REPO_NAME="mares-api"  # name of the ECR repository
IMAGE_TAG="latest"  # tag for your docker image

# Create ECR repository if it does not exist
echo "Creating ECR repository..."
aws ecr describe-repositories --repository-names $REPO_NAME --region $REGION 2>/dev/null
if [ $? -ne 0 ]; then
    aws ecr create-repository --repository-name $REPO_NAME --region $REGION
fi

# Get login command from ECR and execute it to authenticate Docker to the registry
echo "Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Enable experimental features to use buildx (if not already set)
export DOCKER_CLI_EXPERIMENTAL=enabled

# Create a new builder instance which can create multi-architecture images
docker buildx create --name mybuilder --use

# Build the Docker image for both amd64 and arm64 architectures
echo "Building multi-architecture Docker image..."
docker buildx build --platform linux/amd64,linux/arm64/v8 --tag $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG --push .

echo "Deployment complete!"
