# BT4301_Project

## Table of Contents
- [BT4301 Project Backend](#BT4301-Project-Backend)
  - [Table of Contents](#table-of-contents)
  <!-- - [Project Overview](#project-overview) -->
  - [Requirements](#Requirements)
  - [Project Structure](#project-structure)
  - [Notes](#notes)
  <!-- - [Installation](#installation-/-usage) -->
  - [Usage](#usage)
  - [Minikube & Services](#minikube--services)
    - [Starting Minikube Kubernetes Cluster](#starting-minikube-kubernetes-cluster)
    - [Enabling MLOps Suite Services](#enabling-mlops-suite-services)
      - [Enabling model_deployer service](#enabling-model_deployer-service)
    - [Stopping Minikube Kubernetes Cluster](#stopping-minikube-kubernetes-cluster)

## Requirements
1. Docker installed in your system
2. Docker-compose installed in your system
3. Minikube installed in your system

## Project Structure
```
.
├── backend                 <- Flask backend
│   ├── Dockerfile          <- for dockerising Flask backend
│   ├── main.py
│   ├── 
│   └── sql                 <- contains sql scripts
├── env.py                  <- connectors to database and other infrastructure
├── frontend                <- notebooks for explorations / prototyping
│   ├── xxx
│   └── xxx
├── model_deployment_template
│   ├── dockerfile          <- dockerfile definition for deployment base image
│   ├── main.py             <- FastAPI for model deployment
│   ├── model.py            <- template for user to submit model code
│   ├── model               <- model artifacts
│   └── requirments.txt
├── services
│   ├── direct              <- Kubernetes file templates for direct deployment
│   ├── mlops_files         <- File System of the MLOps application
│   ├── model_deployer.py   <- handles the deployment of models from the File System (includes building the image and Kubernetes deployment)
│   ├── outputs
│   ├── models
│   └── weights
├── xxx
└── docker-compose          <- docker compose file for MLOps Suite
```

## Notes

## Usage
1. Activate the virutal environment
    ```bash
    docker-compose up -d --build 
    ```

2. Connect to Postgres on PGAdmin
    - Host: localhost
    - Port: 5455
    - User: user
    - Password: password
    Keep the other settings as default
    DB available at `localhost:5455`

3. Backend API available at `localhost:5050`

4. Frontend available at `localhost:8080`

5. RabbitMQ available at `localhost:5672`. RabbitMQ Web UI available at `localhost:15672`

6. To shutdown the application, run the following command.
    ```bash
    docker-compose down
    ```

## Minikube & Services
### Starting Minikube Kubernetes Cluster
1. Start Minikube Kubernetes cluster
    ```bash
    minikube start
    ```
2. Check that Minikube Kubernetes cluster context exists
    ```bash
    kubectl config get-contexts
    ```
   If the cluster context exists, you should `minikube` in the first column.
3. Ensure that your Kubernetes CLI is using the right context
    ```bash
    kubectl config use-context minikube
    ```
4. Enable ingress on Minikube Kubernetes cluster
    ```bash
    minikube addons enable ingress
    ```
    Then `cd` into the main folder of the repository and run the following command.
    ```bash
    kubectl apply -f ingress-controller.yml
    ```  
5. Enable metrics tracking on Minikube Kubernetes cluster
    ```bash
    minikube addons enable metrics-server
    ```
    Then `cd` into the main folder of the repository and run the following command.
    ```bash
    kubectl apply -f metrics-server.yml
    ```  
6. To allow kubernetes cluster to be accessible from localhost, enable Kubernetes tunneling in a separate terminal**.
   > __Warning__ Please keep this command running when testing/using the application. It would hence be advisable to run this in a separate terminal.
    ```bash
    sudo minikube tunnel
    ```
    You would need to enter your password after running the command.

7. To access the docker daemon in the Minikube container, run the following command.
    ```bash
    eval $(minikube -p minikube docker-env)
    ```
    After which, the `docker` command would point to the docker daemon in the Minikube container.
    
    > __Note__ Deployments with `kubectl` will only be able to use docker images that are in the Minikube container.
    Therefore, you would have to build the docker images with the docker daemon in the Minikube container if
    you want to use those docker images for deployment in the Minikube cluster.
    
8. Build the mlops_base image for model deployment
    - Enter the model_deployment_template folder
      ```bash
      cd model_deployment_template
      ```
    - Build the mlops_base image
      ```bash
      docker build -t mlops_base:latest .
      ```
    - Check that the mlops_base image is created
      ```bash
      docker images
      ```

### Enabling MLOps Suite Services
1. Enter the `/services/` folder of the repository

2. Start the ingress for Project 1 
    ```bash
    kubectl apply -f ./direct/ingress.yml
    ```
    > __Note__ You can check that it has been created successfully by doing `kubectl get ingress`. Project 1's ingress should be shown.
3. Activate the virtual environment of the services
    ```bash
    source venv/bin/activate
    ```
4. Ensure that the `mlops_base` image is present in the docker daemon of the Minikube container
    - To check, run the following command. 
      > __Warning__ Make sure that your `docker` command already points to the docker daemon in the Minikube container. If you are unsure, refer to the instruction for step 6 of [Starting Minikube Kubernetes cluster](#starting-minikube-kubernetes-cluster) 
      ```bash
      docker images
      ```
      If the `mlops_base` image exist, it should be listed in the output
      
    - If not, then `cd` into the `/model_deployment_template` folder in the repository and run the following command.
      ```bash
      docker build -t mlops_base:latest .
      ```
5. Start the model_deployer
    ```bash
    ENV=DEV python model_deployer.py
    ```
6. Start the Drift Monitoring service
    ```bash
    ENV=DEV python data_drift.py
    ```
7. Start the Performance service
    ```bash
    ENV=DEV python performance_metrics.py
    ```
8. If you want to view the logs of model_deployer, Drift Monitoring service or Performance service
    ```bash
    tail -f /logs/model_deployer.log
    ```
    ```bash
    tail -f /logs/data_drift.log
    ```
    ```bash
    tail -f /logs/performance.log
    ```
    This would be useful for debugging if anything does not go as planned.

### Stopping Minikube Kubernetes Cluster
1. Stop Minikube Kubernetes cluster
    ```bash
    minikube stop
    ```
2. Shutdown Minikube tunnel by terminating the Minikube tunnel with the `Ctrl-C` command.
