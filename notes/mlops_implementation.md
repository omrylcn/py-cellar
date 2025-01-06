# Comprehensive MLOps Framework and Implementation Guide

## 1. ML Pipeline Automation and CI/CD (25%)

The foundation of any mature MLOps implementation lies in robust automation and continuous integration/deployment pipelines. This section covers the essential components and best practices for building reliable ML pipelines.

### Core Technologies

#### Kubeflow Pipelines

Kubeflow Pipelines enables the orchestration of machine learning workflows on Kubernetes. It provides a platform for building and managing ML pipelines that are portable and scalable.

```python
from kfp import dsl
from kfp.components import func_to_container_op

@dsl.pipeline(
    name='Advanced Training Pipeline',
    description='End-to-end ML training pipeline with monitoring'
)
def training_pipeline(
    data_path: str,
    model_params: dict,
    validation_threshold: float = 0.85
):
    # Data preparation and validation
    with dsl.ExitHandler(exit_op=cleanup_op()):
        data_prep = data_preparation_op(
            data_path=data_path
        ).set_memory_request('4G')
        
        # Feature engineering with caching enabled
        feature_engineering = (feature_engineering_op(
            data=data_prep.outputs['processed_data']
        ).set_memory_limit('8G')
         .set_caching_options(enable_caching=True))
        
        # Model training with GPU acceleration
        training = (train_model_op(
            features=feature_engineering.outputs['features'],
            hyperparameters=model_params
        ).set_gpu_limit(1)
         .add_node_selector_constraint('cloud.google.com/gke-accelerator', 'nvidia-tesla-k80'))
        
        # Model validation and metrics logging
        with dsl.Condition(training.outputs['validation_accuracy'] > validation_threshold):
            deploy = deploy_model_op(
                model=training.outputs['model'],
                version=dsl.RUN_ID_PLACEHOLDER
            )
```

#### Apache Airflow

Airflow provides a platform for programmatically authoring, scheduling, and monitoring workflows. It's particularly valuable for orchestrating complex data processing and model training pipelines.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'mlops_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'ml_training_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['ml', 'training']
)

def validate_data_quality(**context):
    from great_expectations.data_context import DataContext
    context = DataContext()
    results = context.run_checkpoint(
        checkpoint_name="data_quality_checkpoint"
    )
    if not results["success"]:
        raise Exception("Data quality validation failed")

with dag:
    data_validation = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data_quality,
        provide_context=True
    )
    
    feature_engineering = PythonOperator(
        task_id='feature_engineering',
        python_callable=process_features
    )
    
    model_training = PythonOperator(
        task_id='train_model',
        python_callable=train_model
    )
    
    data_validation >> feature_engineering >> model_training
```

#### MLflow

MLflow provides comprehensive experiment tracking, model registry, and deployment capabilities. It's essential for maintaining reproducibility and version control of ML experiments.

```python
import mlflow
from mlflow.tracking import MlflowClient

def train_with_mlflow(data, params):
    mlflow.set_experiment("production_model_training")
    
    with mlflow.start_run(run_name="training_run") as run:
        # Log input parameters
        mlflow.log_params(params)
        
        # Log dataset information
        mlflow.log_param("data_version", data.version)
        mlflow.log_param("data_shape", data.shape)
        
        # Train model
        model = train_model(data, params)
        
        # Log metrics
        metrics = evaluate_model(model, data.test)
        mlflow.log_metrics(metrics)
        
        # Log model artifacts
        mlflow.sklearn.log_model(
            model, 
            "model",
            registered_model_name="production_model"
        )
        
        # Log feature importance plot
        fig = plot_feature_importance(model)
        mlflow.log_figure(fig, "feature_importance.png")
        
        return run.info.run_id
```

### Best Practices for Pipeline Automation

1. Immutable and Reproducible Pipelines
   - Version control all pipeline configurations
   - Use deterministic operations
   - Implement comprehensive logging
   - Store pipeline metadata

2. Modular Pipeline Design
   - Create reusable components
   - Implement clear interfaces between stages
   - Enable parallel execution where possible
   - Handle failures gracefully

3. Continuous Training Strategy
   - Implement automated retraining triggers
   - Monitor data drift
   - Maintain model performance metrics
   - Version control for models and data

## 2. Model Monitoring and Operations (20%)

Effective model monitoring ensures the continued reliability and performance of deployed models in production.

### Implementation Example with Prometheus and Grafana

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: model-monitoring
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: ml-model
  endpoints:
  - port: metrics
    interval: 15s
    path: /metrics
  - port: custom-metrics
    interval: 30s
    path: /model-metrics
    metricRelabelings:
    - sourceLabels: [__name__]
      regex: 'model_prediction_.*'
      action: keep
```

