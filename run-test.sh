#!/bin/bash
set -e

# Usage check
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <path_to_docker_directory> <path_to_custom_nginx.conf>"
    exit 1
fi

DOCKER_DIR="$1"
CUSTOM_NGINX_CONF="$2"
IMAGE_NAME="test-nginx-image"

# Build the docker image from the specified directory
docker build -t "$IMAGE_NAME" "$DOCKER_DIR"

# Run the container with the custom nginx configuration mounted over the default file
docker run --rm -d \
  -p 80:80 \
  -v "$(pwd)/$CUSTOM_NGINX_CONF":/etc/nginx/nginx.conf \
  --name test-nginx-config "$IMAGE_NAME"

# Wait a bit for nginx to start
sleep 3

# Make a curl request to nginx on default port 80
echo "Making test HTTP request to nginx..."
curl -I http://localhost

# Stop and remove the container
docker stop test-nginx-config
docker rm test-nginx-config