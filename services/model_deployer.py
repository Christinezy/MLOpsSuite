
import docker
from kubernetes import client as kub_client
from kubernetes import config
from kubernetes.client import configuration
from kubernetes import utils
from kubernetes.client.rest import ApiException
import os
import sys
import subprocess
import yaml
import re
import time
from datetime import datetime
from contextlib import contextmanager
import json
import logging

from database import DB_session
import models

import pika

curr_dir = os.getcwd()

FILE_SYSTEM = os.path.join(curr_dir, "mlops_files")
DIRECT = os.path.join(curr_dir, "direct")
BLUE_GREEN = os.path.join(curr_dir, "bluegreen")
CANARY = os.path.join(curr_dir, "canary")

DIRECT_DOCKERFILE = os.path.join(DIRECT, "dockerfile")
# DIRECT_DEPLOY_YAML = None

# with open(os.path.join(DIRECT, "deploy_blue.yml") as file:
#     DIRECT_DEPLOY_YAML = yaml.safe_load(file)

# docker_client = docker.from_env()

ENV = os.environ.get('ENV')

PROD = os.environ.get('PROD')

# RabitMQ
if ENV == "DEV":
    rabbitmq_url = 'amqp://user:password@localhost'
else:
    rabbitmq_url = 'amqp://user:password@rabbitmq'

if PROD == "DEV":
    config.load_kube_config(context='minikube')
else:
    config.load_kube_config(config_file="/home/vboxuser/.kube/config")

port = 	5672
vhost = '/%2F'

rabbitmq_url_param = pika.URLParameters(f"{rabbitmq_url}:{port}{vhost}")
rabbitmq_client = pika.BlockingConnection(
    rabbitmq_url_param
)

formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
handler = logging.FileHandler(filename='logs/model_deployer.log', mode='w')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)


# CANARY_TRAFFIC_STEPS = [10, 25, 50, 75, 100]




@contextmanager
def config_docker_to_minikube():
    # output = subprocess.run("minikube -p minikube docker-env", capture_output=True, shell=True)
    # logging.error(output)
    # data = list(map(lambda x: x.decode("utf-8"), output.stdout.splitlines()))[:4]
    
    # ls = output.split()
    # print(data)
    if PROD == "DEV":
        output = subprocess.run("minikube -p minikube docker-env", capture_output=True, shell=True)
        data = list(map(lambda x: x.decode("utf-8"), output.stdout.splitlines()))[:4]
        # ls = output.split()
        # print(data)
        docker_host = data[1].split("=")[1].replace('"', '')
        docker_cert_path = data[2].split("=")[1].replace('"', '')
    else:
        docker_host = "tcp://192.168.49.2:2376"
        docker_cert_path = "/home/vboxuser/.minikube/certs"

    # print(docker_cert_path, type(docker_cert_path))
    # print(os.path.join(docker_cert_path, "ca.pem"))
    tls_config = docker.tls.TLSConfig(
        ca_cert = os.path.join(docker_cert_path, "ca.pem"),
        client_cert = (os.path.join(docker_cert_path, "cert.pem"), os.path.join(docker_cert_path, "key.pem")),
        verify = True
    )

    try:
        docker_client = docker.DockerClient(docker_host, tls = tls_config)
        print("[INFO] Successfully connected to minikube docker")
        logger.info("[INFO] Successfully connected to minikube docker")
        yield docker_client
    except Exception as err:
        print("[ERROR] Failed to connect to docker")
        print(err)
        logger.error('[ERROR] Failed to connect to docker')
        logger.exception(err)
    # else:
    #     print(docker_client.images.list())
    finally:
        docker_client.close()
        print("[INFO] Closed minikube docker")
        logger.info('[INFO] Closed minikube docker')

@contextmanager
def open_rabbitmq_connection():
    counter = 0
    while True:
        try: 
            channel = rabbitmq_client.channel()
        except Exception as err:
            logger.info(f"[ERROR] Failed to connect to RabbitMQ. Attempt number {counter}")
            sys.stderr.write(f"[ERROR] Failed to connect to RabbitMQ. Attempt number {counter}")
            raise err
        else:
            logger.info(f"[INFO] Successfully connected to RabbitMQ. Attempt number {counter}")
            break
    try:
        yield channel
    finally:
        channel.close()
        print("[INFO] Closed RabbitMQ", flush=True)
        logger.info("[INFO] Closed RabbitMQ")


@contextmanager
def open_db_session():
    session = DB_session()
    try:
        print("[INFO] Successfully connected to PostgreSQL")
        logger.info("[INFO] Successfully connected to PostgreSQL")
        yield session
    except Exception as err:
        print("[ERROR] Failed to connect to PostgreSQL")
        print(err)
        logger.error('[ERROR] Failed to connect to PostgreSQL')
        logger.exception(err)
    # else:
    #     print(docker_client.images.list())
    finally:
        session.close()
        print("[INFO] Closed session PostgreSQL")
        logger.info('[INFO] Closed session PostgreSQL')

def convert_cat_to_int(lst):
    d = {x: i for i, x in enumerate(set(lst))}
    lst_new = [d[x] for x in lst]
    return lst_new




def build_image(docker_client, project_id, version):
    project_str = f"project_{project_id}"
    version_str = f"version_{version}"
    PROJECT_DIR = os.path.join(FILE_SYSTEM, project_str)
    VERSION_DIR = os.path.join(PROJECT_DIR, version_str)
    # print(PROJECT_DIR, VERSION_DIR)
    try: 
        assert os.path.isdir(PROJECT_DIR) == True
        assert os.path.isdir(VERSION_DIR) == True

        requirement_file_path = os.path.join(VERSION_DIR, 'requirements.txt')
        model_file_path = os.path.join(VERSION_DIR, 'model.py')

        assert os.path.isfile(requirement_file_path) == True
        assert os.path.isfile(model_file_path) == True

        # print(requirement_file_path, model_file_path)

        model_image = docker_client.images.build(
            path = VERSION_DIR,
            dockerfile = DIRECT_DOCKERFILE,
            tag = f"mlops_{project_str}:latest"
        )

        return model_image[0]

    except Exception as err:
        print(err) 


def get_pod_name(core_v1,pod_namespace,pod_regex):    
    ret = core_v1.list_namespaced_pod(pod_namespace)
    for i in ret.items:
        #print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
        pod_name=i.metadata.name
        if re.match(pod_regex, pod_name):
            return pod_name

def check_pod_existance(api_instance,pod_namespace,pod_name):
    resp = None
    try:
        resp = api_instance.read_namespaced_pod(name=pod_name,namespace=pod_namespace)
    except ApiException as e:
        if e.status != 404:
            print("Unknown error: %s" % e)
            logger.error("Unknown error: %s" % e)
            exit(1)
    if not resp:
        print("Pod %s does not exist. Create it..." % pod_name)
        logger.info("Pod %s does not exist. Create it..." % pod_name)


def create_deployment(project_id, deployment_type="blue", path_suffix = ""):
    project_str = f"project_{project_id}"
    image_str = f"mlops_{project_str}:latest"

    deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}"
    # metadata_name = f"mlops-project-{project_id}-{deployment_type}"
    container_name = f"mlops-project-{project_id}-container-{deployment_type}"

    api_path = f"/project{project_id}"

    if path_suffix != "":
        api_path = api_path + f"-{path_suffix}"

    with open(os.path.join(DIRECT, "deploy_blue.yml"), "r") as file:
        deploy_yaml = yaml.safe_load(file)
    
    # print(deploy_yaml)

    # Make the changes
    deploy_yaml['metadata']['name'] = deployment_name
    deploy_yaml['spec']['selector']["matchLabels"]['app'] = deployment_name
    deploy_yaml['spec']['template']['metadata']['labels']['app'] = deployment_name
    deploy_yaml['spec']['template']['spec']['containers'][0]['name'] = container_name
    deploy_yaml['spec']['template']['spec']['containers'][0]['image'] = image_str
    deploy_yaml['spec']['template']['spec']['containers'][0]['env'][0]['value'] = api_path
    

    # print("================")
    # print(deploy_yaml)
    
    # config.load_kube_config_kube_config(context="minikube")
    k8s_client = kub_client.ApiClient()
    utils.create_from_dict(k8s_client, deploy_yaml, namespace='default', 
        # verbose=True
    )


