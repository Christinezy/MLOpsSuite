from flask import Flask, request, jsonify, session, flash, redirect, url_for, render_template, Response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, app, login_manager
from extensions import open_rabbitmq_connection
from extensions import sql_to_dict, sql_from_dict
from datetime import datetime, timedelta
from models import User, Project, Performance, Data_Drift, Version, Request
from sqlalchemy import desc
from functools import wraps
from getcode import get_code
import json
import jwt
import os
import re
from io import StringIO
import io
import base64
import sys
import shutil

from pylint.lint import Run
from pylint.reporters.text import TextReporter
import html_linter
import cpplint

from pylint.lint import pylinter
pylinter.MANAGER.clear_cache()

# API route

# File System
# curr_dir = os.path.dirname(os.getcwd())
# FILE_SYSTEM = os.path.relpath("./services/mlops_files", curr_dir)
FILE_SYSTEM = os.path.abspath("../services/mlops_files")


@app.route("/")
def hello_world():
    return jsonify(Message="BT4301 Project")


@app.route("/test", methods=["GET", "POST"])
def hello_test():
    print("test logs")
    if request.method == "POST":
        req_body = request.get_json()
        message = req_body['message']
        return jsonify({
            "server": "Flask",
            "message_received": message
        })

    return jsonify(Message="Test Message")


def test_connect_db():
    print("test connect db")
    try:
        db.session.query(db.text('1')).all()
        print("Connected to the database successfully.")
    except Exception as e:
        print("Failed to connect to the database.")
        print(e)


# # decorator for verifying the JWT
# def decode_auth_token(*args, **kwargs):
#     """
#     Decodes the auth token
#     :param auth_token:
#     :return: integer|string
#     """
#     auth_token = request.headers['Authorization']

#     if not auth_token:
#         return jsonify({'message' : 'Token is missing !!'}), 401

#     try:
#         payload = jwt.decode(auth_token, app.config.get('SECRET'))
#         return payload['id']
#     except jwt.ExpiredSignatureError:
#         return 'Signature expired. Please log in again.'
#     except jwt.InvalidTokenError:
#         return 'Invalid token. Please log in again.'


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split("Bearer")[1].strip()
        # return 401 if token is not passed
        if not token:
            return jsonify({
                'error_message': 'Token is missing !!'
            }), 401

        try:
            # decoding the payload to fetch the stored details

            print(token, flush=True)
            data = jwt.decode(token, "secret", algorithms=['HS256'], )

            print(data, flush=True)
            current_user = User.query\
                .filter_by(id=data['user_id'])\
                .first()
        except Exception as e:
            print(e)
            return jsonify({
                'error_message': 'Token is invalid !!'
            }), 401
        # returns the current logged in users context to the routes
        return f(current_user, *args, **kwargs)

    return decorated


# admin create user route
# @login_required
@app.route("/admin/create_user", methods=["POST"])
def admin_create_user():
    args = request.get_json()
    firstname = args.get("firstname")
    lastname = args.get("lastname")
    email = args.get("email")
    salt = os.urandom(8).hex()
    raw_password = args.get("password")
    salted_password = salt + raw_password
    # encrypt password
    password = generate_password_hash(salted_password)
    role = args.get("role")
    github_credentials = args.get("github_credentials")
    github_id = args.get("github_id")
    date_created = datetime.now()
    regex = r"[^@]+@[^@]+\.[^@]+"

    # if empty flash a message
    if firstname == '' or lastname == '' or email == '' or raw_password == '' or role == '' or \
            firstname == None or lastname == None or email == None or raw_password == None or role == None or \
            github_credentials == '' or github_credentials == None or github_id == '' or github_id == None:

        body = {
            "status": "error",
            "error_message": "Missing firstname / lastname / email / password / role / github_id / github_credentials"
        }
        return jsonify(body)

    if not re.fullmatch(regex, email):
        flash("Invalid Email!")
        body = {
            "status": "error",
            "error_message": "Invalid Email"
        }
        return jsonify(body)

    # query User.id by email, if value is Not Null promt user exists
    if User.query.filter_by(email=email).first() is not None:
        # flash("The email has already being used, user exists")
        body = {
            "status": "error",
            "error_message": "Error: The email has already been used, user exists"
        }
        return jsonify(body)

    # if not make a new User instance with values
    try:
        created_user = User(firstname, lastname, email, salt, password,
                            role, date_created, github_id, github_credentials)
        db.session.add(created_user)
        db.session.commit()
        db.session.remove()

        body = {
            "status": "success",
            "error_message": None
        }

        return jsonify(body)
        # return Response(response = json.dumps(body, default=str), mimetype="application/json")

    except Exception as e:
        # flash("Error creating new user")
        print(e, flush=True)

        body = {
            "status": "error",
            "error_message": "Error creating user"
        }
        return jsonify(body)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Login with flask_login
    if request.method == "POST":
        try:
            data = request.get_json()
            email = data["email"].lower().strip()
            raw_password = data["password"]
        except Exception as err:
            body = {
                "status": "failed",
                "error_message": "Missing email / password",
            }
            return jsonify(body)

        user = User.query.filter_by(email=email).first()

        if user:
            salt = user.salt
            salted_password = salt + raw_password
            if check_password_hash(user.password, salted_password):

                payload = {
                    'user_id': user.id,
                    # 'exp': datetime.utcnow() + timedelta(minutes=480) + timedelta(days=10)
                }

                token = jwt.encode(
                    payload, app.config['SECRET_KEY'], algorithm='HS256')
                role = ["Admin", "Data Scientist", "Manager", "MLOps Engineer"][int(user.role)]

                body = {
                    "status": "success",
                    "error_message": "",
                    "token": token,
                    "name": user.firstname,
                    "role": role
                }

                return jsonify(body)

    body = {
        "status": "fail",
        "error_message": "Invalid username/password"
    }

    return jsonify(body)


