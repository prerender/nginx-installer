# Define variables
DOCKER_IMAGE := my-python-app
DOCKERFILE := build.Dockerfile
CONTAINER_NAME := my-python-app-container
BIN_DIR := bin
EXECUTABLE := main
BIN_EXE_LINUX := prerender-nginx-linux
BIN_EXE := prerender-nginx-mac

# Default target
# all: build

# Build the Docker image and copy the executable to the host filesystem
build-docker:
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

build:
	@echo "Building executable..."
	pyinstaller --onefile --distpath $(BIN_DIR) --name $(BIN_EXE) src/main.py
	@echo "Executable built in ./$(BIN_DIR)/$(BIN_EXE)"


# Clean up build artifacts and temporary files
clean:
	rm -rf build dist **/*.spec ./*.spec
	rm -f ./prerender.log ./.prerender_site_url ./.prerender_nginx_conf ./.prerender_server_conf ./.prerender_token
	rm -rf **/**/*.prerender.backup ./*.prerender.backup

.PHONY: all build clean