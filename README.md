# PY-CELLAR

PY-CELLAR is a comprehensive repository that encompasses Machine Learning (ML), MLOps, and DataOps projects. This repository provides production-ready templates and tools for building robust ML applications and data pipelines.

## Repository Structure

The repository is organized into two main components:

1. **mlapi**: A production-ready ML API template with integrated MLOps components
2. **crud_api**: A production-ready CRUD API template with authentication

### 1. mlapi

The `mlapi` directory contains a production ML API template along with essential MLOps components. It's designed to be deployed using Docker Compose and includes the following services:

- **ML API**: A FastAPI-based service for serving machine learning models
- **MongoDB**: For storing operation logs, model metadata, and model results
- **Prometheus**: For monitoring and alerting
- **Grafana**: For creating dashboards and visualizing metrics
- **MinIO**: Object storage for model artifacts and large datasets

#### Key Features

- Scalable ML model serving
- Comprehensive logging and monitoring
- Model versioning and metadata management
- Object storage for large files and datasets

### 2. crud_api

The `crud_api` directory contains a production-ready CRUD API template with authentication. It's designed to be deployed using Docker Compose and includes:

- **CRUD API**: A FastAPI-based service for handling CRUD operations
- **PostgreSQL**: As the primary database for storing application data
- **Authentication Service**: For secure user authentication and authorization
- **Pytest Integration**: For comprehensive unit and integration testing

#### Key Features

- RESTful API design
- Database integration with PostgreSQL
- Secure authentication and authorization
- Docker Compose setup for easy deployment
- Comprehensive test suite using pytest
