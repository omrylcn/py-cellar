![test](pipeline.svg)

1. Development/Experiment -> Source code:

- Bu CI sürecinin başlangıcı
- Kod geliştirme ve deneysel çalışmalar

1. Source code -> Pipeline continuous integration:

- Klasik CI süreci
- Kod kalite kontrolleri, testler

1. Packages -> Pipeline continuous delivery:

- Paketleme süreci
- Deployment için hazırlık
- Artifact oluşturma

1. Automated pipeline + Newdata -> Continuous training:

- Model eğitim pipeline'ı
- Yeni data ile sürekli eğitim
- Bu aşama CI/CD'den bağımsız

1. Trained model -> Model continuous delivery:

- Eğitilen modelin deployment süreci
- Model artifactlarının dağıtımı

1. Prediction service -> Monitoring:

- Servise alınan modelin izlenmesi
- Performans metrikleri takibi
- Geri besleme döngüsü

Önemli Noktalar:

- CI ve CD süreçleri ayrı pipeline'larda
- Model eğitimi ana CI/CD'den bağımsız
- Monitoring ile sürekli feedback
- Döngüsel bir yapı (monitoring'den development'a geri besleme)

Bu yapı MLOps'ta tercih edilen modern bir yaklaşımı temsil ediyor çünkü:

- Model yaşam döngüsünü otomatize ediyor
- Sürekli iyileştirme imkanı sunuyor
- Data, kod ve model versiyonlamayı destekliyor
- Üretim ortamında monitoring ile güvenli deployment sağlıyor

Bu MLOps pipeline'ını adım adım nasıl kurabileceğimizi açıklayayım:

1. Development/Experiment -> Source Code:

```python
# experiment.py
import mlflow

def experiment():
    mlflow.set_experiment("model_development")
    with mlflow.start_run():
        # Model denemeleri
        mlflow.log_metrics({"accuracy": score})
        mlflow.log_model(model, "model")
```

2. Pipeline Continuous Integration:

```yaml
# .gitlab-ci.yml
ci_pipeline:
  stage: ci
  script:
    # Kod kalite kontrolleri
    - pylint src/
    - black src/
    
    # Unit testler
    - pytest tests/
    
    # Integration testler
    - python integration_tests.py
    
    # Build artifacts
    - python setup.py bdist_wheel
```

3. Continuous Delivery Pipeline:

```yaml
# .gitlab-ci.yml
delivery_pipeline:
  stage: delivery
  script:
    # Docker image build
    - docker build -t ml-api:${CI_COMMIT_SHA} .
    
    # Push to registry
    - docker push registry/ml-api:${CI_COMMIT_SHA}
    
    # Deploy to staging
    - kubectl apply -f k8s/staging/
```

4. Automated Training Pipeline:

```python
# training_pipeline.py
from kedro.pipeline import Pipeline

def create_training_pipeline():
    return Pipeline([
        node(
            func=preprocess_data,
            inputs="raw_data",
            outputs="processed_data"
        ),
        node(
            func=train_model,
            inputs="processed_data",
            outputs="trained_model"
        ),
        node(
            func=evaluate_model,
            inputs="trained_model",
            outputs="model_metrics"
        )
    ])
```

5. Model Continuous Delivery:

```yaml
# k8s/model-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: model-service
        image: registry/ml-api:latest
        ports:
        - containerPort: 8000
```

6. Prediction Service & Monitoring:

```python
# app.py
from fastapi import FastAPI
from prometheus_client import Counter, Histogram

app = FastAPI()
prediction_counter = Counter('predictions_total', 'Total predictions')
model_latency = Histogram('prediction_latency', 'Prediction latency')

@app.post("/predict")
async def predict(data: PredictionInput):
    prediction_counter.inc()
    with model_latency.time():
        prediction = model.predict(data)
    return {"prediction": prediction}
```

Gerekli Araçlar ve Teknolojiler:

1. Version Control:

- Git
- DVC (data versiyonlama)

2. CI/CD Tools:

- GitLab CI/CD veya GitHub Actions
- Jenkins
- ArgoCD

3. Container & Orchestration:

- Docker
- Kubernetes

4. ML Tools:

- MLflow (model tracking)
- Kedro (pipeline orchestration)
- Kubeflow (Kubernetes ML toolkit)

5. Monitoring:

- Prometheus
- Grafana
- ELK Stack

Örnek Monitoring Dashboard:

```yaml
# grafana-dashboard.json
{
  "dashboard": {
    "panels": [
      {
        "title": "Model Latency",
        "type": "graph",
        "metrics": ["prediction_latency"]
      },
      {
        "title": "Prediction Count",
        "type": "counter",
        "metrics": ["predictions_total"]
      },
      {
        "title": "Model Accuracy",
        "type": "gauge",
        "metrics": ["model_accuracy"]
      }
    ]
  }
}
```

Bu yapıyı kurarken dikkat edilmesi gerekenler:

1. Infrastructure as Code (IaC) kullanımı
2. Automated testing stratejisi
3. Model versiyonlama ve rollback mekanizması
4. Monitoring ve alerting yapılandırması
5. Security best practices
6. Resource management ve scaling stratejisi
