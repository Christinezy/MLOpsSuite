
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
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, max_error, r2_score
from sklearn.metrics import log_loss, roc_auc_score, top_k_accuracy_score
from scipy.stats import ks_2samp
import requests
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

# RabitMQ
if ENV == "DEV":
    rabbitmq_url = 'amqp://user:password@localhost'
else:
    rabbitmq_url = 'amqp://user:password@rabbitmq'
port = 	5672
vhost = '/%2F'

rabbitmq_url_param = pika.URLParameters(f"{rabbitmq_url}:{port}{vhost}")
rabbitmq_client = pika.BlockingConnection(
    rabbitmq_url_param
)

formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
handler = logging.FileHandler(filename='logs/deployment_manager.log', mode='w')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)


CANARY_TRAFFIC_STEPS = [10, 25, 50, 75, 100]




@contextmanager
def config_docker_to_minikube():
    output = subprocess.run("minikube -p minikube docker-env", capture_output=True, shell=True)
    data = list(map(lambda x: x.decode("utf-8"), output.stdout.splitlines()))[:4]
    # ls = output.split()
    # print(data)
    docker_host = data[1].split("=")[1].replace('"', '')
    docker_cert_path = data[2].split("=")[1].replace('"', '')

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

def gini(actual, pred):
    assert (len(actual) == len(pred))
    all = np.asarray(np.c_[actual, pred, np.arange(len(actual))], dtype=np.float64)
    all = all[np.lexsort((all[:, 2], -1 * all[:, 1]))]
    totalLosses = all[:, 0].sum()
    giniSum = all[:, 0].cumsum().sum() / totalLosses

    giniSum -= (len(actual) + 1) / 2.
    return giniSum / len(actual)


def gini_normalized(actual, pred):
    return gini(actual, pred) / gini(actual, actual)



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
            tag = f"mlops_{project_str}_test:latest"
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
    image_str = f"mlops_{project_str}_test:latest"

    deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}-test"
    # metadata_name = f"mlops-project-{project_id}-{deployment_type}"
    container_name = f"mlops-project-{project_id}-container-{deployment_type}-test"

    api_path = f"/mlops-test"

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
    
    config.load_kube_config(context="minikube")
    k8s_client = kub_client.ApiClient()
    utils.create_from_dict(k8s_client, deploy_yaml, namespace='default', 
        # verbose=True
    )


def update_deployment(project_id, deployment_type="blue", path_suffix = ""):
    project_str = f"project_{project_id}"
    image_str = f"mlops_{project_str}_test:latest"

    deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}-test"

    # metadata_name = f"mlops-project-{project_id}-{deployment_type}"
    container_name = f"mlops-project-{project_id}-container-{deployment_type}-test"

    api_path = f"/mlops-test"

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
    
    config.load_kube_config(context="minikube")
    # k8s_client = kub_client.ApiClient()
    api_instance = kub_client.AppsV1Api()
    api_instance.patch_namespaced_deployment(deployment_name, "default", deploy_yaml)



def delete_deployment(project_id, deployment_type = "blue"):
    project_name = f"mlops-project-{project_id}-deployment-{deployment_type}-test"

    # Delete pod
    config.load_kube_config(context="minikube")
    api_instance = kub_client.AppsV1Api()

    api_instance.delete_namespaced_deployment(project_name, namespace='default')


def create_hpa(project_id, deployment_type="blue"):
    project_str = f"project_{project_id}"
    image_str = f"mlops_{project_str}_test:latest"

    hpa_name = f"mlops-project-{project_id}-hpa-{deployment_type}-test"

    deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}-test"
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
    
    config.load_kube_config(context="minikube")
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
    image_str = f"mlops_{project_str}_test:latest"

    hpa_name = f"mlops-project-{project_id}-hpa-{deployment_type}-test"

    deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}-test"
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
    
    config.load_kube_config(context="minikube")
    api_client = kub_client.AutoscalingV2Api()

    api_client.patch_namespaced_horizontal_pod_autoscaler(hpa_name, 'default', hpa_yaml)


