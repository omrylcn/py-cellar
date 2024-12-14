import pytest
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import pickle
import io
import sys
from datetime import datetime
from pathlib import Path

from registry.client import ModelRegistryClient
from registry.schemas import ModelMetadata

# PARAMETERS
REGISTRY_API_URL = "http://localhost:8000"



# Get the project root directory
project_root = Path(__file__).parent.parent

# Add the project root and mlkit directory to Python path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "registry"))



@pytest.fixture()
def get_host_url():
    return REGISTRY_API_URL

@pytest.fixture()
def get_client_lib():
    return ModelRegistryClient



@pytest.fixture(autouse=True)
async def cleanup(get_host_url, get_client_lib):
    """Cleanup test data after each test"""
    yield
    # Cleanup code would go here
    # Example: delete test models from storage
    client = get_client_lib(get_host_url)
    # Add cleanup logic

@pytest.fixture
def trained_model():
    """Create and train a simple ML model"""
    np.random.seed(42)
    X = np.random.rand(100, 2)
    y = np.random.randint(0, 2, 100)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = LogisticRegression()
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    
    model_buffer = io.BytesIO()
    pickle.dump(model, model_buffer)
    model_buffer.seek(0)
    
    return model_buffer, accuracy, (X_test, y_test)

@pytest.fixture
def model_metadata():
    return ModelMetadata(
        id="model123",
        name="example_model",
        version="1.0.0",
        file_extension="pkl",
        storage_group="ml-models",
        description="Example model for testing",
        framework="scikit-learn",
        metrics={"accuracy": 0.95},
        parameters={"n_estimators": 100},
        tags={"type": "classification", "key": "example"}
    )