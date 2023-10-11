#!/bin/bash

# Define variables
AIRFLOW_VERSION="2.7.0"
IMAGE_NAME="msc-ds-7029-20275335-airflow-image"
DOCKERFILE_PATH="./Dockerfile"
COMPOSE_FILE="docker-compose.yaml"

# Build the Docker image
docker build -t "$IMAGE_NAME" -f "$DOCKERFILE_PATH" --build-arg AIRFLOW_VERSION="$AIRFLOW_VERSION" .

# Run a container from the image
# docker run -d -p 8080:8080 --name msc-ds-7029-20275335-airflow-container "$IMAGE_NAME"

# Provide some information about the running container
# echo "Docker container $IMAGE_NAME is now running."

# Run Docker Compose
docker-compose -f "$COMPOSE_FILE" up -d

# Provide some information about the Docker Compose services
echo "Docker Compose services are now running."

# You can add more commands here if needed
