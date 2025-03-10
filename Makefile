# Define variables
DOCKER_IMAGE := my-python-app
DOCKERFILE := build.Dockerfile
CONTAINER_NAME := my-python-app-container
BIN_DIR := bin
EXECUTABLE := main
BIN_EXE_LINUX := prerender-nginx-linux

# Default target
# all: build

# Build the Docker image and copy the executable to the host filesystem
build-linux:
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE) -f $(DOCKERFILE) .
	@echo "Creating container..."
	docker create --name $(CONTAINER_NAME) $(DOCKER_IMAGE)
	@echo "Copying executable to host filesystem..."
	mkdir -p $(BIN_DIR)
	docker cp $(CONTAINER_NAME):/usr/src/app/$(BIN_DIR)/$(EXECUTABLE) $(BIN_DIR)/$(BIN_EXE_LINUX)
	@echo "Cleaning up..."
	docker rm $(CONTAINER_NAME)
	@echo "Executable copied to ./$(BIN_DIR)/$(BIN_EXE_LINUX)"

# Clean up build artifacts and temporary files
clean:
	rm -rf build dist **/*.spec
	rm -f ./prerender.log ./.prerender-site

.PHONY: all build clean