from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, session, flash
from flask_login import LoginManager
from flask_cors import CORS

import pika

import os
from contextlib import contextmanager

ENV = os.environ.get('ENV')

db = SQLAlchemy()
login_manager = LoginManager()
app = Flask(__name__)

if ENV == "DEV":
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost:5455/MLOps_Suite'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db:5455/MLOps_Suite'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'secret'
app.app_context().push()
db.init_app(app)
login_manager.init_app(app)
CORS(app)

if ENV == "DEV":
    rabbitmq_url = 'amqp://user:password@localhost'
else:
    rabbitmq_url = 'amqp://user:password@rabbitmq'


port = 	5672
vhost = '/%2F'

rabbitmq_url_param = pika.URLParameters(f"{rabbitmq_url}:{port}{vhost}")
# rabbitmq_client = pika.BlockingConnection(
#         url_param
#         )

@contextmanager
def open_rabbitmq_connection():
    # for i in range(0, 10):
    #     try:
    #         channel = rabbitmq_client.channel()
    #         # yield channel
    #     except:
    #         print(f"[ERROR] Failed to connect to RabbitMQ. Attempt number {i}", flush=True)
    #         continue
    #     else:
    #         print(f"Successfully connected to RabbitMQ. Attempt number {i}", flush=True)
    #         try:
    #             yield channel
    #         finally:
    #             print("Closed RabbitMQ", flush=True)
    #             channel.close()
    #         break

    rabbitmq_client = pika.BlockingConnection(
        rabbitmq_url_param
        )
    channel = rabbitmq_client.channel()
    print(f"Successfully connected to RabbitMQ", flush=True)
    try:
        yield channel
    except:
        print(f"[ERROR] Failed to connect to RabbitMQ", flush=True)
    finally:
        channel.close()
        print("Closed RabbitMQ", flush=True)


def sql_to_dict(model_instance, query_instance=None):
    if hasattr(model_instance, '__table__'):
        return {c.name: str(getattr(model_instance, c.name)) for c in model_instance.__table__.columns}
    else:
        cols = query_instance.column_descriptions
        return { cols[i]['name'] : model_instance[i]  for i in range(len(cols)) }

def sql_from_dict(dict, model_instance):
    for c in model_instance.__table__.columns:
        setattr(model_instance, c.name, dict[c.name])
    


# CORS(app, resources={
#     r"/*":{
#         "origins":"*"
#     }
# })