# # 0 for Admin, 1 for Data Dcientise, 2 or Data Engineers, 3 for DevOps Engineers
# # 4 for Business Analytics, 5 for Project Managers
# @app.route("/authenticate", methods=["GET","POST"])
# def authenticate():
#     if current_user.role == "0":
#         return redirect(url_for("admin_dashboard"))
#     elif current_user.role in [ "1", "2", "3", "4", "5"]:
#         return redirect(url_for("user_dashboard"))
#     else:
#         return redirect(url_for("login"))


# @app.route("/admin_dashboard")
# @login_required
# def admin_dashboard():
#     if current_user.role == "0":
#     flash("You are not authorized to view this page")


# @app.route("/user_dashboard")
# @login_required
# def user_dashboard():
#     if current_user.role in [ "1", "2", "3", "4", "5"]:
#     flash("You are not authorized to view this page")


@app.route("/logout", methods=['GET', 'POST'])
@token_required
def logout(user):
    try:
        # logout_user()
        body = {
            "error_message": "",
            "status": "success",
        }

        return jsonify(body)
    except:
        body = {
            "error_message": "Invalid token",
            "status": "failed"
        }
        return jsonify(body)


@app.route("/list-projects")
@token_required
def list_projects(user):

    data = []
    all_projects = Project.query.all()
    project_ids = [project.id for project in all_projects]

    for id in project_ids:
        project = get_project_overview(id)
        data.append(json.loads(project.data))

    body = {
        "data": data
    }

    return jsonify(body)


@app.route("/project/<int:project_id>/overview")
@token_required
def get_project_overview(user, project_id):

    project = Project.query.filter_by(id=project_id).first()
    version = Version.query.filter(Version.project_id == project_id).filter(
        # Version.active_status == 'Active'
    ).first()
    performance = Performance.query.filter(
        Performance.project_id == project_id).order_by(Performance.timestamp).first()

    body = {
        # "status": "success",
        # "error_message": "",
        "project_id": project.id,
        "project_name": project.name,
        "date_created": project.date_created,
        "description": version.description,
        "endpoint": "http://196.168.49.2/" + str(project_id) + "/predict",
        "status": project.status,
        "deployment": project.deployment,
        "build_environment": project.build_environment,
        "owner": get_project_owner_name(project.owner),
        "approval_status": version.approval_status,
        "model_age": project.model_age,
        "performance": check_project_performance(project_id),
        "drift": check_project_data_drift(project_id),
        "average_prediction": performance.total_prediction,
        "min_num_nodes": project.min_num_nodes,
        "max_num_nodes": project.max_num_nodes,
        "desired_num_nodes": project.desired_num_nodes,
    }

    return jsonify(body)


@app.route("/user/<int:owner_id>/name")
def get_project_owner_name(owner_id):
    user = User.query.filter(User.id == owner_id).first()
    return user.firstname


@app.route("/project/<int:project_id>/calculate_performance")
def check_project_performance(project_id):

    latest_performance = Performance.query.filter(Performance.project_id == project_id).order_by(desc(Performance.timestamp)).first()
    num_containers = latest_performance.num_containers
    
    project = Project.query.filter(Project.id == project_id).first()
    threshold = project.max_num_nodes
    status = "Ok"

    # will update status from "Ok" to "At Risk" if number of containers is more than 65% of max nodes set for elastic scaling 
    if num_containers > (0.65 * threshold):
        status = "At Risk"

    # will update status to "Failing" if number of containers is more than 80% of max nodes set for elastic scaling
    if num_containers > (0.80 * threshold):
        status = "Failing"

    # body = {
    #     "value": calculated_metrics,
    #     "threshold": threshold,
    #     "status": status,
    #     "time1": first_performance.timestamp,
    #     "time2": latest_performance.timestamp
    # }

    return status


@app.route("/project/<int:project_id>/calculate_drift")
def check_project_data_drift(project_id):

    first_data_drift = Data_Drift.query.filter(Data_Drift.project_id == project_id).order_by(Data_Drift.timestamp).first()
    latest_data_drift = Data_Drift.query.filter(Data_Drift.project_id == project_id).order_by(desc(Data_Drift.timestamp)).first()

    log_loss_drift = abs(latest_data_drift.logloss - first_data_drift.logloss) / first_data_drift.logloss
    auc_roc_drift = abs(latest_data_drift.auc_roc - first_data_drift.auc_roc) / first_data_drift.auc_roc
    ks_score_drift = abs(latest_data_drift.ks_score - first_data_drift.ks_score) / first_data_drift.ks_score
    gini_norm_drift = abs(latest_data_drift.gini_norm - first_data_drift.gini_norm) / first_data_drift.gini_norm
    rate_top10_drift = abs(latest_data_drift.rate_top10 - first_data_drift.rate_top10) / first_data_drift.rate_top10

    threshold = 0.1  
    status = "Ok"

    calculated_metrics = [log_loss_drift, auc_roc_drift, ks_score_drift, gini_norm_drift, rate_top10_drift]

    # will update status from "Ok" to "At Risk" if any metrics change by more than 10% 
    if any(metric > threshold for metric in calculated_metrics):
        status = "At Risk"

    # will update status to "Failing" if 3 or more metrics change by more than 10%
    if sum(metric > threshold for metric in calculated_metrics) >= 3:
        status = "Failing"

    # body = {
    #     "value": calculated_metrics,
    #     "threshold": threshold,
    #     "status": status,
    #     "time1": first_data_drift.timestamp,
    #     "time2": latest_data_drift.timestamp
    # }

    return status


@app.route("/project/<int:project_id>/performance")
@token_required
def get_project_performance(user, project_id):

    # Take the last 60 entries which corresponds to last 10 min or more if there is insufficient data
    performance_timeseries = Performance.query.filter(
        Performance.project_id == project_id).order_by(Performance.timestamp.desc()).limit(180).all()
    
    # Correct the order of the data
    performance_timeseries = performance_timeseries[::-1]

    body = {
        "data": [{
            "timestamp": performance.timestamp,
            "total_prediction": performance.total_prediction,
            "total_requests": performance.total_requests,
            # "average_response_time": performance.average_response_time,
            "cpu_usage": performance.cpu_usage,
            "ram_usage": performance.ram_usage,
            "num_containers": performance.num_containers
        } for performance in performance_timeseries]
    }

    return jsonify(body)


