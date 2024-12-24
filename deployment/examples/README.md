# Explanations


## How to run

```bash
# export requirements.txt
uv export --no-dev --no-hashes > requirements.txt

# to run in minikube
minikube tunnel 

# to add docker image to minikube registry
eval $(minikube -p minikube docker-env)

# to build docker image
docker build -t python-fastapi:latest .
# docker build --no-cache -t python-fastapi:latest .

#run kubectl    
kubectl apply -f deployment.yaml

```