def update_deployment(project_id, deployment_type="blue", path_suffix = ""):
    project_str = f"project_{project_id}"
    image_str = f"mlops_{project_str}:latest"

    deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}"

    # metadata_name = f"mlops-project-{project_id}-{deployment_type}"
    container_name = f"mlops-project-{project_id}-container-{deployment_type}"

    api_path = f"/project{project_id}"

    if path_suffix != "":
        api_path = api_path + f"-{path_suffix}"

    with open(os.path.join(DIRECT, "deploy_blue.yml"), "r") as file:
        deploy_yaml = yaml.safe_load(file)
    
    # print(deploy_yaml)

    # Make the changes
    deploy_yaml['metadata']['name'] = deployment_name
    deploy_yaml['spec']['selector']["matchLabels"]['app'] = deployment_name
    deploy_yaml['spec']['template']['metadata']['labels']['app'] = deployment_name
    deploy_yaml['spec']['template']['spec']['containers'][0]['name'] = container_name
    deploy_yaml['spec']['template']['spec']['containers'][0]['image'] = image_str
    deploy_yaml['spec']['template']['spec']['containers'][0]['env'][0]['value'] = api_path
    

    # print("================")
    # print(deploy_yaml)
    
    # config.load_kube_config_kube_config(context="minikube")
    # k8s_client = kub_client.ApiClient()
    api_instance = kub_client.AppsV1Api()
    api_instance.patch_namespaced_deployment(deployment_name, "default", deploy_yaml)


# def update_deployment(project_id, deployment_type="blue", path_suffix = "", change_deployment_name = False):
#     project_str = f"project_{project_id}"
#     image_str = f"mlops_{project_str}:latest"

#     deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}"

#     if change_deployment_name and deployment_type == "blue":
#         new_deployment_name = f"mlops-project-{project_id}-deployment-green"
#         new_container_name = f"mlops-project-{project_id}-container-green"
#     elif change_deployment_name and deployment_type == "green":
#         new_deployment_name = f"mlops-project-{project_id}-deployment-blue"
#         new_container_name = f"mlops-project-{project_id}-container-blue"

#     # metadata_name = f"mlops-project-{project_id}-{deployment_type}"
#     container_name = f"mlops-project-{project_id}-container-{deployment_type}"

#     api_path = f"/project{project_id}"

#     if path_suffix != "":
#         api_path = api_path + f"-{path_suffix}"

#     with open(os.path.join(DIRECT, "deploy_blue.yml"), "r") as file:
#         deploy_yaml = yaml.safe_load(file)
    
#     # print(deploy_yaml)

#     # Make the changes
#     deploy_yaml['metadata']['name'] = new_deployment_name if change_deployment_name else deployment_name
#     deploy_yaml['spec']['selector']["matchLabels"]['app'] = new_deployment_name if change_deployment_name else deployment_name
#     deploy_yaml['spec']['template']['metadata']['labels']['app'] = new_deployment_name if change_deployment_name else deployment_name
#     deploy_yaml['spec']['template']['spec']['containers'][0]['name'] = new_container_name if change_deployment_name else container_name
#     deploy_yaml['spec']['template']['spec']['containers'][0]['image'] = image_str
#     deploy_yaml['spec']['template']['spec']['containers'][0]['env'][0]['value'] = api_path
    

#     # print("================")
#     # print(deploy_yaml)
    
#     # config.load_kube_config_kube_config(context="minikube")
#     # k8s_client = kub_client.ApiClient()
#     api_instance = kub_client.AppsV1Api()
#     api_instance.patch_namespaced_deployment(deployment_name, "default", deploy_yaml)


def delete_deployment(project_id, deployment_type = "blue"):
    project_name = f"mlops-project-{project_id}-deployment-{deployment_type}"

    # Delete pod
    # config.load_kube_config_kube_config(context="minikube")
    api_instance = kub_client.AppsV1Api()

    api_instance.delete_namespaced_deployment(project_name, namespace='default')


def create_hpa(project_id, deployment_type="blue"):
    project_str = f"project_{project_id}"
    image_str = f"mlops_{project_str}:latest"

    hpa_name = f"mlops-project-{project_id}-hpa-{deployment_type}"

    deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}"
    # metadata_name = f"mlops-project-{project_id}-{deployment_type}"
    # container_name = f"mlops-project-{project_id}-container-{deployment_type}"

    # api_path = f"/project{project_id}"

    with open(os.path.join(DIRECT, "hpa.yml"), "r") as file:
        hpa_yaml = yaml.safe_load(file)
    
    # print(deploy_yaml)

    # Make the changes
    hpa_yaml['metadata']['name'] = hpa_name
    hpa_yaml['spec']['scaleTargetRef']["name"] = deployment_name
    # hpa_yaml['spec']['template']['metadata']['labels']['app'] = deployment_name
    # hpa_yaml['spec']['template']['spec']['containers'][0]['name'] = container_name
    # hpa_yaml['spec']['template']['spec']['containers'][0]['image'] = image_str
    # hpa_yaml['spec']['template']['spec']['containers'][0]['env'][0]['value'] = api_path
    

    # print("================")
    # print(hpa_yaml)
    
    # config.load_kube_config_kube_config(context="minikube")
    api_client = kub_client.AutoscalingV2Api()
    # utils.create_from_dict(api_client, hpa_yaml, namespace='default', 
    #     # verbose=True
    # )

    # body = kub_client.V2HorizontalPodAutoscaler()
    # print(body)

    # print("======")
    # print(hpa_yaml)


    api_client.create_namespaced_horizontal_pod_autoscaler('default', hpa_yaml)


def update_hpa(project_id, deployment_type="blue", min_pods = 1, max_pods = 3, desired_pods = 1):
    project_str = f"project_{project_id}"
    image_str = f"mlops_{project_str}:latest"

    hpa_name = f"mlops-project-{project_id}-hpa-{deployment_type}"

    deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}"
    # metadata_name = f"mlops-project-{project_id}-{deployment_type}"
    # container_name = f"mlops-project-{project_id}-container-{deployment_type}"

    # if change_deployment_name and deployment_type == "blue":
    #     new_deployment_name = f"mlops-project-{project_id}-deployment-green"
    #     new_hpa_name = f"mlops-project-{project_id}-hpa-green"
    # elif change_deployment_name and deployment_type == "green":
    #     new_deployment_name = f"mlops-project-{project_id}-deployment-blue"
    #     new_hpa_name = f"mlops-project-{project_id}-hpa-blue"

    # api_path = f"/project{project_id}"

    with open(os.path.join(DIRECT, "hpa.yml"), "r") as file:
        hpa_yaml = yaml.safe_load(file)
    
    # print(deploy_yaml)

    # Make the changes
    hpa_yaml['metadata']['name'] = hpa_name
    hpa_yaml['spec']['scaleTargetRef']["name"] = deployment_name
    hpa_yaml['spec']['minReplicas'] = min_pods
    hpa_yaml['spec']['maxReplicas'] = max_pods
    # hpa_yaml['spec']['template']['metadata']['labels']['app'] = deployment_name
    # hpa_yaml['spec']['template']['spec']['containers'][0]['name'] = container_name
    # hpa_yaml['spec']['template']['spec']['containers'][0]['image'] = image_str
    # hpa_yaml['spec']['template']['spec']['containers'][0]['env'][0]['value'] = api_path
    
    # config.load_kube_config_kube_config(context="minikube")
    api_client = kub_client.AutoscalingV2Api()

    api_client.patch_namespaced_horizontal_pod_autoscaler(hpa_name, 'default', hpa_yaml)