@app.route("/project/<int:project_id>/data-drift")
@token_required
def get_project_data_drift(user, project_id):

    data_drift_timeseries = Data_Drift.query.filter(
        Data_Drift.project_id == project_id).order_by(Data_Drift.timestamp.desc()).limit(180).all()
    
    # Correct the order of the data
    data_drift_timeseries = data_drift_timeseries[::-1]

    body = {
        "data": [{
            "timestamp": data_drift.timestamp,
            'logloss': data_drift.logloss,
            'auc_roc': data_drift.auc_roc,
            'ks_score': data_drift.ks_score,
            'gini_norm': data_drift.gini_norm,
            'rate_top10': data_drift.rate_top10
            # "accuracy": data_drift.accuracy,
            # "recall": data_drift.recall,
            # "precision": data_drift.precision,
            # "f1_score": data_drift.f1_score,
            # "ks_score": data_drift.ks_score,
            # "auc_roc": data_drift.auc_roc
        } for data_drift in data_drift_timeseries]
    }

    return jsonify(body)


@app.route("/list-project-manager/<int:project_id>")
@token_required
def list_project_manager(user, project_id):

    project_owner = Project.query.filter_by(id=project_id).first().owner

    manager = User.query.filter(User.id == project_owner).first()

    body = {
        "manager_name": manager.firstname,
        "manager_email": manager.email
    }

    return jsonify(body)

@app.route("/get-project-threshold/<int:project_id>")
@token_required
def get_project_threshold(user, project_id):
    project = Project.query.filter_by(id=project_id).first()

    body = {
        "cpu_threshold": project.cpu_threshold
    }

    return jsonify(body)


@app.route("/update-project-threshold/<int:project_id>/<float:threshold>")
@token_required
def update_project_threshold(user, project_id, threshold):

    Project.query.filter_by(id=project_id).update({
        Project.cpu_threshold: threshold
    })

    db.session.commit()

    project = Project.query.filter_by(id=project_id).first()

    body = {
        "updated_threshold": project.cpu_threshold
    }

    return jsonify(body)


@app.route("/project/<int:project_id>/create-deployment", methods=['POST'])
@token_required
def project_create_deployment(user, project_id):

    if request.method == "POST":
        req_body = request.get_json()

        try:
            environment = req_body['environment']
            strategy = req_body['strategy']
            assert strategy in ['direct', "blue/green", "canary"]

            version = int(req_body['version'])

            assert type(version) == int

            # # Special case for direct deployment
            # if strategy == 'direct':
            #     try:
            #         # Attempt to delete existing deployment first
            #         project_delete_deployment(project_id)
            #     except Exception as err:
            #         print(err)
            #         body = {
            #             "status": "failed",
            #             "error_message": "Failed to delete existing deployment"
            #         }
            #         return jsonify(body)

            print("[INFO]", environment, project_id, strategy, version)

            deploy_msg = {
                'command': 'deploy',
                'environment': environment,
                "project_id": project_id,
                "strategy": strategy,
                "version": version,
                "who_deploy": user.email
            }

            deploy_msg_str = json.dumps(deploy_msg)
        except Exception as err:
            print(err)

            body = {
                "status": "failed",
                "error_message": "Missing information"
            }
            return jsonify(body)
        else:
            try:
                with open_rabbitmq_connection() as channel:
                    channel.basic_publish(
                        exchange="amq.direct",
                        routing_key="model-deploy",
                        body=deploy_msg_str
                    )
            except Exception as err:
                print(err)

                body = {
                    "status": "failed",
                    "error_message": "Failed to send message to rabbitmq"
                }
                return jsonify(body)
            else:
                body = {
                    "status": "success",
                    "error_message": ""
                }
                return jsonify(body)


@app.route("/project/<int:project_id>/delete-deployment", methods=['POST'])
@token_required
def project_delete_deployment(user, project_id):
    if request.method == "POST":
        req_body = request.get_json()
        try:
            environment = req_body['environment']
            # strategy = req_body['strategy']
            # assert strategy in ['direct', "blue/green", "canary"]

            version = int(req_body['version'])

            assert type(version) == int

            print("[INFO]", environment, project_id, version)

            deploy_msg = {
                'command': 'delete',
                # 'environment': environment,
                "project_id": project_id,
                # "strategy": strategy,
                "version": version
            }

            deploy_msg_str = json.dumps(deploy_msg)
            print("[INFO]", deploy_msg_str)
        except Exception as err:
            print(err)

            body = {
                "status": "failed",
                "error_message": "Missing information"
            }
            return jsonify(body)
        else:
            try:
                with open_rabbitmq_connection() as channel:
                    channel.basic_publish(
                        exchange="amq.direct",
                        routing_key="model-deploy",
                        body=deploy_msg_str
                    )
            except Exception as err:
                print(err)

                body = {
                    "status": "failed",
                    "error_message": "Failed to send message to rabbitmq"
                }
                return jsonify(body)
            else:
                body = {
                    "status": "success",
                    "error_message": ""
                }
                return jsonify(body)


