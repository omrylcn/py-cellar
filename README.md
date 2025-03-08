# py-cellar

py-cellar is a comprehensive repository that encompasses Machine Learning (ML), MLOps, and DataOps codes,works,notes. This repository provides production-ready templates and tools for building robust ML applications and data pipelines.

## Repository Structure

The repository is organized into four main components:

1. **mlapi**: A production-ready ML API template with integrated MLOps components
2. **crud_api**: A production-ready CRUD API template with authentication
3. **model_registry**: A robust system for storing and versioning ML models with metadata management
4. **Feature Store**: *(Coming Soon)*

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

### 3. Model Registry

The `model_registry` directory contains a lightweight yet powerful system for managing machine learning models throughout their lifecycle. It's designed with a layered architecture and deployed with Docker Compose:

- **Registry API**: A FastAPI service for model operations (upload, download, metadata retrieval)
- **Storage Layer**: Dual storage strategy with MinIO for model binaries and MongoDB for metadata
- **Client Library**: Python client for seamless integration with ML workflows

#### Architecture

```
Client → Registry API → Storage Layer (MinIO + MongoDB)
```

#### Key Features

- **Model Storage**: Secure storage for model binary files using MinIO with tagging support
- **Metadata Management**: Flexible metadata tracking with MongoDB
- **Version Control**: Track multiple versions of models with detailed metadata
- **Streaming Support**: Efficient handling of large model files with streaming uploads/downloads
- **Comprehensive Error Handling**: Specialized exception hierarchy for robust error management
- **Python Client**: Well-designed client with automatic retries and error handling
- **RESTful API**: Clean API design with proper status codes and documentation

#### Getting Started

```bash
# Start the model registry services
make start-registry

# Install dependencies
pip install -r mlops/registry_requirements.txt
```

Example usage:
```python
from registry.client import ModelRegistryClient
from registry.schemas import ModelMetadata

# Initialize client
client = ModelRegistryClient("http://localhost:8000")

# Upload a model
response = client.upload_model(model_buffer, metadata)

# Retrieve model metadata
metadata = client.get_metadata("metadata_id")

# Download a model
model_buffer, metadata = client.get_model(
    file_path="path/to/model.pkl",
    metadata_id="metadata_id"
)
```

### 4. Feature Store

*(Coming Soon)*