# def update_hpa_name(project_id, deployment_type="blue", change_deployment_name = False):
#     project_str = f"project_{project_id}"
#     image_str = f"mlops_{project_str}:latest"

#     hpa_name = f"mlops-project-{project_id}-hpa-{deployment_type}"

#     deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}"
#     # metadata_name = f"mlops-project-{project_id}-{deployment_type}"
#     # container_name = f"mlops-project-{project_id}-container-{deployment_type}"

#     if change_deployment_name and deployment_type == "blue":
#         new_deployment_name = f"mlops-project-{project_id}-deployment-green"
#         new_hpa_name = f"mlops-project-{project_id}-hpa-green"
#     elif change_deployment_name and deployment_type == "green":
#         new_deployment_name = f"mlops-project-{project_id}-deployment-blue"
#         new_hpa_name = f"mlops-project-{project_id}-hpa-blue"

#     # api_path = f"/project{project_id}"

#     with open(os.path.join(DIRECT, "hpa.yml"), "r") as file:
#         hpa_yaml = yaml.safe_load(file)
    
#     # print(deploy_yaml)

#     # Make the changes
#     hpa_yaml['metadata']['name'] = new_hpa_name if change_deployment_name else hpa_name
#     hpa_yaml['spec']['scaleTargetRef']["name"] = new_deployment_name if change_deployment_name else deployment_name
#     # hpa_yaml['spec']['minReplicas'] = min_pods
#     # hpa_yaml['spec']['maxReplicas'] = max_pods
#     # hpa_yaml['spec']['template']['metadata']['labels']['app'] = deployment_name
#     # hpa_yaml['spec']['template']['spec']['containers'][0]['name'] = container_name
#     # hpa_yaml['spec']['template']['spec']['containers'][0]['image'] = image_str
#     # hpa_yaml['spec']['template']['spec']['containers'][0]['env'][0]['value'] = api_path
    
#     # config.load_kube_config_kube_config(context="minikube")
#     api_client = kub_client.AutoscalingV2Api()

#     api_client.patch_namespaced_horizontal_pod_autoscaler(hpa_name, 'default', hpa_yaml)


def delete_hpa(project_id, deployment_type="blue"):
    project_str = f"project_{project_id}"
    image_str = f"mlops_{project_str}:latest"

    hpa_name = f"mlops-project-{project_id}-hpa-{deployment_type}"

    deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}"
    # metadata_name = f"mlops-project-{project_id}-{deployment_type}"
    # container_name = f"mlops-project-{project_id}-container-{deployment_type}"

    # api_path = f"/project{project_id}"

    
    # config.load_kube_config_kube_config(context="minikube")
    api_client = kub_client.AutoscalingV2Api()

    api_client.delete_namespaced_horizontal_pod_autoscaler(hpa_name, 'default')


def create_service(project_id, deployment_type = "blue"):
    # project_str = f"project_{project_id}"

    deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}"

    metadata_name = f"mlops-project-{project_id}-service-{deployment_type}"

    with open(os.path.join(DIRECT, "service.yml"), "r") as file:
        service_yaml = yaml.safe_load(file)
    
    # print(deploy_yaml)

    # Make the changes
    service_yaml['metadata']['name'] = metadata_name
    service_yaml['spec']['selector']['app'] = deployment_name
    

    # print("================")
    # print(deploy_yaml)
    
    # config.load_kube_config_kube_config(context="minikube")
    k8s_client = kub_client.ApiClient()
    utils.create_from_dict(k8s_client, service_yaml, namespace='default', 
        # verbose=True
    )


# def update_service(project_id, deployment_type = "blue", change_deployment_name = False):
#     # project_str = f"project_{project_id}"

#     deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}"

#     metadata_name = f"mlops-project-{project_id}-service-{deployment_type}"

#     if change_deployment_name and deployment_type == "blue":
#         new_deployment_name = f"mlops-project-{project_id}-deployment-green"
#         new_metadata_name = f"mlops-project-{project_id}-service-green"
#     elif change_deployment_name and deployment_type == "green":
#         new_deployment_name = f"mlops-project-{project_id}-deployment-blue"
#         new_metadata_name = f"mlops-project-{project_id}-service-blue"



#     with open(os.path.join(DIRECT, "service.yml"), "r") as file:
#         service_yaml = yaml.safe_load(file)
    
#     # print(deploy_yaml)

#     # Make the changes
#     service_yaml['metadata']['name'] = new_metadata_name if change_deployment_name else metadata_name
#     service_yaml['spec']['selector']['app'] = new_deployment_name if change_deployment_name else deployment_name
    

#     # print("================")
#     # print(deploy_yaml)
    
#     # config.load_kube_config_kube_config(context="minikube")
#     api_instance = kub_client.CoreV1Api()
#     api_instance.patch_namespaced_service(metadata_name, 'default', service_yaml)



def delete_service(project_id, deployment_type="blue"):
    service_name = f"mlops-project-{project_id}-service-{deployment_type}"

    # Delete pod
    # config.load_kube_config_kube_config(context="minikube")
    v1 = kub_client.CoreV1Api()

    v1.delete_namespaced_service(service_name, namespace='default')


    


def create_ingress(project_id, deployment_type="blue", path_suffix = ""):
    # deployment_name = f"mlops-project-{project_id}"
    metadata_name = f"project-{project_id}-ingress-{deployment_type}"

    service_name = f"mlops-project-{project_id}-service-{deployment_type}"

    api_path = f"/project{project_id}"
    if path_suffix != "":
        api_path = api_path + f"-{path_suffix}"
    api_path_with_regex = api_path + "(/|$)(.*)"

    with open(os.path.join(DIRECT, "ingress.yml"), "r") as file:
        ingress_yaml = yaml.safe_load(file)
    
    print(ingress_yaml)

    # Make the changes
    ingress_yaml['metadata']['name'] = metadata_name
    ingress_yaml['spec']['rules'][0]['http']['paths'][0]['path'] = api_path_with_regex
    ingress_yaml['spec']['rules'][0]['http']['paths'][0]['backend']['service']['name'] = service_name
    

    # print("================")
    # print(deploy_yaml)
    
    # config.load_kube_config_kube_config(context="minikube")
    k8s_client = kub_client.ApiClient()
    utils.create_from_dict(k8s_client, ingress_yaml, namespace='default', 
        # verbose=True
    )

def create_canary_ingress(project_id, new_deployment_type="blue", path_suffix = ""):
    # deployment_name = f"mlops-project-{project_id}"

    # New ingress will always be green. After Canary, this ingress will be delete
    # and the original "blue" ingress will point to the new service to serve
    # the new model.
    metadata_name = f"project-{project_id}-ingress-green"

    service_name = f"mlops-project-{project_id}-service-{new_deployment_type}"

    api_path = f"/project{project_id}"


    api_path_with_suffix = api_path + f"-test" + "(/|$)(.*)"
    api_path_with_regex = api_path + "(/|$)(.*)"

    with open(os.path.join(DIRECT, "canary_ingress.yml"), "r") as file:
        ingress_yaml = yaml.safe_load(file)

    # Make the changes
    ingress_yaml['metadata']['name'] = metadata_name
    ingress_yaml['spec']['rules'][0]['http']['paths'][0]['path'] = api_path_with_regex
    ingress_yaml['spec']['rules'][0]['http']['paths'][0]['backend']['service']['name'] = service_name
    # ingress_yaml['spec']['rules'][0]['http']['paths'][1]['path'] = api_path_with_suffix
    # ingress_yaml['spec']['rules'][0]['http']['paths'][1]['backend']['service']['name'] = service_name
    

    # print("================")
    # print(deploy_yaml)
    
    # config.load_kube_config_kube_config(context="minikube")
    k8s_client = kub_client.ApiClient()
    utils.create_from_dict(k8s_client, ingress_yaml, namespace='default', 
        # verbose=True
    )