@app.route("/project/<int:project_id>/update-hpa", methods=['POST'])
@token_required
def project_update_hpa(user, project_id):

    if request.method == "POST":
        req_body = request.get_json()

        try:
            min_nodes = req_body['min_nodes']
            max_nodes = req_body['max_nodes']
            desired_nodes = req_body['desired_nodes']

            assert type(min_nodes) == int
            assert type(max_nodes) == int
            assert type(desired_nodes) == int
        except Exception as err:
            print(err)

            body = {
                "status": "failed",
                "error_message": "Missing information"
            }
            return jsonify(body)
        else:
            # Check if project is live
            project = Project.query.filter_by(id=project_id).first()

            if project.status != "Live":
                body = {
                    "status": "failed",
                    "error_message": "Project has not been deployed"
                }
                return jsonify(body)

            print("[INFO]", 'update-hpa', min_nodes, max_nodes, desired_nodes)

            # Prepare rabbitmq message
            deploy_msg = {
                'command': 'update-hpa',
                "project_id": project_id,
                "version": 1,  # TODO: Update version to be from project table
                'min_nodes': min_nodes,
                'max_nodes': max_nodes,
                'desired_nodes': desired_nodes
            }

            deploy_msg_str = json.dumps(deploy_msg)

            try:
                with open_rabbitmq_connection() as channel:
                    channel.basic_publish(
                        exchange="amq.direct",
                        routing_key="model-deploy",
                        body=deploy_msg_str
                    )
            except Exception as err:
                print(err)

                body = {
                    "status": "failed",
                    "error_message": "Failed to send message to rabbitmq"
                }
                return jsonify(body)
            else:
                body = {
                    "status": "success",
                    "error_message": ""
                }
                return jsonify(body)


@app.route("/project/<int:project_id>/go-live", methods=['POST'])
@token_required
def project_go_live(user, project_id):

    if request.method == "POST":
        req_body = request.get_json()

        print(req_body)

        try:
            # min_nodes = req_body['min_nodes']
            # max_nodes = req_body['max_nodes']
            # desired_nodes = req_body['desired_nodes']
            version = int(req_body['version'])

            assert type(version) == int

            # assert type(min_nodes) == int
            # assert type(max_nodes) == int
            # assert type(desired_nodes) == int
            # print(f"Here")
        except Exception as err:
            print(err)

            body = {
                "status": "failed",
                "error_message": "Missing information"
            }
            return jsonify(body)
        else:
            # Check if project is live
            project = Project.query.filter_by(id=project_id).first()

            if project.status != "Live":
                body = {
                    "status": "failed",
                    "error_message": "Project has not been deployed"
                }
                return jsonify(body)

            print("[INFO]", f"Go Live: Project {project_id}")

            # Get new Version
            new_version = Version.query.filter_by(
                version_number=version, active_status="Test").first()

            if new_version == None:
                body = {
                    "status": "failed",
                    "error_message": "Version is not undergoing blue/green deployment"
                }
                return jsonify(body)

            # Prepare rabbitmq message
            deploy_msg = {
                'command': 'go-live',
                "project_id": project_id,
                "version": version
            }

            deploy_msg_str = json.dumps(deploy_msg)

            try:
                with open_rabbitmq_connection() as channel:
                    channel.basic_publish(
                        exchange="amq.direct",
                        routing_key="model-deploy",
                        body=deploy_msg_str
                    )

                # Update db
                new_version.active_status = "Going Live"
                db.session.commit()
                db.session.remove()
            except Exception as err:
                print(err)

                body = {
                    "status": "failed",
                    "error_message": "Failed to send message to rabbitmq"
                }
                return jsonify(body)
            else:
                body = {
                    "status": "success",
                    "error_message": ""
                }
                return jsonify(body)


@app.route("/project/<int:project_id>/model/versions/<int:version_number>/code-port", methods=["POST"])
@token_required
def handle_code_porting_request(user, project_id, version_number):
    if request.method == "POST":
        req_body = request.get_json()
        try:
            filename = req_body["filename"]
            source_lang = req_body["source_lang"]
            target_lang = req_body["target_lang"]

            try:
                assert source_lang in ['cpp', "java", "python"]
                assert target_lang in ['cpp', "java", "python"]
            except Exception as err:
                body = {
                    "status": "failed",
                    "error_message": "Source/Target language not supported"
                }
                return jsonify(body)

            # Check if version and project exists
            version = Version.query.filter_by(
                project_id=project_id, version_number=version_number).first()

            if version == None:
                body = {
                    "status": "failed",
                    "error_message": "Version does not exist"
                }
                return jsonify(body)

            # Check if file exist
            project_dir = os.path.join(FILE_SYSTEM, f"project_{project_id}")
            version_dir = os.path.join(
                project_dir, f"version_{version_number}")

            filepath = os.path.join(version_dir, filename)

            if not os.path.isfile(filepath):
                body = {
                    "status": "failed",
                    "error_message": "File does not exist"
                }
                return jsonify(body)

            # Check if the target type matches the file extension
            ext = os.path.splitext(filepath)[-1].lower()
            # print(ext)
            try:
                if source_lang == "python":
                    assert ext == ".py"
                elif source_lang == "java":
                    assert ext == ".java"
                elif source_lang == "cpp":
                    assert ext == ".cpp"
            except Exception as err:
                print(err)
                body = {
                    "status": "failed",
                    "error_message": "Source language does not match file"
                }
                return jsonify(body)

            # Queue code porting job
            try:
                with open_rabbitmq_connection() as channel:
                    code_port_msg = {
                        'project_id': project_id,
                        "version": version_number,
                        'filename': filename,
                        "source_lang": source_lang,
                        "target_lang": target_lang
                    }
                    code_port_msg_str = json.dumps(code_port_msg)
                    channel.basic_publish(
                        exchange="amq.direct",
                        routing_key="code-porting",
                        body=code_port_msg_str
                    )
            except Exception as err:
                print(err)
                body = {
                    "status": "failed",
                    "error_message": "Failed to send code porting message to RabbitMQ"
                }
                return jsonify(body)
            else:
                body = {
                    "status": "success",
                    "error_message": ""
                }
                return jsonify(body)

        except Exception as err:
            print(err)
            body = {
                "status": "failed",
                "error_message": "Missing information"
            }
            return jsonify(body)


