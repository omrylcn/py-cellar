# Deployment Patterns with BentoML and Docker

This directory contains examples of BentoML deployment patterns using Docker Compose File


## Usage 

```bash	
docker build -t {IMAGE_NAME}:{TAG_NAME} .     # ml_service adında bir image oluşturur
                                       # '.' mevcut dizindeki Dockerfile'ı kullanır

docker run  -p 5000:5000 -e BENTOML_HOST=0.0.0.0 -e BENTOML_PORT=5000     -e BENTOML_WORKERS=2   {IMAGE_NAME}:{TAG_NAME}

```


#!/bin/bash
# run_ml_service.sh

# Eski container'ı temizle (eğer varsa)
docker rm -f ml_service 2>/dev/null

# Yeni container'ı başlat
docker run -d \
    --name ml_service \
    -p 3000:3000 \
    -e BENTOML_HOST=0.0.0.0 \
    -e BENTOML_PORT=3000 \
    -e BENTOML_WORKERS=2 \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/logs:/app/logs \
    ml_service:latest

# Container'ın başladığını kontrol et
echo "Waiting for service to start..."
sleep 5
curl http://localhost:3000/healthz