def update_canary_ingress(project_id, new_deployment_type="blue", traffic=10, path_suffix = ""):
    # deployment_name = f"mlops-project-{project_id}"
    metadata_name = f"project-{project_id}-ingress-{new_deployment_type}"

    service_name = f"mlops-project-{project_id}-service-{new_deployment_type}"
    ingress_name = f"project-{project_id}-ingress-{new_deployment_type}"

    # Update taffic percentage for canary ingress    
    new_def = {
        'metadata': {
            'annotations' : {
                "nginx.ingress.kubernetes.io/canary": 'true', 
                "nginx.ingress.kubernetes.io/canary-weight": f"{traffic}"
            }
        }
    }
    
    # config.load_kube_config_kube_config(context="minikube")
    networking_api = kub_client.NetworkingV1Api()

    networking_api.patch_namespaced_ingress(ingress_name, namespace='default', body=new_def)

    logger.info(f"[INFO] Success: Updated traffic percentage for canary ingress to {traffic}%")


def update_ingress(project_id, deployment_type="blue", path_suffix = ""):
    # deployment_name = f"mlops-project-{project_id}"

    metadata_name = f"project-{project_id}-ingress-{deployment_type}"

    service_name = f"mlops-project-{project_id}-service-{deployment_type}"
    ingress_name = f"project-{project_id}-ingress-{deployment_type}"

    api_path = f"/project{project_id}"
    if path_suffix != "":
        api_path = api_path + f"-{path_suffix}"

    api_path_with_regex = api_path + "(/|$)(.*)"

    with open(os.path.join(DIRECT, "ingress.yml"), "r") as file:
        ingress_yaml = yaml.safe_load(file)
    
    # print(ingress_yaml)

    # Make the changes
    ingress_yaml['metadata']['name'] =  metadata_name
    ingress_yaml['spec']['rules'][0]['http']['paths'][0]['path'] = api_path_with_regex
    ingress_yaml['spec']['rules'][0]['http']['paths'][0]['backend']['service']['name'] =  service_name
    

    # print("================")
    # print(deploy_yaml)

    update_deployment(project_id, deployment_type, path_suffix)
    
    # config.load_kube_config_kube_config(context="minikube")
    networking_api = kub_client.NetworkingV1Api()

    networking_api.patch_namespaced_ingress(ingress_name, namespace='default', body=ingress_yaml)


def update_ingress_add_test_path(project_id, deployment_type="blue"):
    # deployment_name = f"mlops-project-{project_id}"

    metadata_name = f"project-{project_id}-ingress-blue"
    ingress_name = f"project-{project_id}-ingress-blue"

    service_name = f"mlops-project-{project_id}-service-{deployment_type}"
    

    api_path = f"/project{project_id}"
    api_path_with_regex = api_path + "(/|$)(.*)"

    if deployment_type == "blue":
        new_deployment_type = "green"
    else:
        new_deployment_type = "blue"
    
    new_service_name = f"mlops-project-{project_id}-service-{new_deployment_type}"

    test_api_path = f"/project{project_id}-test"
    test_api_path_with_regex = test_api_path + "(/|$)(.*)"


    with open(os.path.join(DIRECT, "ingress.yml"), "r") as file:
        ingress_yaml = yaml.safe_load(file)
    
    # print(ingress_yaml)

    # Make the changes
    # ingress_yaml['metadata']['name'] =  metadata_name
    rule1 = {
        'path': api_path_with_regex,
        'pathType': 'Prefix',
        'backend': {
            'service': {
                'name': service_name,
                'port': {
                    'number': 8050
                }
            }
        }
    }

    rule2 = {
        'path': test_api_path_with_regex,
        'pathType': 'Prefix',
        'backend': {
            'service': {
                'name': new_service_name,
                'port': {
                    'number': 8050
                }
            }
        }
    }
    

    new_def = {
        'spec': {
            'rules' : [{
                'http': {
                    'paths': [rule1, rule2]
                    }
            }]
        }
    }

    print(new_def)

    # ingress_yaml['spec']['rules'][0]['http']['paths'][0]['path'] = api_path_with_regex
    # ingress_yaml['spec']['rules'][0]['http']['paths'][0]['backend']['service']['name'] =  service_name


    # update_deployment(project_id, deployment_type, path_suffix)
    
    # config.load_kube_config_kube_config(context="minikube")
    networking_api = kub_client.NetworkingV1Api()

    # networking_api.patch_namespaced_ingress(ingress_name, namespace='default', body=ingress_yaml)
    networking_api.patch_namespaced_ingress(ingress_name, namespace='default', body=new_def)


def update_ingress_reset_original(project_id, deployment_type = "blue"):
    # deployment_name = f"mlops-project-{project_id}"

    metadata_name = f"project-{project_id}-ingress-blue"
    ingress_name = f"project-{project_id}-ingress-blue"

    service_name = f"mlops-project-{project_id}-service-{deployment_type}"  # Restore default service name
    

    api_path = f"/project{project_id}"
    api_path_with_regex = api_path + "(/|$)(.*)"


    rule1 = {
        'path': api_path_with_regex,
        'pathType': 'Prefix',
        'backend': {
            'service': {
                'name': service_name,   # Restore default service name
                'port': {
                    'number': 8050
                }
            }
        }
    }
    

    new_def = {
        'spec': {
            'rules' : [{
                'http': {
                    'paths': [rule1]
                    }
            }]
        }
    }

    
    # config.load_kube_config_kube_config(context="minikube")
    networking_api = kub_client.NetworkingV1Api()
    networking_api.patch_namespaced_ingress(ingress_name, namespace='default', body=new_def)



def update_ingress_promote_test_path(project_id, deployment_type="blue"):
    # deployment_name = f"mlops-project-{project_id}"

    metadata_name = f"project-{project_id}-ingress-blue"
    ingress_name = f"project-{project_id}-ingress-blue"

    service_name = f"mlops-project-{project_id}-service-{deployment_type}"
    

    api_path = f"/project{project_id}"
    api_path_with_regex = api_path + "(/|$)(.*)"

    if deployment_type == "blue":
        new_deployment_type = "green"
    else:
        new_deployment_type = "blue"
    
    new_service_name = f"mlops-project-{project_id}-service-{new_deployment_type}"

    # test_api_path = f"/project{project_id}-test"
    # test_api_path_with_regex = test_api_path + "(/|$)(.*)"
    
    # print(ingress_yaml)

    # Make the changes
    # ingress_yaml['metadata']['name'] =  metadata_name
    rule1 = {
        'path': api_path_with_regex,
        'pathType': 'Prefix',
        'backend': {
            'service': {
                'name': new_service_name,   # Switch traffic to new service
                'port': {
                    'number': 8050
                }
            }
        }
    }
    

    new_def = {
        'spec': {
            'rules' : [{
                'http': {
                    'paths': [rule1]
                    }
            }]
        }
    }

    # ingress_yaml['spec']['rules'][0]['http']['paths'][0]['path'] = api_path_with_regex
    # ingress_yaml['spec']['rules'][0]['http']['paths'][0]['backend']['service']['name'] =  service_name


    # update_deployment(project_id, deployment_type, path_suffix)
    
    # config.load_kube_config_kube_config(context="minikube")
    networking_api = kub_client.NetworkingV1Api()

    # networking_api.patch_namespaced_ingress(ingress_name, namespace='default', body=ingress_yaml)
    networking_api.patch_namespaced_ingress(ingress_name, namespace='default', body=new_def)