def delete_hpa(project_id, deployment_type="blue"):
    project_str = f"project_{project_id}"
    image_str = f"mlops_{project_str}_test:latest"

    hpa_name = f"mlops-project-{project_id}-hpa-{deployment_type}-test"

    deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}-test"
    # metadata_name = f"mlops-project-{project_id}-{deployment_type}"
    # container_name = f"mlops-project-{project_id}-container-{deployment_type}"

    # api_path = f"/project{project_id}"

    
    config.load_kube_config(context="minikube")
    api_client = kub_client.AutoscalingV2Api()

    api_client.delete_namespaced_horizontal_pod_autoscaler(hpa_name, 'default')


def create_service(project_id, deployment_type = "blue"):
    # project_str = f"project_{project_id}"

    deployment_name = f"mlops-project-{project_id}-deployment-{deployment_type}-test"

    metadata_name = f"mlops-project-{project_id}-service-{deployment_type}-test"

    with open(os.path.join(DIRECT, "service.yml"), "r") as file:
        service_yaml = yaml.safe_load(file)
    
    # print(deploy_yaml)

    # Make the changes
    service_yaml['metadata']['name'] = metadata_name
    service_yaml['spec']['selector']['app'] = deployment_name
    

    # print("================")
    # print(deploy_yaml)
    
    config.load_kube_config(context="minikube")
    k8s_client = kub_client.ApiClient()
    utils.create_from_dict(k8s_client, service_yaml, namespace='default', 
        # verbose=True
    )

def delete_service(project_id, deployment_type="blue"):
    service_name = f"mlops-project-{project_id}-service-{deployment_type}-test"

    # Delete pod
    config.load_kube_config(context="minikube")
    v1 = kub_client.CoreV1Api()

    v1.delete_namespaced_service(service_name, namespace='default')
    


def create_mlops_ingress():
    # deployment_name = f"mlops-project-{project_id}"
    metadata_name = f"mlops-ingress-test"

    service_name = f""

    api_path = f"/mlops-test"
    api_path_with_regex = api_path + "(/|$)(.*)"

    with open(os.path.join(DIRECT, "ingress.yml"), "r") as file:
        ingress_yaml = yaml.safe_load(file)
    
    # print(ingress_yaml)

    # Make the changes
    ingress_yaml['metadata']['name'] = metadata_name
    ingress_yaml['spec']['rules'][0]['http']['paths'][0]['path'] = api_path_with_regex
    ingress_yaml['spec']['rules'][0]['http']['paths'][0]['backend']['service']['name'] = service_name
    

    # print("================")
    # print(deploy_yaml)
    
    config.load_kube_config(context="minikube")
    k8s_client = kub_client.ApiClient()
    utils.create_from_dict(k8s_client, ingress_yaml, namespace='default', 
        # verbose=True
    )

