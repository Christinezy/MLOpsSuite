
import os
import sys
import json
from database import DB_session
from datetime import datetime
from contextlib import contextmanager
import pandas as pd
import io
import subprocess
import time
import logging
# import models

import pika



curr_dir = os.getcwd()

FILE_SYSTEM = os.path.join(curr_dir, "mlops_files")

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
handler = logging.FileHandler(filename='logs/code_porter.log', mode='w')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler) 


class add_path():
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            sys.path.remove(self.path)
        except ValueError:
            pass

with add_path("./transcoder"):
    translate = __import__("translate")


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


def code_porter_main():
    with open_rabbitmq_connection() as channel:
        while True:
            method_frame, header_frame, body = channel.basic_get(queue="code-porting-queue")
            if method_frame != None and method_frame.NAME == "Basic.GetOk":
                # print(method_frame)
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                try: 
                    data = json.loads(body)
                    # print(data)
                    logger.info(f"New Message: {data}")
                    
                    project_id = data['project_id']
                    version = data['version']
                    source_lang = data['source_lang']
                    target_lang = data['target_lang']
                    filename = data['filename']
                    
                    assert type(project_id) == int
                    assert type(version) == int
                    assert source_lang in ['cpp', 'java', 'python']
                    assert target_lang in ['cpp', 'java', 'python']
                    
                except Exception as err:
                    # print("[ERROR] Failed to process message")
                    # print(body)
                    # print(err)
                    logger.error(f"Failed to process message: {body}")
                    logger.exception(err)


                    channel.basic_publish(exchange="amq.direct", routing_key="code-porting",
                        body = body
                    )
                else:
                    version_dir = os.path.join(FILE_SYSTEM, f"project_{project_id}", f"version_{version}")
                    filepath = os.path.join(version_dir, filename)

                    filename_without_ext = os.path.splitext(filename)[0]
                    target_path = os.path.join(version_dir, f"{filename_without_ext}_{target_lang}")

                    model = ''
                    if (source_lang == 'java') or (source_lang == 'cpp' and target_lang == 'java'):
                        model = './transcoder/models/model_1.pth'
                    elif (source_lang == 'python') or (source_lang == 'cpp' and target_lang == 'python'):
                        model = './transcoder/models/model_2.pth'
                    
                    env = {
                        "DYLD_LIBRARY_PATH": "/Users/daniel/Documents/GitHub/BT4301_Project/services/venv/lib/python3.8/site-packages/clang/native"
                    }

                    # print(filepath, target_path)

                    try:
                        translate.trans(
                            model, "./transcoder/data/BPE_with_comments_codes",
                            source_lang, target_lang,
                            filepath, target_path
                        )
                        # trans(source_lang, target_lang, filepath, target_path)
                        # output = subprocess.call([
                        #     "python", "'./transcoder/translate.py'", f"--model_path='{model}'", "--BPE_path='./transcoder/data/BPE_with_comments_codes'",
                        #     f"--src_lang='{source_lang}'", f"--tgt_lang='{target_lang}'",
                        #     f"--filepath='{filepath}'", f"--target_path='{target_path}'"
                        # ], env=env)
                    except Exception as err:
                        print(err)
                        logger.error(f"[ERROR] Failed to code port {filename} from {source_lang} - {target_lang} in project {project_id} version {version}")
                    else:
                        logger.info(f"[INFO] Success: Code port {filename} from {source_lang} - {target_lang} in project {project_id} version {version}")
            else:
                logger.info('No message')
            time.sleep(3)





if __name__ == "__main__":
    code_porter_main()