def update_ingress_service(project_id, deployment_type="blue", new_deployment_type = 'green'):
    # deployment_name = f"mlops-project-{project_id}"

    metadata_name = f"project-{project_id}-ingress-blue"
    ingress_name = f"project-{project_id}-ingress-blue"

    service_name = f"mlops-project-{project_id}-service-{deployment_type}"

    new_service_name = f"mlops-project-{project_id}-service-{new_deployment_type}"
    

    api_path = f"/project{project_id}"
    api_path_with_regex = api_path + "(/|$)(.*)"


    # Make the changes
    # ingress_yaml['metadata']['name'] =  metadata_name
    rule1 = {
        'path': api_path_with_regex,
        'pathType': 'Prefix',
        'backend': {
            'service': {
                'name': new_service_name,   # Switch traffic to new service
                'port': {
                    'number': 8050
                }
            }
        }
    }
    

    new_def = {
        'spec': {
            'rules' : [{
                'http': {
                    'paths': [rule1]
                    }
            }]
        }
    }


    # config.load_kube_config_kube_config(context="minikube")
    networking_api = kub_client.NetworkingV1Api()

    networking_api.patch_namespaced_ingress(ingress_name, namespace='default', body=new_def)
    



def delete_ingress(project_id, deployment_type = "blue"):
    ingress_name = f"project-{project_id}-ingress-{deployment_type}"

    # Delete pod
    # config.load_kube_config_kube_config(context="minikube")
    networking_api = kub_client.NetworkingV1Api()

    networking_api.delete_namespaced_ingress(ingress_name, namespace='default')



def create_model_stack(project_id, deployment_type = "blue"):
    try:
        create_deployment(project_id, deployment_type)
    except ApiException as err:
        print(err)
        print(f"[INFO] Failed to create deployment for model {project_id}")
        # logger.error(f"Failed to create deployment for model {project_id}", err)
        logger.exception("Failed to create deployment for model {project_id}")
    else:
        try:
            create_hpa(project_id, deployment_type)
        except ApiException as err:
            print(err)
            print(f"[INFO] Failed to create hpa for model {project_id}")
            # logger.error(f"Failed to create service for model {project_id}", err)
            logger.exception("Failed to create hpa for model {project_id}")
            delete_deployment(project_id, deployment_type)
        else:
            try:
                create_service(project_id, deployment_type)
            except ApiException as err:
                print(err)
                print(f"[INFO] Failed to create service for model {project_id}")
                # logger.error(f"Failed to create service for model {project_id}", err)
                logger.exception("Failed to create service for model {project_id}")
                delete_deployment(project_id, deployment_type)
                delete_hpa(project_id, deployment_type)
            # else:
            #     try:
            #         create_ingress(project_id, deployment_type)
            #     except ApiException as err:
            #         print(err)
            #         print(f"[INFO] Failed to create ingress for model {project_id}")
            #         # logger.error(f"Failed to create ingress for model {project_id}", err)
            #         logger.exception("Failed to create ingress for model {project_id}")
            #         delete_deployment(project_id, deployment_type)
            #         delete_hpa(project_id, deployment_type)
            #         delete_service(project_id, deployment_type)
            #     else:
            #         print("[INFO] Success: Created model stack")
            #         logger.info(f"Success: Created model stack for project {project_id}")


def create_blue_green_model_stack(project_id, deployment_type = "blue"):
    try:
        create_deployment(project_id, deployment_type, "test")
    except ApiException as err:
        print(err)
        print(f"[INFO] Failed to create blue/green deployment for model {project_id}")
        # logger.error(f"Failed to create deployment for model {project_id}", err)
        logger.exception("Failed to create blue/green deployment for model {project_id}")
    else:
        try:
            create_hpa(project_id, deployment_type)
        except ApiException as err:
            print(err)
            print(f"[INFO] Failed to create blue/green hpa for model {project_id}")
            # logger.error(f"Failed to create service for model {project_id}", err)
            logger.exception("Failed to create blue/green hpa for model {project_id}")
            delete_deployment(project_id, deployment_type)
        else:
            try:
                create_service(project_id, deployment_type)
            except ApiException as err:
                print(err)
                print(f"[INFO] Failed to create blue/green service for model {project_id}")
                # logger.error(f"Failed to create service for model {project_id}", err)
                logger.exception("Failed to create blue/green service for model {project_id}")
                delete_deployment(project_id, deployment_type)
                delete_hpa(project_id, deployment_type)
            # else:
            #     try:
            #         create_ingress(project_id, deployment_type, "test")
            #     except ApiException as err:
            #         print(err)
            #         print(f"[INFO] Failed to create ingress for model {project_id}")
            #         # logger.error(f"Failed to create ingress for model {project_id}", err)
            #         logger.exception("Failed to create ingress for model {project_id}")
            #         delete_deployment(project_id, deployment_type)
            #         delete_hpa(project_id, deployment_type)
            #         delete_service(project_id, deployment_type)
            #     else:
            #         print("[INFO] Success: Created model stack")
            #         logger.info(f"Success: Created model stack for project {project_id}")

def create_canary_model_stack(project_id, deployment_type = "blue"):
    try:
        create_deployment(project_id, deployment_type, "")
    except ApiException as err:
        print(err)
        print(f"[INFO] Failed to create canary deployment for model {project_id}")
        # logger.error(f"Failed to create deployment for model {project_id}", err)
        logger.exception("Failed to create canary deployment for model {project_id}")
    else:
        try:
            create_hpa(project_id, deployment_type)
        except ApiException as err:
            print(err)
            print(f"[INFO] Failed to create canary hpa for model {project_id}")
            # logger.error(f"Failed to create service for model {project_id}", err)
            logger.exception("Failed to create canary hpa for model {project_id}")
            delete_deployment(project_id, deployment_type)
        else:
            try:
                create_service(project_id, deployment_type)
            except ApiException as err:
                print(err)
                print(f"[INFO] Failed to create canary service for model {project_id}")
                # logger.error(f"Failed to create service for model {project_id}", err)
                logger.exception("Failed to create canary service for model {project_id}")
                delete_deployment(project_id, deployment_type)
                delete_hpa(project_id, deployment_type)
            else:
                try:
                    create_canary_ingress(project_id, deployment_type, "")
                except ApiException as err:
                    print(err)
                    print(f"[INFO] Failed to create canary ingress for model {project_id}")
                    # logger.error(f"Failed to create ingress for model {project_id}", err)
                    logger.exception("Failed to create canary ingress for model {project_id}")
                    delete_deployment(project_id, deployment_type)
                    delete_hpa(project_id, deployment_type)
                    delete_service(project_id, deployment_type)
                else:
                    print("[INFO] Success: Created canary model stack")
                    logger.info(f"Success: Created canary model stack for project {project_id}")



