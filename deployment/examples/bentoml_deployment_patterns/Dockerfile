# Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/data /app/logs /app/models
COPY src /app/src
COPY config /app/config
#COPY models /app/models 
COPY  bentofile.yaml /app/bentofile.yaml
COPY  .env /app/.


# BentoML environment variables
ENV BENTOML_HOST="0.0.0.0"
ENV BENTOML_PORT="3000"
ENV BENTOML_WORKERS="2"
ENV BENTOML_BACKLOG="2048"
ENV BENTOML_WORKING_DIR="/app"
ENV CONFIG_YAML_PATH="config/config.yaml"
EXPOSE ${BENTOML_PORT}

CMD ["bentoml", "serve", ".", "--production"]