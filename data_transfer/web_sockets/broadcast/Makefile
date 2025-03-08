# Variables
COMPOSE := compose..yaml
ENV_FILE_PATH := .env
DEV_ENV_FILE_PATH := .env.dev

# Start registry services
.PHONY: start
start:
	docker compose --env-file ${ENV_FILE_PATH} -f  $(COMPOSE) up -d

# Stop all services
.PHONY: stop
stop: stop
	docker compose --env-file ${ENV_FILE_PATH} -f  $(COMPOSE) down

.PHONY: start-dev
start:
	docker compose --env-file ${DEV_ENV_FILE_PATH} -f  $(COMPOSE) up -d

.PHONY: stop-dev
stop-dev:
	docker compose --env-file ${DEV_ENV_FILE_PATH} -f  $(COMPOSE) down


# Clean everything
.PHONY: clean-services
clean-everything: stop
	docker network rm $(NETWORK_NAME) 2>/dev/null || true
	docker volume prune -f

# Show logs
.PHONY: logs
logs: # Show all services logs
	docker compose -f $(COMPOSE) logs -f & \
	
# Build images
.PHONY: build
build: ## Build all serrvices
	docker compose -f $(COMPOSE) build


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


