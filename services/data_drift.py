
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
import sklearn
# from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score, roc_auc_score 
from sklearn.metrics import mean_squared_error, max_error, r2_score
from sklearn.metrics import log_loss, roc_auc_score, top_k_accuracy_score
from scipy.stats import ks_2samp
import requests
from datetime import datetime
from contextlib import contextmanager
import json
import logging

import pika

from database import DB_session

# from backend.models import *
# from models import *
import models

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

curr_dir = os.getcwd()

FILE_SYSTEM = os.path.join(curr_dir, "mlops_files")
# DIRECT = os.path.join(curr_dir, "direct")
# BLUE_GREEN = os.path.join(curr_dir, "bluegreen")
# CANARY = os.path.join(curr_dir, "canary")

# DIRECT_DOCKERFILE = os.path.join(DIRECT, "dockerfile")
# DIRECT_DEPLOY_YAML = None

# with open(os.path.join(DIRECT, "deploy_blue.yml") as file:
#     DIRECT_DEPLOY_YAML = yaml.safe_load(file)

# docker_client = docker.from_env()

ENV = os.environ.get('ENV')

PROD = os.environ.get("PROD")

# # RabitMQ
# if ENV == "DEV":
#     rabbitmq_url = 'amqp://user:password@localhost'
# else:
#     rabbitmq_url = 'amqp://user:password@rabbitmq'
# port = 	5672
# vhost = '/%2F'

if PROD == "DEV":
    mlops_project_url_base = "http://localhost"
else:
    mlops_project_url_base = "http://192.168.49.2"

# os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname("../"))




formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
handler = logging.FileHandler(filename='logs/data_drift.log', mode='w')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)




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


def data_drift_main():
    while True:
        with open_db_session() as db:
            projects = db.query(models.Project).filter(
                models.Project.status == "Live"
                ).all()
        
        if len(projects) > 0:
            logger.info(f"Found {len(projects)} projects. Performing data drift test(s)...")
            for project in projects:
                project_id = project.id
                version = 1     #TODO: Get version from db

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
                    continue
                
                try: 
                    df = pd.read_csv(dataset_path)
                    X_test = df.loc[:, df.columns != 'target']
                    y_test = df.loc[:, ['target']]
                    y_true = y_test['target'].tolist()
                    payload = X_test.to_dict('records')
                except Exception as err:
                    logging.error(f"Error: Failed to get payload for project {project_id} version {version}")
                    continue

                try:
                    project_url = f"{mlops_project_url_base}/project{project_id}/batch-predict-proba"

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
                    continue

                try:
                    resp_data = resp.json()
                    preds = resp_data['data']
                except Exception as err:
                    # print(resp_data)
                    logging.error(f"Error: Response data error for project {project_id} version {version}")
                    continue
                
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
                    continue

                try:
                    # accuracy = accuracy_score(y_true, y_pred)
                    # recall = recall_score(y_true, y_pred)
                    # precision = precision_score(y_true, y_pred)
                    # f1 = f1_score(y_true, y_pred)
                    # auc_roc = roc_auc_score(y_true, y_pred)
                    # mse = mean_squared_error(y_true, y_pred)

                    # accuracy = 0
                    # recall = 0
                    # precision = 0
                    # f1= 0
                    # auc_roc = 0

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
                    continue
                
                performance = models.Data_Drift(
                    # timestamp=datetime.now(),
                    project_id=project_id,
                    logloss=logloss,
                    auc_roc = auc_roc,
                    ks_score = ks_score,
                    gini_norm = gini_norm,
                    rate_top10 = rate_top10
                )


                # logging.info(f"[INFO] Success: Obtained metrics for project {project_id} version {version}")
                # print(f"""Accuracy: {accuracy}, Recall: {recall}, Precision: {precision}, \
                #     f1_score: {f1}, auc_roc: {auc_roc} \
                #     """)

                logging.info(f"[INFO] Success: Obtained metrics for project {project_id} version {version}")
                print(f"""Logloss: {logloss}, AUC_ROC: {auc_roc}, KS: {ks_score}, Gini Norm: {gini_norm}, Rate@top10 : {rate_top10}
                    """)

                # print(f"MSE: {mse}")
                try: 
                    with open_db_session() as db:
                        db.add(performance)
                        db.commit()
                except Exception as err:
                    logging.error(f"Error: Failed to insert metrics to DB for project {project_id} version {version}")
                    print(err)


        else:
            # print(f"{datetime.now()} : No message")
            logger.info('No message')

        time.sleep(10)

        # channel = open_rabbitmq_connection()
        # print("here")
        # method_frame, header_frame, body = channel.basic_get(queue="model-deploy-queue")
        # channel.basic_reject(delivery_tag = method_frame.delivery_tag)

        # print(method_frame)



# @contextmanager
# def open_rabbitmq_connection():
#     counter = 0
#     while True:
#         try: 
#             channel = rabbitmq_client.channel()
#         except Exception as err:
#             logger.info(f"[ERROR] Failed to connect to RabbitMQ. Attempt number {counter}")
#             sys.stderr.write(f"[ERROR] Failed to connect to RabbitMQ. Attempt number {counter}")
#             raise err
#         else:
#             logger.info(f"[INFO] Successfully connected to RabbitMQ. Attempt number {counter}")
#             break
#     try:
#         yield channel
#     finally:
#         channel.close()
#         print("[INFO] Closed RabbitMQ", flush=True)
#         logger.info("[INFO] Closed RabbitMQ")



    


        
        
        
    
        

    
        
        


if __name__ == "__main__":
    data_drift_main()