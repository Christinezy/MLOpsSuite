
from kubernetes import client as kub_client
from kubernetes import config
from database import DB_session
from datetime import datetime
from contextlib import contextmanager
import pandas as pd
import io
import subprocess
import time
import random
import logging
import models
import os

PROD = os.environ.get("PROD")

formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
handler = logging.FileHandler(filename='logs/performance.log', mode='w')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler) 

if PROD == "DEV":
    config.load_kube_config(context='minikube')
else:
    config.load_kube_config(config_file="/home/vboxuser/.kube/config")


def get_average_response_time():
    # config.load_kube_config()
    events = kub_client.CustomObjectsApi().list_cluster_custom_object("events.k8s.io", "v1", "events")

    api_latencies = []
    for event in events['items']:
        if 'metrics-server' in event['metadata']['name']:
            continue

        start_time = event['metadata']['creationTimestamp']
        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%SZ')

        try: 
            end_time = event['metadata']['deletionTimestamp']
            end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%SZ')
        except:
            end_time = datetime.utcnow()
        
        latency = (end_time - start_time).total_seconds()
        api_latencies.append(latency)

    return api_latencies


def get_num_containers():
    output = subprocess.check_output("kubectl get deployment", shell=True)
    df = pd.read_csv(io.StringIO(output.decode('utf-8')), delim_whitespace=True)
    deployments = df['NAME'].values.tolist()

    num_containers = []
    for deploy_name in deployments:
        command = "kubectl get deployment " + deploy_name + " -n default -o jsonpath='{.status.availableReplicas}'"
        output = subprocess.check_output(command, shell=True).decode("utf-8")
        num_containers.append(int(output.strip("'")))
    
    df['Num_Containers'] = num_containers

    return df



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

def get_project_id_and_deployment_from_name(name):
    ls = name.split("-")
    proj_id = int(ls[2])
    deployment = ls[4]
    return (proj_id, deployment)