### Custom Metrics Implementation

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
prediction_counter = Counter(
    'model_predictions_total',
    'Total number of predictions',
    ['model_version', 'prediction_class']
)

prediction_latency = Histogram(
    'model_prediction_latency_seconds',
    'Time spent processing prediction',
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

feature_drift = Gauge(
    'model_feature_drift',
    'Feature drift score',
    ['feature_name']
)

def predict_with_monitoring(features):
    with prediction_latency.time():
        prediction = model.predict(features)
        
    prediction_counter.labels(
        model_version=model.version,
        prediction_class=str(prediction)
    ).inc()
    
    # Monitor feature drift
    for feature_name, value in features.items():
        drift_score = calculate_drift(feature_name, value)
        feature_drift.labels(feature_name=feature_name).set(drift_score)
    
    return prediction
```

## 3. Infrastructure and Platform Integration (15%)

A robust infrastructure foundation is crucial for scaling ML operations effectively. This section covers the essential components of a production-grade ML infrastructure.

### Kubernetes-Based Infrastructure

The following example demonstrates a production-ready Kubernetes configuration for ML workloads:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-serving
  labels:
    app: ml-inference
spec:
  replicas: 3
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: ml-inference
  template:
    metadata:
      labels:
        app: ml-inference
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
    spec:
      containers:
      - name: model-server
        image: model-server:v1
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "8Gi"
            cpu: "4"
          requests:
            memory: "4Gi"
            cpu: "2"
        ports:
        - containerPort: 8080
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        volumeMounts:
        - name: model-storage
          mountPath: /models
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-pvc
```

### GPU Resource Management with NVIDIA Triton

Here's an example of configuring Triton Inference Server for efficient GPU utilization:

```python
import tritonclient.grpc as grpcclient
from tritonclient.utils import InferenceServerException

class TritonModelServer:
    def __init__(self, url="localhost:8001"):
        self.client = grpcclient.InferenceServerClient(url=url)
        
    def load_model(self, model_name, model_version="1"):
        try:
            self.client.load_model(model_name)
            model_config = self.client.get_model_config(model_name, model_version)
            return True, model_config
        except InferenceServerException as e:
            return False, str(e)
    
    def get_inference(self, input_data, model_name):
        inputs = [
            grpcclient.InferInput(
                "input_1", input_data.shape, "FP32"
            )
        ]
        inputs[0].set_data_from_numpy(input_data)
        
        outputs = [
            grpcclient.InferRequestedOutput("output_1")
        ]
        
        response = self.client.infer(
            model_name=model_name,
            inputs=inputs,
            outputs=outputs
        )
        return response.as_numpy("output_1")
```

### Auto-scaling Configuration with HorizontalPodAutoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-serving
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: inference_queue_length
      target:
        type: AverageValue
        averageValue: 100
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Pods
        value: 2
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
```

## 4. Data Management (15%)

Effective data management is crucial for maintaining model performance and ensuring reproducibility. This section covers the implementation of feature stores and data processing pipelines.

### Feature Store Implementation with Feast

```python
from feast import Entity, Feature, FeatureView, FileSource, ValueType
from feast.types import Float32, Int64
from datetime import timedelta

# Define an entity for our ML features
driver = Entity(
    name="driver",
    value_type=ValueType.INT64,
    description="Driver ID"
)

# Define our feature data source
driver_stats_source = FileSource(
    path="data/driver_stats.parquet",
    event_timestamp_column="event_timestamp",
)

# Create a Feature View
driver_stats_fv = FeatureView(
    name="driver_stats_fv",
    entities=["driver"],
    ttl=timedelta(hours=24),
    features=[
        Feature(name="conv_rate", dtype=Float32),
        Feature(name="acc_rate", dtype=Float32),
        Feature(name="avg_daily_trips", dtype=Int64),
    ],
    batch_source=driver_stats_source,
    online=True
)

# Feature retrieval example
def get_online_features(driver_ids):
    return store.get_online_features(
        features=[
            "driver_stats_fv:conv_rate",
            "driver_stats_fv:acc_rate",
            "driver_stats_fv:avg_daily_trips"
        ],
        entity_rows=[{"driver": driver_id} for driver_id in driver_ids]
    )
```

### Real-time Feature Processing with Apache Kafka

```python
from confluent_kafka import Producer, Consumer, KafkaError
import json

class FeatureProcessor:
    def __init__(self, bootstrap_servers):
        self.producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            'client.id': 'feature_processor'
        })
        
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'feature_processor_group',
            'auto.offset.reset': 'earliest'
        })
    
    def process_features(self, raw_data):
        processed_features = self._transform_features(raw_data)
        
        self.producer.produce(
            topic='processed_features',
            key=str(raw_data['id']),
            value=json.dumps(processed_features),
            callback=self._delivery_report
        )
        self.producer.flush()
    
    def _transform_features(self, raw_data):
        # Feature transformation logic
        return {
            'id': raw_data['id'],
            'normalized_features': [
                (x - self.feature_means[i]) / self.feature_stds[i]
                for i, x in enumerate(raw_data['features'])
            ],
            'timestamp': raw_data['timestamp']
        }
    
    def _delivery_report(self, err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')
```

## 5. ML Platform Development (15%)

A well-designed ML platform enables data scientists and ML engineers to work efficiently while maintaining production standards.

### FastAPI-based Model Serving Interface

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import numpy as np
from prometheus_client import Counter, Histogram
import time

app = FastAPI(title="ML Model Service")

# Define request/response models
class PredictionRequest(BaseModel):
    features: List[float]
    metadata: Dict[str, str] = {}

class PredictionResponse(BaseModel):
    prediction: float
    confidence: float
    processing_time: float

# Metrics
PREDICTION_REQUEST_COUNT = Counter(
    'prediction_requests_total',
    'Total prediction requests'
)

PREDICTION_LATENCY = Histogram(
    'prediction_latency_seconds',
    'Prediction latency in seconds'
)

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    start_time = time.time()
    PREDICTION_REQUEST_COUNT.inc()
    
    try:
        # Input validation
        features = np.array(request.features)
        if features.shape[0] != MODEL_INPUT_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Expected {MODEL_INPUT_SIZE} features, got {features.shape[0]}"
            )
        
        # Make prediction
        with PREDICTION_LATENCY.time():
            prediction = model.predict(features)
            confidence = model.predict_proba(features).max()
        
        processing_time = time.time() - start_time
        
        return PredictionResponse(
            prediction=float(prediction),
            confidence=float(confidence),
            processing_time=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 6. Security and Compliance (10%)

Security is paramount in ML systems, particularly when dealing with sensitive data and model access.

### Secure Model Serving with Authentication

```python
from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Security configurations
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401)
        return username
    except JWTError:
        raise HTTPException(status_code=401)

