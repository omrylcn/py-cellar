DOCKER_COMPOSE := docker-compose

.PHONY: docker-up docker-down run help

VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
UV := uv


docker-up:  ## Start the Docker containers
	$(DOCKER_COMPOSE) -f docker/docker-compose.yaml up

docker-down:  ## Stop and remove containers, networks, images, and volumes
	$(DOCKER_COMPOSE) -f docker/docker-compose.yaml down


help:  ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


run:  ## Run the application
	$(UV) run  run.py

.DEFAULT_GOAL := help