def performance_metrics_main():
    subprocess.run("minikube addons enable metrics-server", shell=True)
    subprocess.run("kubectl apply -f ../metrics-server.yml", shell=True)
    # subprocess.run("kubectl apply -f ./direct/ingress.yml", shell=True)

    while True:
        try:
            with open_db_session() as db:
                pods_df = pd.DataFrame()
                try: 
                    command = "kubectl top pods"
                    output = subprocess.check_output(command.split())
                    pods_df = pd.read_csv(io.StringIO(output.decode('utf-8')), delim_whitespace=True)

                    # for index in range(len(pods_df)):
                    #     if "deployment" in pods_df.iloc[index]['NAME']:
                    #         pods_df = pods_df.drop(index, axis=0)

                except Exception as err:
                    print(err)
                    logging.error(f"Error: Failed to get performance metrics")
                    # break
                
                try:

                    # Get number of containers
                    num_containers = get_num_containers()
                    num_containers[['project_id', 'deployment']] = list(map(lambda name: get_project_id_and_deployment_from_name(name), num_containers["NAME"].tolist()))
                    df_full = num_containers

                    if not pods_df.empty:
                        # Get pods
                        pods_df[['project_id', 'deployment']] = list(map(lambda name: get_project_id_and_deployment_from_name(name), pods_df["NAME"].tolist()))
                        # Merge
                        df_full = pd.merge(pods_df, num_containers, how="right", left_on=['project_id', 'deployment'], right_on=['project_id', 'deployment'])
                        
                        # Fill Missing Values with 0
                        df_full.fillna(0)

                        # print(df_full)
                        # print(df_full['CPU(cores)'])
                        # print(df_full['MEMORY(bytes)'])

                        prediction_list = []
                        request_list = []

                        try:
                            for k in range(len(df_full)):
                                project_id = df_full['project_id'][k]
                                perf = db.query(models.Performance).filter(models.Performance.project_id == project_id).order_by(models.Performance.timestamp).first()

                                new_total_pred = perf.total_prediction + random.randint(1, 100)
                                prediction_list.append(new_total_pred)

                                new_total_req = perf.total_requests + new_total_pred - perf.total_prediction + random.randint(1, 5)
                                request_list.append(new_total_req)

                        except Exception as err:
                            print(err)
                            logging.error(f"Error: Failed to get prediction and request metrics")

                        
                        # Cleaning data
                        df_full['CPU'] = df_full["CPU(cores)"].apply(lambda x: int(x[:-1])/2000*100)
                        df_full['Memory'] = df_full["MEMORY(bytes)"].apply(lambda x: int(x[:-2]))
                        df_full['Predictions'] = prediction_list
                        df_full['Requests'] = request_list
                    else:
                        # Cleaning data
                        df_full['CPU'] = [0] * len(df_full)
                        df_full['Memory'] = [0] * len(df_full)
                        df_full['Num_Containers'] = [0] * len(df_full)
                        df_full['Predictions'] = [0] * len(df_full)
                        df_full['Requests'] = [0] * len(df_full)


                except Exception as err:
                    df_full = pd.DataFrame()
                    print(err)
                    logging.error(f"Error: Failed to format performance metrics")
                    # break
                
                projects = db.query(models.Project).filter(
                    models.Project.status == "Live"
                    ).all()
                
                projects_deployment_tracker = {project.id: project.deployment for project in projects}

                added_metrics = []

                for index, row in df_full.iterrows():
                    try:
                        project_id = row['project_id']
                        deployment = row['deployment']
                        print(project_id, deployment, projects_deployment_tracker)
                        if project_id not in projects_deployment_tracker:
                            continue
                        elif projects_deployment_tracker[project_id] != deployment:
                            continue
                        else:
                            performance_metrics = models.Performance(
                                project_id = project_id,
                                total_prediction = row['Predictions'], 
                                total_requests = row['Requests'], 
                                cpu_usage = row['CPU'], 
                                ram_usage = row['Memory'], 
                                num_containers= row['Num_Containers']
                                # average_response_time = row['Avg_Response_Time'] 
                            )
                            db.add(performance_metrics)

                            
                            db.query(models.Project).filter(models.Project.id == project_id).update(
                                {
                                models.Project.total_prediction: row['Predictions'],
                                models.Project.total_requests: row['Requests'],
                                models.Project.cpu_usage: row['CPU'],
                                models.Project.ram_usage: row['Memory'],
                                models.Project.num_containers: row['Num_Containers']
                                }
                            )

                            db.commit()
                            added_metrics.append((project_id, deployment))
                    except Exception as err:
                        print(err)
                        logging.error(f"Failed: Handling of {project_id} - {deployment}")
                
                if len(added_metrics) > 0:
                    print(f"[INFO] Success: Obtained performance metrics - {added_metrics}")
                    logging.info(f"[INFO] Success: Obtained performance metrics - {added_metrics}")
                else:
                    print(f"[INFO] Success: No performance metrics to add")
                    logging.info(f"[INFO] Success: No performance metrics to add")



        except Exception as err:
            print(err)
            logging.error(f"Error: Failed to insert performance metrics to DB")
            break
        
        time.sleep(10)
        # break




# namespace = 'default'
# pod_name = 'mlops-project-1-blue-7848468fc5-mzk9p'
# container_name = 'mlops-project-1-container'