# def switch_model_stack(project_id, deployment_type = "blue"):
#     try:
#         update_deployment(project_id, deployment_type, change_deployment_name = True)
#     except ApiException as err:
#         print(err)
#         print(f"[INFO] Failed to switch deployment for model {project_id} {deployment_type}")
#         # logger.error(f"Failed to create deployment for model {project_id}", err)
#         logger.exception("Failed to switch deployment for model {project_id}")
#     else:
#         try:
#             update_hpa_name(project_id, deployment_type, change_deployment_name = True)
#         except ApiException as err:
#             print(err)
#             print(f"[INFO] Failed to switch hpa for model {project_id}")
#             # logger.error(f"Failed to create service for model {project_id}", err)
#             logger.exception("Failed to switch hpa for model {project_id}")
#             update_deployment(project_id, deployment_type, change_deployment_name = True)
#         else:
#             try:
#                 update_service(project_id, deployment_type, change_deployment_name=True)
#             except ApiException as err:
#                 print(err)
#                 print(f"[INFO] Failed to switch service for model {project_id}")
#                 # logger.error(f"Failed to create service for model {project_id}", err)
#                 logger.exception("Failed to switch service for model {project_id}")
#                 update_deployment(project_id, deployment_type, change_deployment_name = True)
#                 update_hpa_name(project_id, deployment_type, change_deployment_name = True)
#             else:
#                 try:
#                     update_ingress_name(project_id, deployment_type, change_deployment_name=True)
#                 except ApiException as err:
#                     print(err)
#                     print(f"[INFO] Failed to switch ingress for model {project_id}")
#                     # logger.error(f"Failed to create ingress for model {project_id}", err)
#                     logger.exception("Failed to switch ingress for model {project_id}")
#                     update_deployment(project_id, deployment_type, change_deployment_name = True)
#                     update_hpa_name(project_id, deployment_type, change_deployment_name = True)
#                     update_service(project_id, deployment_type, change_deployment_name = True)
#                 else:
#                     print("[INFO] Success: Created model stack")
#                     logger.info(f"Success: Created model stack for project {project_id}")


def delete_model_stack(project_id, deployment_type = "blue"):
    # try:
    #     delete_ingress(project_id, deployment_type)
    #     logger.info(f"Deleted model ingress for project {project_id}")
    # except ApiException as err:
    #     # print("[INFO] Failed to delete ingress")
    #     logger.info(f"Failed to delete ingres for project {project_id}")

    try:
        delete_service(project_id, deployment_type)
        logger.info(f"Deleted model service for project {project_id}")
    except ApiException as err:
        # print("[INFO] Failed to delete service")
        logger.info(f"Failed to delete service for project {project_id}")

    try:
        delete_hpa(project_id, deployment_type)
        logger.info(f"Deleted model hpa for project {project_id}")
    except ApiException as err:
        # print("[INFO] Failed to delete ingress")
        logger.info(f"Failed to delete hpa for project {project_id}")

    try:
        delete_deployment(project_id, deployment_type)
        logger.info(f"Deleted model deployment for project {project_id}")
    except ApiException as err:
        # print("[INFO] Failed to delete deployment")
        logger.info(f"Failed to delete deployment for project {project_id}")
    
    logger.info(f"Success: Deleted model stack for project {project_id}")
    

# def go_live(project_id, existing_type):





