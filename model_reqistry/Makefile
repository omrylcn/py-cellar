# Variables
NETWORK_NAME := mlops_network
REGISTRY_COMPOSE := docker-compose.model-registry.yaml
ENV_FILE_PATH := .env


# Default target
.PHONY: all
all: network start

# Create shared network
.PHONY: network
network:
	docker network create $(NETWORK_NAME) 2>/dev/null || true

# Start all services
.PHONY: start
start: network start-registry 


# Stop all services
.PHONY: stop
stop: stop-registry 


# Start registry services
.PHONY: start-registry
start-registry:
	docker compose --env-file ${ENV_FILE_PATH} -f mlops/$(REGISTRY_COMPOSE) up -d

# Stop registry services
.PHONY: stop-registry
stop-registry:
	docker compose --env-file ${ENV_FILE_PATH}  -f mlops/$(REGISTRY_COMPOSE) down


# Clean everything
.PHONY: clean-services
clean-everything: stop
	docker network rm $(NETWORK_NAME) 2>/dev/null || true
	docker volume prune -f

# Show logs
.PHONY: logs
logs: # Show all services logs
	docker compose -f $(REGISTRY_COMPOSE) logs -f & \
	

# Build images
.PHONY: build
build: ## Build all serrvices
	docker compose -f $(REGISTRY_COMPOSE) build


.PHONY: clean-file
clean-file:  ## Remove the virtual environment and cached files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: format
format:
	uvx ruff format .

.PHONY: lint	
lint:
	uvx ruff check .


help:  ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