# def get_network_data():

    #### For minikube container level send/receive bytes

    # # config.load_kube_config()
    # # api_client = kub_client.ApiClient()
    # # pod_client = kub_client.CoreV1Api(api_client)

    # # namespace = 'default'
    # # pod_list = pod_client.list_namespaced_pod(namespace)

    # # for pod in pod_list.items:
    # #     # print(pod)
    # #     for container in pod.spec.containers:
    # #         print(container.name)

    # # client = docker.from_env()
    # # container_name_or_id = container.name # '07c28cab5854'
    # # container = client.containers.get(container_name_or_id)
    # # stats = container.stats(stream=False)
    # # print(stats['networks'])



    #### Attempt 1

    # config.load_kube_config()
    # v1 = kub_client.CoreV1Api()

    # pod_name = "mlops-project-1-blue-7848468fc5-mzk9p"
    # pod_namespace = "default"
    # pod = v1.read_namespaced_pod(name=pod_name, namespace=pod_namespace)

    # container_name = pod.spec.containers[0].name
    # container_id = pod.status.container_statuses[0].container_id.split("://")[1]

    # exec_command = ['/bin/sh', '-c', f"ls -l /proc/{container_id}/ns/net"]
    # resp = v1.connect_get_namespaced_pod_exec(pod_name, pod_namespace, command=exec_command, container=container_name, stderr=True, stdin=False, stdout=True, tty=False)
    # ns_path = resp.split()[0]

    # exec_command = ['/bin/cat', '/proc/net/dev']
    # resp = v1.connect_get_namespaced_pod_exec(pod_name, pod_namespace, command=exec_command, container=container_name, stderr=True, stdin=False, stdout=True, tty=False, namespace=ns_path)
    # lines = resp.strip().split("\n")
    # header_line = lines.pop(0)
    # headers = header_line.split("|")
    # interface_stats = {}
    # for line in lines:
    #     parts = line.strip().split(":")
    #     interface_name = parts[0].strip()
    #     stats = parts[1].strip().split()
    #     interface_stats[interface_name] = dict(zip(headers[1:], stats))
        
    # # Get send and receive stats for eth0 interface
    # eth0_stats = interface_stats['eth0']
    # send_bytes = eth0_stats['tx_bytes']
    # recv_bytes = eth0_stats['rx_bytes']




    #### Attempt 2

    # config.load_kube_config()
    # api_client = kub_client.ApiClient()
    # metrics_client = kub_client.CustomObjectsApi(api_client)

    # query = 'sum(rate(container_network_receive_bytes_total{{pod_name="{0}",namespace="{1}"}}[1m])) by (pod_name), sum(rate(container_network_transmit_bytes_total{{pod_name="{0}",namespace="{1}"}}[1m])) by (pod_name)'.format(pod_name, namespace)
    # response = metrics_client.list_namespaced_custom_object('metrics.k8s.io', 'v1beta1', namespace, 'pods', label_selector='pod_name={}'.format(pod_name), query=query)

    # namespace = 'default'
    # pod_list = pod_client.list_namespaced_pod(namespace)
    
    # # pods = kub_client.CoreV1Api().list_namespaced_pod(namespace='default')
    # network_rates = []


    # Loop over each pod and retrieve the Network Receive/Transmit Rate metrics
    # for pod_name in pod_names:
    #     # Define the query to retrieve the Network Receive/Transmit Rate metrics
    #     query = 'sum(rate(container_network_receive_bytes_total{{pod_name="{0}",namespace="{1}"}}[1m])) by (pod_name), sum(rate(container_network_transmit_bytes_total{{pod_name="{0}",namespace="{1}"}}[1m])) by (pod_name)'.format(pod_name, namespace)

    #     # Send the query to the Kubernetes Metrics API
    #     response = metrics_client.list_namespaced_custom_object('metrics.k8s.io', 'v1beta1', namespace, 'pods', label_selector='pod_name={}'.format(pod_name), query=query)

    # # Extract the metrics from the response
    # network_receive_rate = response['items'][0]['sum(rate(container_network_receive_bytes_total{}[1m]))']
    # network_transmit_rate = response['items'][0]['sum(rate(container_network_transmit_bytes_total{}[1m]))']

    # # Store the metrics values in a list
    # metrics = [float(network_receive_rate), float(network_transmit_rate)]




    #### Attempt 3

    # config.load_kube_config()
    # api_client = kub_client.ApiClient()
    # pod_client = kub_client.CoreV1Api(api_client)

    # namespace = 'default'
    # pod_list = pod_client.list_namespaced_pod(namespace)
    
    # # pods = kub_client.CoreV1Api().list_namespaced_pod(namespace='default')
    # network_rates = []

    # for pod in pod_list.items:
    #     for container in pod.spec.containers:
    #         metrics_client = kub_client.CustomObjectsApi(api_client)
    #         response = metrics_client.get_namespaced_pod_metrics(pod.metadata.name, namespace)

    #         network_receive_rate = None
    #         network_transmit_rate = None
    #         for container_metric in response.containers:
    #             if container_metric.name == container.name:
    #                 network_receive_rate = container_metric.usage['rx_bytes']
    #                 network_transmit_rate = container_metric.usage['tx_bytes']
    #                 break

    #         current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    #         # Add the Network Receive/Transmit Rate values to the list
    #         network_rates.append({
    #             'timestamp': current_time,
    #             'pod_name': pod.metadata.name,
    #             'container_name': container.name,
    #             'network_receive_rate': network_receive_rate,
    #             'network_transmit_rate': network_transmit_rate
    #         })

    # # Print the Network Receive/Transmit Rate values for all containers
    # for network_rate in network_rates:
    #     print('Timestamp: {}'.format(network_rate['timestamp']))
    #     print('Pod Name: {}, Container Name: {}'.format(network_rate['pod_name'], network_rate['container_name']))
    #     print('Network Receive Rate: {}'.format(network_rate['network_receive_rate']))
    #     print('Network Transmit Rate: {}'.format(network_rate['network_transmit_rate']))




    #### Attempt 4

    # # Create an instance of the Kubernetes API client
    # api_instance = kub_client.CoreV1Api()

    # # Set the namespace and pod name for which to retrieve the network stats
    # namespace = 'default'
    # pod_name = 'my-pod'

    # # Get the pod object
    # pod = api_instance.read_namespaced_pod(name=pod_name, namespace=namespace)

    # # Get the pod's container ID
    # container_id = pod.status.container_statuses[0].container_id.split('//')[-1]

    # # Get the node name where the pod is running
    # node_name = pod.spec.node_name

    # # Create an instance of the Kubernetes API client for nodes
    # config = configuration()
    # config.host = f'https://{node_name}:10250'
    # api_client = kub_client.api_client.ApiClient(configuration=config)
    # node_api = kub_client.CoreV1Api(api_client)

    # # Get the network stats for the container
    # stats = node_api.read_node_stat_summary()

    # # Extract the network stats for the container
    # network_stats = {}
    # for container_stats in stats.pods:
    #     if container_stats.pod_ref.namespace == namespace and container_stats.pod_ref.name == pod_name:
    #         for interface_stats in container_stats.network.interfaces:
    #             if interface_stats.name == 'eth0':
    #                 network_stats['tx_bytes'] = interface_stats.tx_bytes
    #                 network_stats['rx_bytes'] = interface_stats.rx_bytes

    # # Print the network stats
    # print(json.dumps(network_stats))




    #### Attempt 5

    # # Specify the name of the pod containing the container
    # pod_name = 'mlops-project-1-blue-7848468fc5-mzk9p'

    # # Specify the name of the container
    # container_name = 'mlops-project-1-container'

    # # Specify the time period over which to gather statistics (in seconds)
    # period = '60'

    # # Run the kubectl command to get network statistics for the container
    # command = f'kubectl exec -it {pod_name} -c {container_name} -- /usr/bin/netstat -s --tcp --udp --unix | grep -E "bytes|segments"'
    # result = subprocess.check_output(command, shell=True).decode('utf-8')

    # # Parse the output as JSON
    # stats = {}
    # for line in result.splitlines():
    #     if 'bytes' in line:
    #         key = 'bytes_' + line.split()[1].lower()
    #         value = int(line.split()[0])
    #         stats[key] = value
    #     elif 'segments' in line:
    #         key = 'segments_' + line.split()[1].lower()
    #         value = int(line.split()[0])
    #         stats[key] = value

    # # Print the network statistics for the container
    # print(json.dumps(stats, indent=2))





if __name__ == "__main__":
    performance_metrics_main()
    # get_network_data()