def update_mlops_ingress_service(project_id, deployment_type = "blue"):
    # deployment_name = f"mlops-project-{project_id}"

    metadata_name = f"mlops-ingress-test"
    ingress_name =  f"mlops-ingress-test"

    service_name = f"mlops-project-{project_id}-service-{deployment_type}-test"  

    api_path = f"/mlops-test"
    api_path_with_regex = api_path + "(/|$)(.*)"


    # Make the changes
    # ingress_yaml['metadata']['name'] =  metadata_name
    rule1 = {
        'path': api_path_with_regex,
        'pathType': 'Prefix',
        'backend': {
            'service': {
                'name': service_name,   # Switch traffic to new service
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


    config.load_kube_config(context="minikube")
    networking_api = kub_client.NetworkingV1Api()

    networking_api.patch_namespaced_ingress(ingress_name, namespace='default', body=new_def)


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
    
    config.load_kube_config(context="minikube")
    networking_api = kub_client.NetworkingV1Api()

    networking_api.patch_namespaced_ingress(ingress_name, namespace='default', body=new_def)

    logger.info(f"[INFO] Success: Updated traffic percentage for canary ingress to {traffic}%")




def delete_mlops_ingress():
    ingress_name = f"mlops-ingress-test"

    # Delete pod
    config.load_kube_config(context="minikube")
    networking_api = kub_client.NetworkingV1Api()

    networking_api.delete_namespaced_ingress(ingress_name, namespace='default')



# def create_model_stack(project_id, deployment_type = "blue"):
#     try:
#         create_deployment(project_id, deployment_type)
#     except ApiException as err:
#         print(err)
#         print(f"[INFO] Failed to create deployment for model {project_id}")
#         # logger.error(f"Failed to create deployment for model {project_id}", err)
#         logger.exception("Failed to create deployment for model {project_id}")
#     else:
#         try:
#             create_hpa(project_id, deployment_type)
#         except ApiException as err:
#             print(err)
#             print(f"[INFO] Failed to create hpa for model {project_id}")
#             # logger.error(f"Failed to create service for model {project_id}", err)
#             logger.exception("Failed to create hpa for model {project_id}")
#             delete_deployment(project_id, deployment_type)
#         else:
#             try:
#                 create_service(project_id, deployment_type)
#             except ApiException as err:
#                 print(err)
#                 print(f"[INFO] Failed to create service for model {project_id}")
#                 # logger.error(f"Failed to create service for model {project_id}", err)
#                 logger.exception("Failed to create service for model {project_id}")
#                 delete_deployment(project_id, deployment_type)
#                 delete_hpa(project_id, deployment_type)
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


def create_model_stack(project_id):
    try:
        create_deployment(project_id)
    except ApiException as err:
        print(err)
        print(f"[INFO] Failed to create deployment for model {project_id}")
        # logger.error(f"Failed to create deployment for model {project_id}", err)
        logger.exception("Failed to create deployment for model {project_id}")
    else:
        try:
            create_hpa(project_id)
        except ApiException as err:
            print(err)
            print(f"[INFO] Failed to create hpa for model {project_id}")
            # logger.error(f"Failed to create service for model {project_id}", err)
            logger.exception("Failed to create hpa for model {project_id}")
            delete_deployment(project_id)
        else:
            try:
                create_service(project_id)
            except ApiException as err:
                print(err)
                print(f"[INFO] Failed to create service for model {project_id}")
                # logger.error(f"Failed to create service for model {project_id}", err)
                logger.exception("Failed to create service for model {project_id}")
                delete_deployment(project_id)
                delete_hpa(project_id)


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

def test_model(project_id, version):
    logger.info(f"Performing test for project {project_id} version {version}")
    
    dataset_dir = os.path.join(FILE_SYSTEM, 
        f"project_{project_id}",
        f"version_{version}"
        )
    dataset_path = os.path.join(dataset_dir, 'test.csv')

    try:
        assert os.path.isfile(dataset_path)
    except Exception as err:
        logging.error(f"Error: test.csv not found for project {project_id} version {version}")
        raise Exception
    
    try: 
        df = pd.read_csv(dataset_path)
        X_test = df.loc[:, df.columns != 'target']
        y_test = df.loc[:, ['target']]
        y_true = y_test['target'].tolist()
        payload = X_test.to_dict('records')
    except Exception as err:
        logging.error(f"Error: Failed to get payload for project {project_id} version {version}")
        raise Exception

    try:
        project_url = f"http://localhost/project{project_id}-test/batch-predict-proba"

        headers ={
            # 'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate',
            # 'Connection': 'close',
            # 'Content-Length': '16',
            'Content-Type': 'application/json',
            'Accept': 'applicaiton/json'
        }

        resp = requests.post(
            url= project_url,
            data= json.dumps(payload),
            headers= headers
        )
    except Exception as err:
        logging.error(f"Error: Failed to POST for project {project_id} version {version}")
        raise Exception

    try:
        resp_data = resp.json()
        preds = resp_data['data']
    except Exception as err:
        # print(resp_data)
        logging.error(f"Error: Response data error for project {project_id} version {version}")
        raise Exception
    
    try:
        # y_true = convert_cat_to_int(y_true)
        # y_pred = convert_cat_to_int(preds)
        y_pred = preds

        # temp = y_pred[:, 1]
        temp = np.vstack(y_pred)
        # print(temp[:, 1])

        df = pd.DataFrame()
        df['true'] = y_true
        df['proba'] = temp[:, 1]
        
    except Exception as err:

        logging.error(f"Error: Failed to convert cat to int for project {project_id} version {version}")
        raise Exception

    try:
        # Group by actual classes
        class0 = df[df['true'] == 0]
        class1 = df[df['true'] == 1]
        

        logloss = log_loss(y_true, df['proba'])
        auc_roc = roc_auc_score(y_true, df['proba'])
        ks_score = ks_2samp(class0['proba'], class1['proba']).statistic
        rate_top10 = top_k_accuracy_score(df['true'], df['proba'], k=1)

        # # By definition, normalised gini_score = 2 * auc - 1
        # gini_norm = 2 * auc_roc - 1

        gini_norm = gini_normalized(df['true'], df['proba'])


    except Exception as err:
        print(err)
        logging.error(f"Error: Failed to get metrics for project {project_id} version {version}")
        raise Exception
    
    # performance = models.Data_Drift(
    #     # timestamp=datetime.now(),
    #     project_id=project_id,
    #     logloss=logloss,
    #     auc_roc = auc_roc,
    #     ks_score = ks_score,
    #     gini_norm = gini_norm,
    #     rate_top10 = rate_top10
    # )


    

    # logging.info(f"[INFO] Success: Obtained metrics for project {project_id} version {version}")
    # print(f"""Accuracy: {accuracy}, Recall: {recall}, Precision: {precision}, \
    #     f1_score: {f1}, auc_roc: {auc_roc} \
    #     """)

    logging.info(f"[INFO] Success: Obtained metrics for project {project_id} version {version}")
    print(f"""Logloss: {logloss}, AUC_ROC: {auc_roc}, KS: {ks_score}, Gini Norm: {gini_norm}, Rate@top10 : {rate_top10}
        """)


    if auc_roc >= 0.5:
        return True
    else:
        return False
        


def deployment_manager_main():
    try:
        create_mlops_ingress()
        logger.info(f"[INFO] MLOps Ingress Test created")
    except Exception as err:
        logger.info(f"[INFO] MLOps Ingress Test exists")

    
    while True:
        with open_rabbitmq_connection() as channel:
            while True:
                method_frame, header_frame, body = channel.basic_get(queue="deployment-manager-queue")

                if method_frame != None and method_frame.NAME == "Basic.GetOk":
                    # print(method_frame)
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    try: 
                        data = json.loads(body)
                        print(data)
                        logger.info(f"New Message: {data}")
                        
                        command = data['command']
                        project_id = data['project_id']
                        version = data['version']
                        
                        assert type(project_id) == int
                        assert type(version) == int

                    except Exception as err:
                        # print("[ERROR] Failed to process message")
                        # print(body)
                        # print(err)
                        logger.error(f"Failed to process message: {body}")
                        logger.exception(err)


                        channel.basic_publish(exchange="amq.direct", routing_key="deployment-manager-queue",
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
                                        models.Version.version_number == version
                                    ).first()

                                if command == "test-model":
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
                                    
                                    # new_version = db.query(models.Version).filter(
                                    #             models.Version.project_id == project_id
                                    #         ).filter(
                                    #             models.Version.version_number == version
                                    #         ).first()
                                    # new_version.deploy_status = "deploying"
                                    # db.commit()

                                    # Create the model stack
                                    create_model_stack(project_id)
                                    time.sleep(10)
                                    
                                    # Test the model

                                    # Delete model stack
                                    delete_model_stack(project_id)

                                
                                elif command == "monitor-canary":
                                    new_stack = "blue" if curr_deployment == "green" else "green"

                                    new_version = db.query(models.Version).filter(
                                                models.Version.project_id == project_id
                                            ).filter(
                                                models.Version.version_number == version
                                            ).filter(
                                                models.Version.active_status == "Canary"
                                            ).first()
                                    
                                    if new_version == None:
                                        logger.error(f"[Error] No canary version detected for project {project_id} version {version}")
                                        break
                                                                      
                                    curr_traffic = version.traffic
                                    curr_traffic = curr_traffic if curr_traffic != None else 10
                                    curr_idx = CANARY_TRAFFIC_STEPS.index(curr_traffic)

                                    try:
                                        test_result = test_model(project_id, version)
                                    except Exception as err:
                                        logger.info(f"[INFO] Requeue request to monitor canary for project {project_id} version {version}")
                                        channel.basic_publish(exchange="amq.direct", routing_key="model-deploy-queue",
                                            body = body
                                        )
                                    else:
                                        if not test_result:
                                            logger.info(f"[INFO] Test failed. Requeue request to monitor canary for project {project_id} version {version}")
                                            channel.basic_publish(exchange="amq.direct", routing_key="model-deploy-queue",
                                                body = body
                                            )
                                        else:
                                            curr_idx += 1

                                            if curr_idx >= len(CANARY_TRAFFIC_STEPS):
                                                print('canary finish', project_id, new_stack)

                                                canary_msg = {
                                                    'command': "go-live-canary",
                                                    'project_id': project_id,
                                                    'version': version
                                                }

                                                canary_msg_str = json.dumps(canary_msg)

                                                channel.basic_publish(exchange="amq.direct", routing_key="model-deploy-queue",
                                                    body = canary_msg_str
                                                )

                                                logger.info(f"[INFO] Canary finish: Sent message to model deployer")

                                            else:
                                                new_traffic = CANARY_TRAFFIC_STEPS[curr_idx]
                                                print('monitor-canary', project_id, new_stack)
                                                update_canary_ingress(project_id, new_stack, new_traffic)

                                                canary_msg = {
                                                    'command': "canary",
                                                    'project_id': project_id,
                                                    'version': version
                                                }

                                                canary_msg_str = json.dumps(canary_msg)

                                                channel.basic_publish(exchange="amq.direct", routing_key="deployment-manager-queue",
                                                    body = canary_msg_str
                                                )

                                                logger.info(f"[INFO] monitor-canary: Update project {project_id} version {version} traffic to {new_traffic}%")

                                    
                                        

                                    # create_model_stack(project_id, 'blue')
                                # elif command == 'go-live':
                                #     print("go-live")
                                #     # update_ingress(project_id, 'green', "")
                                #     new_stack = "blue" if curr_deployment == "green" else "green"

                                #     new_version = db.query(models.Version).filter(
                                #             models.Version.project_id == project_id
                                #         ).filter(
                                #             models.Version.deploy_status == "deployed"
                                #         ).filter(
                                #             models.Version.active_status == "Test"
                                #         ).first()
                                #     if new_version == None:
                                #         logger.error("[go-live] Error: No existing blue/green deployment testing env")
                                #     else:
                                #         update_deployment(project_id, new_stack, path_suffix="")
                                #         logging.info(f'[go-live] Updated test deployment to remove path suffix')

                                #         # Pause to allow for the project pods to be updated
                                #         time.sleep(15)

                                #         update_ingress_promote_test_path(project_id,  curr_deployment)
                                #         logging.info(f'[go-live] Promoted test deployment and removed test path in ingress')
                                        
                                #         # Update db project deployment field
                                #         project.deployment = new_stack
                                #         db.commit()
                                #         logging.info(f'[go-live] DB committed new deployment environment')

                                #         delete_model_stack(project_id, curr_deployment)
                                #         logging.info(f'[go-live] Deleted previous model stack')
                                #         logging.info(f'[go-live] Success: New model went live')


                                #         # Update existing deployed version in db
                                #         curr_version.active_status = "Down"
                                #         curr_version.deploy_status = "not deployed"
                                #         curr_version.traffic_percentage = 0.0
                                #         curr_version.deployed_before = True
                                #         db.commit()

                                #         logging.info(f'[go-live] Success: Updated existing model version')

                                #         # Update new version in db
                                #         new_version.active_status = "Active"
                                #         new_version.deploy_status = "deployed"
                                #         new_version.traffic_percentage = 100.0
                                #         new_version.deployed_before = True
                                #         db.commit()

                                #         logging.info(f'[go-live] Success: Updated new model version')

                                #         # Update db
                                #         project.status = "Live"
                                #         db.commit()

                                # elif command == "delete":
                                #     if curr_version != None:
                                #         logger.info(f"[INFO] Deleting existing deployment")
                                #         delete_model_stack(project_id, curr_deployment)
                                        
                                #         # Update existing deployed version in db
                                #         curr_version.active_status = "Down"
                                #         curr_version.deploy_status = "not deployed"
                                #         curr_version.traffic_percentage = 0
                                #         curr_version.deployed_before = True
                                #         db.commit()
                                #     else:
                                #         logger.info(f"[INFO] No existing deployment detected")

                                #     # Update db
                                #     project.status = "Down"
                                #     db.commit()

                                # elif command == 'update-hpa':
                                #     update_hpa(project_id, deployment_type=curr_deployment, 
                                #         min_pods=data['min_nodes'], max_pods=data['max_nodes'], desired_pods=data['desired_nodes']
                                #     )
                                #     logger.info(f"Success: Updated hpa for project {project_id}")
                                # else:
                                #     logger.warning(f"Command not recognised: {command}")
                        except Exception as err:
                            # print(f"[ERROR] Failed to {command} project {project_id}")
                            # print(err)
                            logger.error(f"Failed to {command} project {project_id} \n")
                            logger.exception(err)
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
    deployment_manager_main()

    