@app.route("/project/<int:project_id>/model/versions/<int:version_number>/get-file", methods=["POST"])
@token_required
def handle_get_file_request(user, project_id, version_number):
    if request.method == "POST":
        req_body = request.get_json()
        try:
            filename = req_body["filename"]

            # Check if version and project exists
            version = Version.query.filter_by(
                project_id=project_id, version_number=version_number).first()

            if version == None:
                body = {
                    "status": "failed",
                    "error_message": "Version does not exist"
                }
                return jsonify(body)

            # Check if file exist
            project_dir = os.path.join(FILE_SYSTEM, f"project_{project_id}")
            version_dir = os.path.join(
                project_dir, f"version_{version_number}")

            filepath = os.path.join(version_dir, filename)

            if not os.path.isfile(filepath):
                body = {
                    "status": "failed",
                    "error_message": "File does not exist"
                }
                return jsonify(body)

            # Check if the target type matches the file extension
            ext = os.path.splitext(filepath)[-1].lower()
            # print(ext)
            if ext not in ['.py', '.java', '.cpp']:
                print(err)
                body = {
                    "status": "failed",
                    "error_message": "File is not python, java or cpp"
                }
                return jsonify(body)

            # Get file
            try:
                with open(filepath, 'rb') as file:
                    payload = {
                        "status": "success",
                        "error_message": ""
                    }

                    base64_bytes = base64.b64encode(file.read())
                    base64_str = base64_bytes.decode("utf-8")

                    payload['data'] = base64_str
                    return jsonify(payload)
            except Exception as err:
                print(err)
                body = {
                    "status": "failed",
                    "error_message": "Failed to send file"
                }
                return jsonify(body)
        except Exception as err:
            print(err)
            body = {
                "status": "failed",
                "error_message": "Missing information"
            }
            return jsonify(body)

@app.route("/project/<int:project_id>/model/versions/<int:version_number>/save-file", methods=["POST"])
@token_required
def handle_save_file_request(user, project_id, version_number):
    if request.method == "POST":
        req_body = request.get_json()
        try:
            filename = req_body['filename']
            file_data = req_body["file"]

            # Check if version and project exists
            version = Version.query.filter_by(
                project_id=project_id, version_number=version_number).first()

            if version == None:
                body = {
                    "status": "failed",
                    "error_message": "Version does not exist"
                }
                return jsonify(body)

            # Check if file exist
            project_dir = os.path.join(FILE_SYSTEM, f"project_{project_id}")
            version_dir = os.path.join(
                project_dir, f"version_{version_number}")

            filepath = os.path.join(version_dir, filename)

            if not os.path.isfile(filepath):
                body = {
                    "status": "failed",
                    "error_message": "File does not exist"
                }
                return jsonify(body)

            # Check if the target type matches the file extension
            ext = os.path.splitext(filepath)[-1].lower()
            # print(ext)
            if ext not in ['.py', '.java', '.cpp']:
                print(err)
                body = {
                    "status": "failed",
                    "error_message": "File is not python, java or cpp"
                }
                return jsonify(body)

            # Save file
            try:
                # base64_bytes = base64.b64encode(file.read())
                # base64_str = base64_bytes.decode("utf-8")
                # base64_str = file_data.decode("utf-8")
                file_bytes = base64.b64decode(file_data)
                # file_str = file_bytes.decode("utf-8")
                # base64_str = base64_bytes.decode("utf-8")
                with open(filepath, 'wb') as file:
                    file.write(file_bytes)
                
                    payload = {
                        "status": "success",
                        "error_message": ""
                    }
                    return jsonify(payload)
            except Exception as err:
                print(err)
                body = {
                    "status": "failed",
                    "error_message": "Failed to send file"
                }
                return jsonify(body)
        except Exception as err:
            print(err)
            body = {
                "status": "failed",
                "error_message": "Missing information"
            }
            return jsonify(body)

# TO DELETE 
@app.route("/get_linting_comments", methods=["POST"])
def get_linting_comments_old():
    if (request.method == "POST"):
        req_body = request.files['file']
        file_type = request.form.get('file_type')
        file_contents = req_body.read()
        pylint_output = StringIO()  # Custom open stream
        if file_type == 'py':
            py_file_name = 'model_py.py'
            reporter = TextReporter(pylint_output)

            with open(py_file_name, 'wb') as file:
                file.write(file_contents)
            # Run(['--ignored-modules=sklearn',f"{py_file_name}"], reporter=reporter, exit=False)
            Run([f"{py_file_name}"], reporter=reporter, exit=False)
            os.remove(f"{py_file_name}")
            error_message = pylint_output.getvalue()

        elif file_type == 'html':
            html_file_name = 'model_html.html'
            with open(html_file_name, 'wb') as file:
                file.write(file_contents)
            clean_html = html_linter.template_remover.clean(
                io.open(html_file_name).read())
            error_message = html_linter.lint(clean_html)
            os.remove(f"{html_file_name}")

        elif (file_type == 'cpp') | (file_type == 'c') :
            sys.stderr = open('output.txt','wt')
            cpp_file_name = 'model_cpp.cpp'
            with open(cpp_file_name, 'wb') as file:
                file.write(file_contents)
            cpplint.ProcessFile(cpp_file_name,5)
            sys.stderr.close()
            with open('output.txt', 'r') as f:
                error_message = f.read()
            os.remove(f"{cpp_file_name}")
            os.remove('output.txt')
        else:
            return jsonify({
                "status": "failed",
                "error_message": "Wrong File format"
            })
    
        return jsonify({
            "status": "success",
            "error_message": error_message
        })
    else:
        print("request is not a get req")
        return Response(status=404)



