# Model Registry

A lightweight, extensible model registry for machine learning models. This registry provides storage and versioning for ML models with metadata management.

## System Architecture

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

- 📦 Model artifact storage using MinIO
- 📝 Metadata management with MongoDB
- 🔄 Version tracking
- 🔍 Model search and retrieval
- 🧰 Easy-to-use Python client

## Quick Start

1. Start the services:

```bash
make start # start all services(docker-compose file)
```

2. Install the package:

```bash
pip install -e .
```

3. Use the client:

```python
# model upload example
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LogisticRegression()
model.fit(X_train, y_train)


model_buffer = io.BytesIO()
pickle.dump(model, model_buffer)
model_buffer.seek(0)

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
            tags={"type":"classification", "key":"example"}
        )
res = client.upload_model(model_buffer, metadata)

```

## Project Structure

```
registry
├── api                         # API package for handling HTTP endpoints
│   ├── __init__.py             
│   └── routes                  # Routes directory
│       └── models.py           # Model-related API endpoints
├── app.py                      # Main FastAPI application entry point
├── client.py                   # Client library for interacting with registry
├── core                        # Core functionality package
│   ├── config.py               # Configuration settings and environment variables
│   ├── dependencies.py         # Dependency injection and shared resources
│   └── registry.py             # Core registry implementation
├── exceptions.py               # Custom exception definitions
├── __init__.py                 
├── logger.py                   # Logging configuration
├── schemas.py                  # Pydantic models and data schemas
├── services.py                 # Service layer implementations
├── static                      # Static assets directory
│   ├── css                     # CSS styles directory
│   │   └── style.css           # Main stylesheet
│   └── index.html              # Main HTML template
├── storage                     # Storage implementations package
│   ├── base.py                 # Abstract storage interface
│   ├── minio.py                # MinIO storage implementation
│   └── mongo.py                # MongoDB storage implementation
├── util.py                     # Utility functions and helpers
└── version.py                  # Version information```

```

## Configuration

Set up using environment variables or `.env`:

```env
# registry API
REGISTRY_PORT=8000
REGISTRY_MINIO_PORT=9004
REGISTRY_MONGODB_PORT=27019

# MongoDB Configuration
MONGODB_PORT=27017
MONGODB_ROOT_USERNAME=root
MONGODB_ROOT_PASSWORD=root
MONGODB_HOST=localhost
MONGODB_URL=mongodb://root:root@localhost:27017
MONGODB_DB=metadata

# MinIO Configuration
MINIO_PORT=9000
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=models
```

## Development

Run tests:

```bash
pytest
```

## Future Improvements

- [ ] Add authentication
- [ ] Add model validation
- [ ] Add metrics visualization
- [ ] Support more storage backends

## License

MIT License