def model_deployer_main():
    while True:
        with open_rabbitmq_connection() as channel:
            while True:
                method_frame, header_frame, body = channel.basic_get(queue="model-deploy-queue")

                if method_frame != None and method_frame.NAME == "Basic.GetOk":
                    # print(method_frame)
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    try: 
                        data = json.loads(body)
                        print(data)
                        logger.info(f"New Message: {data}")
                        
                        command = data['command']
                        project_id = data['project_id']
                        
                        

                        assert type(project_id) == int
                        
                    except Exception as err:
                        # print("[ERROR] Failed to process message")
                        # print(body)
                        # print(err)
                        logger.error(f"Failed to process message: {body}")
                        logger.exception(err)


                        channel.basic_publish(exchange="amq.direct", routing_key="model-deploy",
                            body = body
                        )
                    else:
                        try:
                            with open_db_session() as db:
                                project = db.query(models.Project).filter(
                                    models.Project.id == project_id
                                    ).first()
                                    # project = project[0]
                                curr_deployment = project.deployment
                                project_status = project.status

                                # Get current verion deployed
                                curr_version = db.query(models.Version).filter(
                                        models.Version.project_id == project_id
                                    ).filter(
                                        models.Version.active_status == "Active"
                                    ).first()

                                if command == "deploy":
                                    version = data['version']
                                    strategy = data['strategy']
                                    who_deploy = data['who_deploy']

                                    assert type(version) == int

                                    # with open_db_session() as db:
                                    #     project = db.query(models.Project).filter(
                                    #         models.Project.id == project_id
                                    #         ).first()
                                    #     # project = project[0]
                                    # curr_deployment = project.deployment
                                    # project_status = project.status

                                    


                                    # Build the docker image for the new version
                                    with config_docker_to_minikube() as docker_client:
                                        try: 
                                            mlops_base_image = docker_client.images.get("mlops_base:latest")
                                        except docker.errors.ImageNotFound:
                                            logger.info(f"[INFO] MLOps Base Image not found. Building now...")
                                            
                                            project_str = f"project_{project_id}"
                                            version_str = f"version_{version}"
                                            TEMPLATE_DIR = os.path.join(FILE_SYSTEM, "model_deployment_template")
                                            TEMPLATE_DOCKERFILE = os.path.join(TEMPLATE_DIR, 'dockerfile')
                                            model_image = docker_client.images.build(
                                                path = TEMPLATE_DIR,
                                                dockerfile = TEMPLATE_DOCKERFILE,
                                                tag = f"mlops_base:latest"
                                            )

                                            logger.info(f"[INFO] Built MLOps Base Image successfully")
                                        except Exception as err:
                                            logger.error(f"Error: Failed to check if MLOps Base Image exists.")
                                        
                                        build_image(docker_client, project_id, version)
                                        docker_client.images.prune()
                                    
                                    new_version = db.query(models.Version).filter(
                                                models.Version.project_id == project_id
                                            ).filter(
                                                models.Version.version_number == version
                                            ).first()
                                    new_version.deploy_status = "deploying"
                                    db.commit()

                                    # Direct
                                    if strategy == "direct":
                                        # try:
                                        #     # delete_ingress(project_id, curr_deployment)
                                            
                                        # except:
                                        #     print("No existing records")
                                        
                                        
                                        
                                        logger.info(f"[INFO] Ensuring new version can be deployed")
                                        
                                        new_deployment = "green" if curr_deployment == "blue" else "blue"
                                        delete_model_stack(project_id, new_deployment)
                                        
                                        logger.info(f"[INFO] Deleting existing deployment")
                                        delete_model_stack(project_id, curr_deployment)

                                        try:
                                            delete_ingress(project_id, "green")     # Clear any Canary ingress
                                            logger.info(f"[INFO] Deleted existing canary ingress")
                                        except Exception as err:
                                            logger.info(f"[INFO] No existing canary ingress")
                                        
                                        
                                        # Also, update db if any other versions were deployed
                                        versions = db.query(models.Version).filter(
                                            models.Version.project_id == project_id)
                                        # ).filter(
                                        #     (models.Version.active_status == "Test") | (models.Version.active_status == "Canary") | (models.Version.active_status == "Active")
                                        # )

                                        for version in versions:
                                            version.active_status = "Down"
                                            version.deploy_status = "not deployed"
                                            version.deploy_test = 0
                                            version.traffic_percentage = 0
                                            version.deployed_before = True
                                            version.who_deploy = ""
                                            db.commit()

                                        #     # Update existing deployed version in db
                                        #     curr_version.active_status = "Down"
                                        #     curr_version.deploy_status = "not deployed"
                                        #     curr_version.deploy_test = 0
                                        #     curr_version.traffic_percentage = 0
                                        #     curr_version.deployed_before = True
                                        #     db.commit()
                                        # else:
                                        #     logger.info(f"[INFO] No existing deployment detected")
                                        
                                        update_ingress_reset_original(project_id, curr_deployment)

                                        # Create the model stack
                                        # create_ingress(project_id, curr_deployment)
                                        create_model_stack(project_id, curr_deployment)

                                        # Make sure the new version has the same HPA setting
                                        update_hpa(project_id, curr_deployment, min_pods=project.min_num_nodes,
                                            max_pods=project.max_num_nodes, desired_pods=project.desired_num_nodes
                                        )

                                        logger.info(f"[INFO] Success: Deployed project {project_id} version {version}")

                                        # Update new version in db
                                        new_version.active_status = "Active"
                                        new_version.deploy_status = "deployed"
                                        new_version.traffic_percentage = 100
                                        new_version.deployed_before = True
                                        new_version.who_deploy = who_deploy
                                        db.commit()
                                        # Update project in db
                                        project.status = "Live"
                                        db.commit()

                                        logger.info(f"[INFO] Updated db for project {project_id} version {version}")

                                        
                                        
                                    elif project_status != "Live":
                                        logger.error(f"Error: Project not live. Failed to {command} project {project_id} \n")
                                        new_version.deploy_status = "deploying"
                                        db.commit()

                                    elif strategy == "blue/green":
                                        new_stack = "blue" if curr_deployment == "green" else "green"
                                        create_blue_green_model_stack(project_id, new_stack)
                                        update_ingress_add_test_path(project_id, curr_deployment)

                                        # Make sure the new version has the same HPA setting
                                        update_hpa(project_id, new_stack, min_pods=project.min_num_nodes,
                                            max_pods=project.max_num_nodes, desired_pods=project.desired_num_nodes
                                        )

                                        logger.info(f"[INFO][blue/green] Success: Created new blue/green deployment for project {project_id}")

                                        # Update new version in db
                                        new_version = db.query(models.Version).filter(
                                                models.Version.project_id == project_id
                                            ).filter(
                                                models.Version.version_number == version
                                            ).first()
                                        new_version.active_status = "Test"
                                        new_version.deploy_status = "deployed"
                                        new_version.deploy_test = 0
                                        new_version.traffic_percentage = 0
                                        new_version.deployed_before = True
                                        new_version.who_deploy = who_deploy
                                        db.commit()

                                        logger.info(f"[INFO][blue/green] Success: Updated new model version in DB")

                                        blue_green_msg = {
                                            'command': "blue/green",
                                            'project_id': project_id,
                                            'version': version
                                        }

                                        blue_green_body = json.dumps(blue_green_msg)

                                        channel.basic_publish(exchange="amq.direct", routing_key="deployment-manager-queue",
                                            body = blue_green_body
                                        )

                                        logger.info(f"[INFO][canary] Success: Sent blue/green message to deployment manager queue")
                                    
                                    elif strategy == "canary":
                                        new_stack = "blue" if curr_deployment == "green" else "green"
                                        create_canary_model_stack(project_id, new_stack)

                                        # Make sure the new version has the same HPA setting
                                        update_hpa(project_id, new_stack, min_pods=project.min_num_nodes,
                                            max_pods=project.max_num_nodes, desired_pods=project.desired_num_nodes
                                        )

                                        logger.info(f"[INFO][canary] Success: Created new canary deployment for project {project_id}")

                                        # Update new version in db
                                        new_version = db.query(models.Version).filter(
                                                models.Version.project_id == project_id
                                            ).filter(
                                                models.Version.version_number == version
                                            ).first()
                                        new_version.active_status = "Canary"
                                        new_version.deploy_status = "deployed"
                                        new_version.deploy_test = 0
                                        new_version.traffic_percentage = 10
                                        new_version.deployed_before = True
                                        new_version.who_deploy = who_deploy
                                        db.commit()

                                        logger.info(f"[INFO][canary] Success: Updated new model version in DB")

                                        # Update current version in db
                                        curr_version.traffic_percentage = 90
                                        db.commit()

                                        logger.info(f"[INFO][canary] Success: Updated existing model version in DB")

                                        # canary_msg = {
                                        #     'command': "canary",
                                        #     'project_id': project_id,
                                        #     'version': version
                                        # }

                                        # canary_body = json.dumps(canary_msg)

                                        # channel.basic_publish(exchange="amq.direct", routing_key="deployment-manager-queue",
                                        #     body = canary_body
                                        # )
                                        # logger.info(f"[INFO][canary] Success: Sent canary message to deployment manager queue")




                                    # create_model_stack(project_id, 'blue')

                                elif command == 'go-live':
                                    print("go-live")
                                    # update_ingress(project_id, 'green', "")
                                    new_stack = "blue" if curr_deployment == "green" else "green"

                                    new_version = db.query(models.Version).filter(
                                            models.Version.project_id == project_id
                                        ).filter(
                                            models.Version.deploy_status == "deployed"
                                        ).filter(
                                            models.Version.active_status == "Going Live"
                                        ).first()
                                    if new_version == None:
                                        logger.error("[go-live] Error: No existing blue/green deployment testing env")
                                    else:
                                        update_deployment(project_id, new_stack, path_suffix="")
                                        logging.info(f'[go-live] Updated test deployment to remove path suffix')

                                        # Pause to allow for the project pods to be updated
                                        time.sleep(10)

                                        update_ingress_promote_test_path(project_id,  curr_deployment)
                                        logging.info(f'[go-live] Promoted test deployment and removed test path in ingress')
                                        
                                        # Update db project deployment field
                                        project.deployment = new_stack
                                        db.commit()
                                        logging.info(f'[go-live] DB committed new deployment environment')

                                        delete_model_stack(project_id, curr_deployment)
                                        logging.info(f'[go-live] Deleted previous model stack')
                                        logging.info(f'[go-live] Success: New model went live')


                                        # Update existing deployed version in db
                                        curr_version.active_status = "Down"
                                        curr_version.deploy_status = "not deployed"
                                        curr_version.deploy_test = 0
                                        curr_version.traffic_percentage = 0.0
                                        curr_version.deployed_before = True
                                        curr_version.who_deploy = ""
                                        db.commit()

                                        logging.info(f'[go-live] Success: Updated existing model version')

                                        # Update new version in db
                                        new_version.active_status = "Active"
                                        new_version.deploy_status = "deployed"
                                        new_version.traffic_percentage = 100.0
                                        new_version.deployed_before = True
                                        db.commit()

                                        logging.info(f'[go-live] Success: Updated new model version')

                                        # Update db
                                        project.status = "Live"
                                        db.commit()

                                elif command == 'go-live-canary':
                                    print("go-live-canary")
                                    # update_ingress(project_id, 'green', "")
                                    new_stack = "blue" if curr_deployment == "green" else "green"

                                    new_version = db.query(models.Version).filter(
                                            models.Version.project_id == project_id
                                        ).filter(
                                            models.Version.deploy_status == "deployed"
                                        ).filter(
                                            models.Version.active_status == "Canary"
                                        ).first()
                                    if new_version == None:
                                        logger.error("[go-live] Error: No existing canary deployment")
                                    else:
                                        # Switch "blue" ingress to point to the new service
                                        update_ingress_service(project_id,  curr_deployment, new_stack)
                                        logging.info(f'[go-live-canary] Updated project {project_id} ingress service from {curr_deployment} to {new_stack}')
                                        
                                        # Update db project deployment field
                                        project.deployment = new_stack
                                        db.commit()
                                        logging.info(f'[go-live-canary] DB committed new deployment environment')
                                        
                                        delete_ingress(project_id, "green")
                                        logging.info(f'[go-live-canary] Deleted canary ingress')

                                        delete_model_stack(project_id, curr_deployment)
                                        logging.info(f'[go-live-canary] Deleted previous model stack')


                                        logging.info(f'[go-live-canary] Success: New model went live')


                                        # Update existing deployed version in db
                                        curr_version.active_status = "Down"
                                        curr_version.deploy_status = "not deployed"
                                        curr_version.deploy_test = 0
                                        curr_version.traffic_percentage = 0.0
                                        curr_version.deployed_before = True
                                        curr_version.who_deploy = ""
                                        db.commit()

                                        logging.info(f'[go-live-canary] Success: Updated existing model version')

                                        # Update new version in db
                                        new_version.active_status = "Active"
                                        new_version.deploy_status = "deployed"
                                        new_version.traffic_percentage = 100.0
                                        new_version.deployed_before = True
                                        db.commit()

                                        logging.info(f'[go-live-canary] Success: Updated new model version')

                                        # Update db
                                        project.status = "Live"
                                        db.commit()

                                elif command == "delete":
                                    if curr_version != None:
                                        logger.info(f"[INFO] Deleting existing deployment")
                                        delete_model_stack(project_id, curr_deployment)
                                        
                                        # Update existing deployed version in db
                                        curr_version.active_status = "Down"
                                        curr_version.deploy_status = "not deployed"
                                        curr_version.deploy_test = 0
                                        curr_version.traffic_percentage = 0
                                        curr_version.deployed_before = True
                                        curr_version.who_deploy = ""
                                        db.commit()
                                    else:
                                        logger.info(f"[INFO] No existing deployment detected")

                                    # Update db
                                    project.status = "Down"
                                    db.commit()

                                elif command == 'update-hpa':
                                    update_hpa(project_id, deployment_type=curr_deployment, 
                                        min_pods=data['min_nodes'], max_pods=data['max_nodes'], desired_pods=data['desired_nodes']
                                    )

                                    # Update db
                                    project.min_num_nodes = data['min_nodes']
                                    project.max_num_nodes = data['max_nodes']
                                    project.desired_num_nodes = data['desired_nodes']
                                    db.commit()

                                    logger.info(f"Success: Updated hpa for project {project_id}")

                                    # Try to update hpa for Canary deployment or Test deployment (Used by Blue/Green strategy)
                                    try:
                                        new_deployment = "green" if curr_deployment == "blue" else "blue"
                                        update_hpa(project_id, deployment_type=new_deployment,
                                            min_pods=data['min_nodes'], max_pods=data['max_nodes'], desired_pods=data['desired_nodes']
                                        )
                                        logger.info(f"[INFO] Success: Updated hpa for new deployment as well")
                                    except Exception as err:
                                        logger.info(f"[INFO] No new deployment to update hpa")

                                    


                                else:
                                    logger.warning(f"Command not recognised: {command}")
                        except Exception as err:
                            # print(f"[ERROR] Failed to {command} project {project_id}")
                            # print(err)
                            logger.error(f"Failed to {command} project {project_id} \n")
                            logger.exception(err)
                            channel.basic_publish(exchange="amq.direct", routing_key="model-deploy",
                                body = body
                            )

                    finally:
                        time.sleep(3)
                else:
                    # print(f"{datetime.now()} : No message")
                    logger.info('No message')
                time.sleep(3)

        # channel = open_rabbitmq_connection()
        # print("here")
        # method_frame, header_frame, body = channel.basic_get(queue="model-deploy-queue")
        # channel.basic_reject(delivery_tag = method_frame.delivery_tag)

        # print(method_frame)

    


        
        
        
    
        

    
        
        