@app.route("/project/<int:project_id>/model/versions/<int:version_number>/lint-comments", methods=["POST"])
@token_required
def get_linting_comments(user, project_id, version_number):
    if (request.method == "POST"):
        req_body = request.get_json()
        try:
            filename = req_body["filename"]
            
            # Check if file exist
            project_dir = os.path.join(FILE_SYSTEM, f"project_{project_id}")
            version_dir = os.path.join(
                project_dir, f"version_{version_number}")

            filepath = os.path.join(version_dir, filename)

            if not os.path.isfile(filepath):
                body = {
                    "status": "failed",
                    "error_message": "File does not exist"
                }
                return jsonify(body)
            ext = os.path.splitext(filepath)[-1].lower()[1:]
            try:
                assert ext in ['py', "html", "cpp", 'c']
            except Exception as err:
                body = {
                    "status": "failed",
                    "error_message": "Source language not supported"
                }
                return jsonify(body)
            
            if ext == 'py':
                pylint_output = StringIO()  # Custom open stream
                reporter = TextReporter(pylint_output)
                # Run(['--ignored-modules=sklearn',f"{py_file_name}"], reporter=reporter, exit=False)
                Run([f"{filepath}"], reporter=reporter, exit=False)
                error_message = pylint_output.getvalue()

            elif ext == 'html':
                clean_html = html_linter.template_remover.clean(
                    io.open(filepath).read())
                error_message = html_linter.lint(clean_html)

            elif (ext == 'cpp') | (ext == 'c') :
                sys.stderr = open('output.txt','wt')
                cpplint.ProcessFile(filepath,5)
                sys.stderr.close()
                with open('output.txt', 'r') as f:
                    error_message = f.read()
                os.remove('output.txt')
        
            error_message = error_message.replace(version_dir+'\\','')

            return jsonify({
                "status": "success",
                "error_message": error_message
            })
        except Exception as err:
            print(err)
            body = {
                "status": "failed",
                "error_message": "Missing information"
            }
            return jsonify(body)
    else:
        print("request is not a get req")
        return Response(status=404)

# versions


@app.route("/project/<int:project_id>/model/versions/list_versions")
@token_required
def list_versions(user, project_id):
    versions = Version.query.with_entities(
        Version.version_number,
        Version.created_time,
        Version.last_updated,
        Version.test_status,
        Version.description,
        Version.approval_status,
        Version.deploy_status,
        Version.deploy_test,
        Version.active_status,
        Version.deployed_before,
        Version.who_deploy,
        Version.logloss,
        Version.auc_roc,
        Version.ks_score,
        Version.gini_norm,
        Version.rate_top10,
        Version.traffic_percentage
    ).filter_by(project_id=project_id).order_by(Version.version_number.desc()).all()

    data = []
    version_number_list = []
    for version in versions:
        version_dict = {
            "version_number": version[0],
            "created": version[1],
            "last_updated": version[2],
            "test_status": version[3],
            "version_description": version[4],
            "approval_status": version[5],
            "deploy_status": version[6],
            "deploy_test": version[7],
            "active_status": version[8],
            "deployed_before": version[9],
            "who_deploy": version[10],
            "logloss": version[11],
            'auc_roc': version[12],
            "ks_score": version[13],
            "gini_norm": version[14],
            'rate_top10': version[15],
            "traffic": version[16],
        }
        version_number_list.append(str(version[0]))
        data.append(version_dict)

    # get model file name
    try:
        file = []
        parent_path = os.path.dirname(os.getcwd())
        rootfolder1_path = "services"
        rootfolder2_path = "mlops_files"
        project_name = "project_" + str(project_id)
        for version_number in version_number_list:
            version_folder_name = "version_" + version_number
            file_path1 = os.path.join(
                parent_path, rootfolder1_path, rootfolder2_path, project_name, version_folder_name)
            file_path2 = os.path.join(
                parent_path, rootfolder1_path, rootfolder2_path, project_name, version_folder_name, "model")
            
            if not os.listdir(file_path1):
                body = {
                    "error_message": "No file to fecth",
                    "status": "failed"
                }
                return jsonify(body)

            version_files1 = [f for f in os.listdir(
                file_path1) if os.path.isfile(os.path.join(file_path1, f))]
            version_files2 = [f for f in os.listdir(
                file_path2) if os.path.isfile(os.path.join(file_path2, f))]

            if version_files1 and version_files2:
                version_file = version_files1 + version_files2
            elif version_files1:
                version_file = version_files1
            elif version_files2:
                version_file = version_files2
            else:
                version_file = ''


            res = []
            for f in version_file:
                ext = os.path.splitext(f)[1]

                lang_map = {
                    ".py": "python",
                    ".cpp": "c++",
                    ".java": "java"
                }
                lang = lang_map.get(ext, "")
                res.append({"file_name": f, "language_type": lang})

            file.append(res)

        # attach file list to each version
        for i in range(len(data)):
            data[i]["version_files"] = file[i]

        body = {
            "data": data
        }
        return jsonify(body)

    except Exception as err:
        print(err)
        body = {
            "error_message": "Error in fetching file for versions",
            "status": "failed"
        }
        return jsonify(body)


@app.route("/project/<int:project_id>/model/governance/versions/overview")
@token_required
def get_governance_versions(user, project_id):
    try:
        versions = Version.query.with_entities(
            Version.version_number,
            Version.description,
            Version.created_time,
            Version.traffic_percentage,
            Version.test_status,
            Version.active_status,
            Version.deploy_status,
            Version.deploy_test,
            Version.approval_status,
            Version.pending_approval,
            Version.who_deploy
        ).filter_by(project_id=project_id).order_by(Version.version_number.asc()).all()

        data = []
        for v in versions:
            v_dict = {
                "version_number": v.version_number,
                "description": v.description,
                "created_time": v.created_time,
                "traffic_percentage": v.traffic_percentage,
                "test_status": v.test_status,
                "active_status": v.active_status,
                "deploy_status": v.deploy_status,
                "deploy_test": v.deploy_test,
                "approval_status": v.approval_status,
                "pending_approval": v.pending_approval,
                "who_deloy": v.who_deploy,
                "request": []
            }

            # get the requets for each version
            # each v only has 1 request
            get_request = Request.query.with_entities(
                Request.created_time,
                Request.who_sumbit_request,
                Request.submit_request_comment,
                Request.who_handle_request,
                Request.handle_request_comment,
                Request.request_status
            ).filter_by(project_id=project_id, version_number=v.version_number).first()

            # get role for who handle the request
            if get_request:
                role = ''
                if get_request.who_handle_request != None or get_request.who_handle_request != '':
                    who = User.query.filter_by(
                        email=get_request.who_handle_request).first()
                    role_index = int(who.role)
                    role = ["Admin", "Data Scientist",
                            "Manager", "MLOps Engineer"][role_index]

                request = {
                    "created_time": get_request.created_time,
                    "who_sumbit_request": get_request.who_sumbit_request,
                    "submit_request_comment": get_request.submit_request_comment,
                    "who_handle_request": get_request.who_handle_request,
                    "role for approver": role,
                    "handle_request_comment": get_request.handle_request_comment,
                    "request_status": get_request.request_status
                }
                # v_dict.update(request)
                v_dict['request'].append(request)

            data.append(v_dict)

        body = {
            "status": "success",
            "data": data
        }
        return jsonify(body)

    except Exception as err:
        print(err)
        body = {
            "error_message": "Fail to get versions under governance.",
            "status": "failed"
        }
        return jsonify(body)