@app.post("/secure-predict")
async def secure_predict(
    request: PredictionRequest,
    current_user: str = Depends(get_current_user)
):
    # Log the authenticated request
    logger.info(f"Prediction request from user: {current_user}")
    
    # Proceed with prediction
    return await predict(request)
```

### Audit Logging Implementation

```python
import structlog
from datetime import datetime

logger = structlog.get_logger()

class AuditLogger:
    def __init__(self):
        self.logger = structlog.wrap_logger(
            logger,
            processor=structlog.processors.JSONRenderer()
        )
    
    def log_prediction(self, user, model_version, features, prediction, metadata=None):
        self.logger.info(
            "model_prediction",
            timestamp=datetime.utcnow().isoformat(),
            user=user,
            model_version=model_version,
            feature_hash=hash(str(features)),
            prediction=prediction,
            metadata=metadata or {}
        )
    
    def log_model_update(self, model_version, update_user, update_reason):
        self.logger.info(
            "model_update",
            timestamp=datetime.utcnow().isoformat(),
            model_version=model_version,
            update_user=update_user,
            update_reason=update_reason
        )

# Usage example
audit_logger = AuditLogger()
audit_logger.log_prediction(
    user="data_scientist_1",
    model_version="v1.2.3",
    features=processed_features,
    prediction=model_output,
    metadata={"environment": "production"}
)
```

This completes our comprehensive MLOps framework with detailed implementations across all major components. Each section includes production-ready code examples and best practices for implementation. The framework can be adapted and scaled based on specific organizational needs while maintaining security, reliability, and efficiency.
