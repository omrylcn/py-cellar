import pickle
import numpy as np

def test_create_client_intance(get_host_url, get_client_lib):
    client = get_client_lib(get_host_url)
    assert client, "Client instance created"


def test_connect_client(get_host_url, get_client_lib):
    client = get_client_lib(get_host_url)
    assert client.health_check(), "Connected to Model Registry"


def test_upload_ml_model(get_host_url, get_client_lib, trained_model, model_metadata):
    """Basic upload test"""
    client = get_client_lib(get_host_url)
    model_buffer, accuracy, _ = trained_model
    model_metadata.metrics["accuracy"] = float(accuracy)
    
    result = client.upload_model(model_buffer, model_metadata)
    assert result.name == model_metadata.name
    assert result.version == model_metadata.version


def test_download_model(get_host_url, get_client_lib, trained_model, model_metadata):
    """Download and test model"""
    client = get_client_lib(get_host_url)
    model_buffer, _, _ = trained_model
    
    # Upload
    result = client.upload_model(model_buffer, model_metadata)
    
    # Download
    downloaded_buffer, download_model_metadata = client.get_model(
        file_path=result.file_path,
        metadata_id=result.metadata_id
    )
    
    assert downloaded_buffer, "Downloaded model buffer is not empty"
    assert model_metadata.name == download_model_metadata["name"]



def test_model_prediction_consistency(get_host_url, get_client_lib, trained_model, model_metadata):
    """Test if model predictions are consistent after upload and download"""
    client = get_client_lib(get_host_url)
    model_buffer,_, (X_test, y_test) = trained_model
    
    # Get original predictions
    model_buffer.seek(0)
    original_model = pickle.loads(model_buffer.read())
    original_predictions = original_model.predict(X_test)
    
    # Reset buffer for upload
    model_buffer.seek(0)
    
    # Upload model
    result = client.upload_model(model_buffer, model_metadata)
    
    # Download model
    downloaded_buffer, metadata = client.get_model(
        file_path=result.file_path,
        metadata_id=result.metadata_id
    )
    
    # Load downloaded model and get predictions
    downloaded_model = pickle.loads(downloaded_buffer.getvalue())
    downloaded_predictions = downloaded_model.predict(X_test)
    
    # Compare predictions
    assert np.array_equal(original_predictions, downloaded_predictions),"Predictions before and after storage should match"
    