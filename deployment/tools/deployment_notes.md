# Deploying Notes

```bash
## Export env packages
uv export --no-dev --extra {env_name} --no-hashes > requirements.txt

## Export all packages
uv export --all-packages  --no-hashes > mlops/requirements.txt

## Create shared network
docker network create mlops_network

## Start registry
docker compose -f docker-compose.registry.yaml up -d

## Start training
docker compose -f docker-compose.training.yaml up -d

## Test from ml-training container
docker exec mlkit curl <http://model-registry:8000/health>

## Test from registry container
docker exec model_registry curl <http://mlflow:5000/health>

## Environment file setup
cd mlops
cp ../.env .env

## Create registry image
docker build -f mlops/Dockerfile.registry -t registry .

## Create mlkit image
docker build -f mlops/Dockerfile.mlkit -t mlkit .

## Create API image
docker build -f mlops/Dockerfile.api -t api .

## Run container
docker run  -d -p 8000:8000 --name {container_name} {image_name}

```