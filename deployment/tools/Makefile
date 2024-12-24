# Variables
NETWORK_NAME := mlops_network
TRAINING_COMPOSE := docker-compose.model-train.yaml
REGISTRY_COMPOSE := docker-compose.model-registry.yaml
API_COMPOSE := docker-compose.api.yaml

# Default target
.PHONY: all
all: network start

# Create shared network
.PHONY: network
network:
	docker network create $(NETWORK_NAME) 2>/dev/null || true

# Start all services
.PHONY: start
start: network start-registry start-training start-api


# Stop all services
.PHONY: stop
stop: stop-training stop-registry stop-api


# Start registry services
.PHONY: start-registry
start-registry:
	docker compose -f mlops/$(REGISTRY_COMPOSE) up -d

# Stop registry services
.PHONY: stop-registry
stop-registry:
	docker compose -f mlops/$(REGISTRY_COMPOSE) down


# Start training services
.PHONY: start-training
start-training:
	docker compose -f mlops/$(TRAINING_COMPOSE) up -d


# Stop training services
.PHONY: stop-training
stop-training:
	docker compose -f mlops/$(TRAINING_COMPOSE) down



# Start training services
.PHONY: start-api
start-api:
	docker compose -f mlops/$(API_COMPOSE) up -d


# Stop training services
.PHONY: stop-api
stop-api:
	docker compose -f mlops/$(API_COMPOSE) down


# Clean everything
.PHONY: clean-services
clean-everything: stop
	docker network rm $(NETWORK_NAME) 2>/dev/null || true
	docker volume prune -f

# Show logs
.PHONY: logs
logs: # Show all services logs
	docker compose -f $(TRAINING_COMPOSE) logs -f & \
	docker compose -f $(REGISTRY_COMPOSE) logs -f & \
	docker compose -f $(API_COMPOSE) logs -f

# Build images
.PHONY: build
build: ## Build all serrvices
	docker compose -f $(TRAINING_COMPOSE) build
	docker compose -f $(REGISTRY_COMPOSE) build
	docker compose -f $(API_COMPOSE) build


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



# # Enter ml-training container
# .PHONY: bash-training
# bash-training: ## Enter ml-training container
# 	docker exec -it mlkit bash

# # Enter registry container
# .PHONY: bash-registry
# bash-registry: ## Enter registry container
# 	docker exec -it model_registry bash

# # Enter api container
# .PHONY: bash-api
# bash-api: ## Enter api container
# 	docker exec -it api bash