@app.route("/project/<int:project_id>/model/versions/test", methods=["POST"])
@token_required
def test_version(user, project_id):
    if (request.method == "POST"):
        req_body = request.get_json()
        version_number = int(req_body["version_number"])

        try:
            version = Version.query.filter_by(
                project_id=project_id, version_number=version_number).first()
            version.test_status = "testing"
            db.session.commit()
            db.session.remove()

            body = {
                "message": "Successfully pass the test.",
                "status": "success"
            }
            return jsonify(body)

        except Exception as err:
            print(err)
            body = {
                "error_message": "Fail to pass the test.",
                "status": "failed"
            }
            return jsonify(body)


@app.route("/project/<int:project_id>/model/versions/<int:version_number>/submit_approval_request", methods=["POST"])
@token_required
def submit_approval_request(user, project_id, version_number):
    if request.method == "POST":
        req_body = request.get_json()
        try:
            submit_request_comment = req_body["submit_request_comment"]
            submit_to_who = req_body["submit_to_who"]
            version = Version.query.filter_by(
                project_id=project_id, version_number=version_number).first()

            if submit_to_who == '' or submit_request_comment == '' or submit_to_who == None or submit_request_comment == None:
                body = {
                    "status": "failed",
                    "error_message": "Please select a target peole to view the request."
                }
                return jsonify(body)

            if version.approval_status == "pending approval":
                body = {
                    "status": "failed",
                    "error_message": "Approval request has been submitted."
                }
                return jsonify(body)

            elif version.approval_status == "approved":
                body = {
                    "status": "failed",
                    "error_message": "Request has been approved."
                }
                return jsonify(body)

            elif version.approval_status == "not approved" and submit_request_comment != "" \
                    and submit_request_comment != None:
                version.approval_status = "pending approval"
                version.pending_approval = True
                created_time = datetime.now()
                who_submit = user.email
                handle_request_comment = None
                who_handle = submit_to_who
                request_status = "pending approval"
                new_request = Request(version.project_id, version.version_number, created_time, submit_request_comment,
                                      handle_request_comment, who_submit, who_handle, request_status)
                db.session.add(new_request)
                db.session.commit()
                db.session.remove()

                body = {
                    "status": "success",
                    "error_message": "Request submitted, pending approval."
                }
                return jsonify(body)

        except Exception as err:
            print(err)
            body = {
                "status": "failed",
                "error_message": "Error in submitting approval request."
            }
            return jsonify(body)


@app.route("/project/<int:project_id>/model/requests/handle_approval_request", methods=["POST"])
@token_required
def handle_approval_request(user, project_id):
    if request.method == "POST":
        req_body = request.get_json()
        try:
            is_approved = req_body["approval_result"]
            handle_request_comment = req_body["handle_request_comment"]
            version_number = req_body["version_number"]

            if is_approved == '' or handle_request_comment == '' or is_approved == None or handle_request_comment == None\
               or version_number == '' or version_number == None:
                body = {
                    "status": "error",
                    "error_message": "Please provide all the required information for handle the request."
                }
                return jsonify(body)

            # update version table
            try:
                version = Version.query.filter_by(
                    project_id=project_id, version_number=int(version_number)).first()
                requests = Request.query.filter_by(project_id=project_id, version_number=version_number).\
                    order_by(Request.created_time.desc()).first()
            except Exception as err:
                print(err)
                body = {
                    "status": "failed",
                    "error_message": "Error in querying data."
                }
                return jsonify(body)

            if user.email != requests.who_handle_request:
                body = {
                    "status": "failed",
                    "error_message": "You are not allowed to handle this request."
                }
                return jsonify(body)

            if requests.request_status == "pending approval" and version.approval_status == "pending approval":

                version.pending_approval = False
                version.approval_status = "approved" if is_approved == "true" else "not approved"
                requests.request_status = "approved" if is_approved == "true" else "not approved"
                res = requests.request_status
                requests.handle_request_comment = handle_request_comment
                try:
                    db.session.commit()
                    db.session.remove()
                except Exception as err:
                    print(err)

                body = {
                    "status": "success",
                    "request_status": res
                }
                return jsonify(body)
            elif (requests.request_status == "approved" and version.approval_status == "approved") or \
                    (requests.request_status == "not approved" and version.approval_status == "not approved"):
                body = {
                    "status": "failed",
                    "error_message": "This request has been handled."
                }
                return jsonify(body)

            else:
                body = {
                    "status": "failed",
                    "error_message": "Invalid request. unable to handle."
                }
            return jsonify(body)

        except Exception as err:
            print(err)
            body = {
                "status": "failed",
                "error_message": "Error in handling request."
            }
            return jsonify(body)


