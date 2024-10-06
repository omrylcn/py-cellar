DOCKER_COMPOSE := docker-compose

.PHONY: docker-up docker-down run help

VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
UV := uv
ENV_FILE := .env
DOCKER_COMPOSE_FILE := mlops/docker-compose.yaml


docker-up:  ## Start the Docker containers
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) --env-file $(ENV_FILE) up 

docker-down:  ## Stop and remove containers, networks, images, and volumes
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) --env-file $(ENV_FILE) down

help:  ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

run:  ## Run the application
	$(UV) run  run.py

clean:  ## Remove the virtual environment and cached files
	rm -rf $(VENV_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.DEFAULT_GOAL := help