if __name__ == "__main__":
    model_deployer_main()


    # ####### Test Kubernetes Update Canary Ingress #########
    # update_canary_ingress(1, 'green', 100)
    # ##########################################

    ####### Test Kubernetes Update Canary Ingress #########
    # finish_canary(1, 'green')
    ##########################################

    ####### Test Kubernetes Canary Go Live #########
    # with open_rabbitmq_connection() as channel:
    #     canary_msg = {
    #         'command': "go-live-canary",
    #         'project_id': 1,
    #         'version': 2
    #     }

    #     body = json.dumps(canary_msg)

    #     channel.basic_publish(exchange="amq.direct", routing_key="model-deploy",
    #         body = body
    #     )
    ##########################################




    # ####### Test Kubernetes Create HorizontalPodScaler #########
    # create_hpa(1, 'blue')
    # ##########################################

    # # ####### Test Kubernetes Update HorizontalPodScaler #########
    # update_hpa(1, 'blue', 1, 5, 1)
    # # ##########################################

    # # ####### Test Kubernetes Delete HorizontalPodScaler #########
    # delete_hpa(1, 'blue')
    # # ##########################################

    

    # ### Test config_docker_to_minikube function #####
    # with config_docker_to_minikube() as docker_client:
    #     print(docker_client.images.list())
    # #################################################


    # model_deployer_main()
    
    # for image in docker_client.images.list():
    #     print(image.tags)
    

    # ####### Test Docker Image Builder #########
    # docker_client.images.prune()

    # model_image = build_image(1, 2)
    # print(model_image)
    # docker_client.images.prune()
    # docker_client.close()
    # ##########################################

    # ####### Test Kubernetes Create Deployment #########
    # create_deployment(1)
    # ##########################################

    # ####### Test Kubernetes Delete Deployment #########
    # delete_deployment(1)
    # ##########################################


    # ####### Test Kubernetes Create Service #########
    # create_service(1)
    # ##########################################

    # ####### Test Kubernetes Delete Deployment #########
    # delete_service(1)
    ##########################################


    ####### Test Kubernetes Create Ingress #########
    # create_ingress(1)
    ##########################################

    ####### Test Kubernetes Update Ingress #########
    # update_ingress(1, 'blue', "test")
    ##########################################

    # ####### Test Kubernetes Delete Ingress #########
    # delete_ingress(1)
    # #########################################


    ####### Create Model Stack #########
    # create_model_stack(1)
    ##########################################

    ####### Update Model Stack #########
    # update_deployment(1, 'blue', "",change_deployment_name=True)
    # switch_model_stack(1, "blue")
    ##########################################

    ####### Delete Model Stack #########
    # delete_model_stack(1)
    ##########################################






    # # config.load_kube_config_incluster_config()
    # # config.load_kube_config_kube_config
    # v1 = kub_client.CoreV1Api()

    # create_deployment(1)

    # contexts, active_context = config.list_kube_config_contexts()

    # # print(contexts)

    # minikube_context = list(filter(lambda x: x['context']['cluster'] == 'minikube', contexts))[0]

    # print(minikube_context)





    # # config.load_kube_config_kube_config(context="minikube")
    # # # config.load_kube_config_incluster_config(context=minikube_context)
    # # # config.load_kube_config_config(active_context=minikube_context)

    # # print("Active host is %s" % configuration.Configuration().host)
    # v1 = kub_client.CoreV1Api()
    # services = v1.list_namespaced_service(namespace='default')
    # print(services)



    # create_deployment(1)


    # # Delete pod
    # # config.load_kube_config_kube_config(context="minikube")
    # # v1 = kub_client.CoreV1Api()
    # api_instance = kub_client.AppsV1Api()
    # # pods = v1.list_namespaced_pod(namespace='default')
    # # print(pods)

    # project_name = f"mlops-project-{1}-blue"

    # api_instance.delete_namespaced_deployment(project_name, namespace='default')

    # target_pod = list(filter( \
    #     lambda x: x['metadata']['labels']['app'] == project_name,
    #     pods.get('items')))[0]['metadata']['name']
    # target_pods = list(v1.list_namespaced_pod(namespace='default', label_selector=f"app={project_name}").items)
    # print(target_pods)

    # for pod in target_pods:
    #     try:
    #         print(pod.metadata.name)
    #         v1.delete_namespaced_pod(pod.metadata.name, namespace='default')
    #     except ApiException as e:
    #         print("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)

    # pod_name = "mlops-project-1-blue"
    