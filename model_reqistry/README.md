# Model Registry

A lightweight, extensible registry for managing machine learning models with efficient storage and comprehensive metadata tracking.

## Overview

This Model Registry provides a centralized system for storing, versioning, and retrieving machine learning models. It's designed for MLOps workflows and offers both a REST API and a Python client for seamless integration.

## Architecture

The system follows a layered architecture with:

- **Client Layer**: Python client for easy integration
- **API Layer**: FastAPI endpoints for model operations
- **Service Layer**: Core registry logic
- **Storage Layer**: Dual storage with MinIO (model files) and MongoDB (metadata)

```mermaid
graph LR
    Client[Client] -->|Upload Model| API[FastAPI Service]
    
    subgraph Registry
        API -->|Store| Storage[Storage Layer]
        Storage -->|Models| Minio[MinIO]
        Storage -->|Metadata| Mongo[MongoDB]
    end

    classDef client fill:#ddd,stroke:#333
    classDef service fill:#bbf,stroke:#333
    classDef storage fill:#ddd,stroke:#333
    classDef database fill:#bfb,stroke:#333
    
    class Client client
    class API service
    class Storage storage
    class Minio,Mongo database
```

## Features

- **Model Storage**: Securely store model binary files using MinIO
- **Metadata Management**: Track model details, parameters, and metrics
- **Version Control**: Manage multiple versions of the same model
- **Streaming Support**: Efficient handling of large model files
- **Tagging System**: Add custom tags to models for better organization
- **Python Client**: Simple client with built-in error handling
- **REST API**: Complete API for model operations

## Getting Started

### 1. Start the Services

```bash
# Start all services using Docker Compose
make start
```

### 2. Install Dependencies

```bash
# Using pip
pip install -r mlops/registry_requirements.txt

# Or using uv
uv sync
```

### 3. Upload a Model

```python
from registry.client import ModelRegistryClient
from registry.schemas import ModelMetadata
import io
import pickle
from sklearn.linear_model import LogisticRegression

# Train a simple model
model = LogisticRegression()
model.fit(X_train, y_train)

# Serialize the model
model_buffer = io.BytesIO()
pickle.dump(model, model_buffer)
model_buffer.seek(0)

# Create client and upload
client = ModelRegistryClient("http://localhost:8000")
metadata = ModelMetadata(
    id="model123",
    name="example_model",
    version="1.0.0",
    file_extension="pkl",
    storage_group="ml-models",
    description="Example model",
    framework="scikit-learn",
    metrics={"accuracy": 0.95},
    parameters={"n_estimators": 100},
    tags={"type": "classification"}
)

response = client.upload_model(model_buffer, metadata)
print(f"Model uploaded with ID: {response.metadata_id}")
```

### 4. Retrieve a Model

```python
# Get model metadata
metadata = client.get_metadata("metadata_id")

# Download model file
model_buffer, metadata = client.get_model(
    file_path=metadata["storage_path"],
    metadata_id=metadata["_id"],
    bucket_name=metadata["storage_group"]
)

# Load the model
model = pickle.load(model_buffer)
```

## Configuration

The registry can be configured through environment variables or a `.env` file:

```env
# API Configuration
REGISTRY_PORT=8000

# MongoDB Configuration
MONGODB_URL=mongodb://root:root@localhost:27017
MONGODB_DB=metadata

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=models
```

## Development

```bash
# Run tests
pytest

# Format code
make format

# Lint code
make lint

# Clean Python cache files
make clean-file
```

## Directory Structure

```
registry/
├── api/                  # API endpoints
├── core/                 # Core registry configuration
├── storage/              # Storage implementations
│   ├── base.py           # Abstract interfaces
│   ├── minio.py          # MinIO implementation
│   └── mongo.py          # MongoDB implementation
├── app.py                # Main FastAPI application
├── client.py             # Python client
├── exceptions.py         # Error handling
├── schemas.py            # Data models
└── services.py           # Service layer
```

## Future Improvements

- Authentication and authorization
- Model validation hooks
- Web UI for model management
- Support for additional storage backends
- Model lineage tracking

## License

MIT License