@app.route("/project/<int:project_id>/model/active_version/overview")
@token_required
def get_active_version(user, project_id):
    try:
        project = Project.query.filter_by(id=project_id).first()
        active_version = Version.query.filter_by(
            project_id=project_id, active_status="Active").first()

        if active_version:
            body = {
                "active_status": "true",
                "data": {
                    "model_created_time": project.date_created,
                    "deployment_environment": active_version.deployment_environment,
                    "deployment_strategy": project.deployment,
                    "model_name": project.name,
                    "version_number": active_version.version_number
                }
            }
            return jsonify(body)

        else:
            body = {
                "active_status": "false",
                "data": {
                    "model_created_time": project.date_created,
                    "model_name": project.name,
                    "deployment_strategy": project.deployment,
                    "deployment_environment": "",
                    "deployment_strategy": "",
                    "version_number": 0,
                }
            }
            return jsonify(body)

    except Exception as err:
        body = {
            "status": "failed",
            "error_message": "Failed to fetch any active version"
        }
        return jsonify(body)


@app.route("/project/<int:project_id>/requests/list_requests", methods=['GET'])
@token_required
def list_requests(user, project_id):
    try:
        # get active version corresponding to this project
        # normally, 1 active version for each project, but for canary, two versions active
        active_v = Version.query.with_entities(
            Version.version_number,
            Version.active_status,
            Version.logloss,
            Version.auc_roc,
            Version.ks_score,
            Version.gini_norm,
            Version.rate_top10
        ).filter_by(project_id=project_id, active_status="Active").all()

        active_v_list = []
        for version in active_v:
            v_dict = {
                "version_number": version.version_number,
                "active_status": version.active_status,
                "logloss": version.logloss,
                "auc_roc": version.auc_roc,
                "ks_score": version.ks_score,
                "gini_norm": version.gini_norm,
                "rate_top10": version.rate_top10
            }
            active_v_list.append(v_dict)

        # get pending request for this proj
        requests = Request.query.with_entities(
            Request.version_number,
            Request.created_time,
            Request.who_sumbit_request,
            Request.submit_request_comment,
            Request.request_status
        ).filter_by(project_id=project_id, request_status="pending approval")\
            .order_by(Request.version_number.desc()).all()
        requests_list = []
        for req in requests:
            v_dict = {
                "version_number": req.version_number,
                "created_time": req.created_time,
                "who_sumbit_request": req.who_sumbit_request,
                "submit_request_comment": req.submit_request_comment,
                "request_status": req.request_status
            }
            requests_list.append(v_dict)

        # attach version performance to each request
        for req in requests_list:
            v_num = req["version_number"]
            v = Version.query.with_entities(
                Version.logloss,
                Version.auc_roc,
                Version.ks_score,
                Version.gini_norm,
                Version.rate_top10
            ).filter_by(project_id=project_id, version_number=v_num).first()

            v_dic = {
                "logloss": v.logloss,
                "auc_roc": v.auc_roc,
                "ks_score": v.ks_score,
                "gini_norm": v.gini_norm,
                "rate_top10": v.rate_top10
            }
            req.update(v_dic)

        body = {
            "active_version_list": active_v_list,
            "pending_requests": requests_list,
            "status": "success"
        }
        return jsonify(body)

    except Exception as err:
        body = {
            "status": "failed",
            "error_message": "Failed to get pending requests."
        }
        return jsonify(body)


@app.route("/project/<int:project_id>/model/stop_service", methods=['POST'])
@token_required
def stop_service(user, project_id):
    if request.method == "POST":
        try:
            req_body = request.get_json()
            version_number = req_body["version_number"]
            project = Project.query.filter_by(id=project_id).first()
            active_version = Version.query.filter_by(
                project_id=project_id, version_number=version_number).first()

            if active_version and active_version.active_status == "Active":
                active_version.active_status = "Down"
                active_version.deploy_status = "not deployed"
                db.session.commit()

                body = {
                    "active_status": "false",
                    "data": {
                        "model_created_time": project.date_created,
                        "model_name": project.name
                    }
                }
                db.session.remove()
                return jsonify(body)
            else:
                body = {
                    "status": "failed",
                    "error_message": "No active version to stop"
                }
                return jsonify(body)

        except Exception as err:
            body = {
                "status": "failed",
                "error_message": "Failed to stop service"
            }
            return jsonify(body)


@app.route("/project/<int:project_id>/model/create_version", methods=['POST'])
@token_required
def model_create_version(user, project_id):
    if request.method == "POST":
        req_body = request.get_json()

        try:
            latest_version = Version.query.filter_by(project_id=project_id).order_by(
                Version.version_number.desc()).first()
            version_number = int(latest_version.version_number) + 1
            description = req_body["description"]
            github_file_url = req_body["githubFileURL"]
            url_metadata = github_file_url.split('/')
            created_time = datetime.now()
            # test_status = "not passed"
            # actice_status = "Down"
            # traffic_percentage = 0

            if (len(url_metadata) < 1) | ((url_metadata[-1] != '') & ('.' in url_metadata[-1])):
                # example_file_url = "https://github.com/danieltwh/BT4301_Project/blob/main/fake_data/model1.py"
                example_folder_url = "https://github.com/danieltwh/BT4301_Project/blob/main/fake_data/version_latest/"
                body = {
                    "status": "error",
                    "error_message": f"Incorrect URL format, URL should look like [{example_folder_url}]"
                }
                print(body)
                return jsonify(body)
            else:
                if not ('.' in url_metadata[-1]): # folder path but never add /
                    github_file_url += '/'
                    url_metadata = github_file_url.split('/')
                get_code(url_metadata, user.github_id,
                         user.github_credentials, project_id, version_number)

            created_version = Version(
                project_id, version_number, description, created_time)
            db.session.add(created_version)
            db.session.commit()
            created_version = created_version.serialize()
            db.session.remove()
            body = {
                "status": "success",
                "message": "Successfully create new version."
            }

            return jsonify(body)

        except Exception as err:
            body = {
                "status": "failed",
                "error_message": f"Error in creating a new version: {err}"
            }
            return jsonify(body)


if __name__ == "__main__":
    # source env/bin/activate
    # ENV=DEV python main.py

    app.run(debug=True, host="0.0.0.0", port=5050)
