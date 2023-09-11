# BT4301_Project Services

### Containerize the model by generating the application image
1. docker build -t kubernetes-models .
2. docker run kubernetes-models python3 model.py 

### Upload the model to Docker Hub
3. docker tag kubernetes-models:latest <insert-docker-hub-id>/kubernetes-models:latest
4. docker push <insert-docker-hub-id>/kubernetes-models:latest

### Deploying to Kubernetes service
5. docker run kubernetes-models python3 model.py OR kubectl apply -f deployment.yaml
