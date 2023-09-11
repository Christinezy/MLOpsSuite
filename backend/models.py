from flask import Flask, request, jsonify, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db, login_manager, app




@login_manager.user_loader
def user_loader(id):
    return User.query.get(id)

class User(db.Model, UserMixin):
    __tablename__='users'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    salt = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # 0 for Admin, 1 for Data Dcientise, 2 or Data Engineers, 3 for DevOps Engineers
    # 4 for Business Analytics, 5 for Project Managers
    role = db.Column(db.String(80), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    github_id = db.Column(db.String(80), default=None)
    github_credentials = db.Column(db.String(150), default=None)


    def __repr__(self):
        return '<User %r>' % self.firstname

    def __init__(self, firstname, lastname, email, salt, password, role, date_created, github_id, github_credentials):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.salt = salt
        self.password = password
        self.role = role
        self.date_created = date_created
        self.github_id = github_id
        self.github_credentials = github_credentials


    def serialize(self):
        return {
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "salt": self.salt, 
            "password": self.password,
            "role": self.role,
            "date_created": self.date_created,
            "github_id" : self.github_id,
            "github_credentials" : self.github_credentials,
        }



class Version(db.Model):
    __tablename__ = 'versions'
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    version_number = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    description = db.Column(db.Text)
    created_time = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    last_updated = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    traffic_percentage = db.Column(db.REAL)
    uploaded = db.Column(db.Boolean)
    test_status = db.Column(db.String(80))
    active_status = db.Column(db.String(80))
    deploy_status = db.Column(db.String(80))
    deploy_test = db.Column(db.Integer)
    deployed_before = db.Column(db.Boolean)
    deployment_environment = db.Column(db.String(120))
    approval_status = db.Column(db.String(120))
    pending_approval = db.Column(db.Boolean)
    who_deploy = db.Column(db.String(80))
    logloss = db.Column(db.Double)
    auc_roc = db.Column(db.Double)
    ks_score = db.Column(db.Double)
    gini_norm = db.Column(db.Double)
    rate_top10 = db.Column(db.Double)


    def __repr__(self):
        return "<Project_id=%s version_number=%s>" % (self.project_id, self.version_number)
    

    def __init__(self, project_id, version_number, description=None, created_time = datetime.utcnow, 
                traffic_percentage=0, uploaded=False, test_status="not passed", active_status="Down", deploy_status="not deployed",
                deploy_test=0, deployed_before=False, deployment_environment=None, approval_status="not approved", pending_approval=False,
                who_deploy=None, logloss=None, auc_roc=None, ks_score=None,
                gini_norm=None, rate_top10=None):
        self.project_id = project_id
        self.version_number = version_number
        self.description = description
        self.created_time = created_time
        self.traffic_percentage = traffic_percentage
        self.uploaded = uploaded
        self.test_status = test_status
        self.active_status = active_status
        self.deploy_status = deploy_status
        self.deploy_test = deploy_test
        self.deployed_before = deployed_before
        self.deployment_environment = deployment_environment
        self.approval_status = approval_status
        self.pending_approval = pending_approval
        self.who_deploy = who_deploy
        self.logloss = logloss
        self.auc_roc = auc_roc
        self.ks_score = ks_score
        self.gini_norm = gini_norm
        self.rate_top10 = rate_top10

        

    def serialize(self):
        return {
            "project_id": self.project_id,
            "version_number": self.version_number,
            "description": self.description,
            "created_time": self.created_time,
            "traffic_percentage": self.traffic_percentage, 
            "uploaded": self.uploaded,
            "test_status": self.test_status,
            "active_status": self.active_status,
            "deploy_status" : self.deploy_status,
            "deploy_test" : self.deploy_test,
            "deployed_before" : self.deployed_before,
            "deployment_environment": self.deployment_environment,
            "approval_status": self.approval_status,
            "pending_approval": self.pending_approval,
            "who_deploy" : self.who_deploy,
            "logloss" : self.logloss,
            "auc_roc" : self.auc_roc,
            "ks_score" : self.ks_score,
            "gini_norm" : self.gini_norm,
            "rate_top10" : self.rate_top10
        }



class Request(db.Model):
    __tablename__ = 'requests'
    request_id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True, unique=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    version_number = db.Column(db.Integer, db.ForeignKey('versions.version_number'), primary_key=True)
    created_time = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    submit_request_comment = db.Column(db.Text)
    handle_request_comment = db.Column(db.Text)
    who_sumbit_request = db.Column(db.String(80), db.ForeignKey('users.email'))
    who_handle_request= db.Column(db.String(80), db.ForeignKey('users.email'))
    request_status = db.Column(db.String(80))

    def __repr__(self):
        return "<Project_id=%s version_number=%s request_id=%s>" % (self.project_id, self.version_number, self.request_id)
    

    def __init__(self,project_id, version_number, created_time = datetime.utcnow, 
                submit_request_comment=None, handle_request_comment=False, who_sumbit_request=None,
                who_handle_request=None, request_status=None):
        self.project_id = project_id
        self.version_number = version_number
        self.created_time = created_time
        self.submit_request_comment = submit_request_comment
        self.handle_request_comment = handle_request_comment
        self.who_sumbit_request = who_sumbit_request
        self.who_handle_request = who_handle_request
        self.request_status = request_status

    
    def serialize(self):
        return {
            "request_id": self.request_id,
            "project_id": self.project_id,
            "version_number": self.version_number,
            "created_time": self.created_time,
            "submit_request_comment": self.submit_request_comment, 
            "handle_request_comment": self.handle_request_comment,
            "who_sumbit_request": self.who_sumbit_request,
            "who_handle_request": self.who_handle_request,
            "request_status" : self.request_status
        }




class Project(db.Model):
    __tablename__='projects'
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(80), nullable=False)
    deployment = db.Column(db.String(80), nullable=False)
    build_environment = db.Column(db.String(80), nullable=False)
    total_prediction = db.Column(db.Integer, nullable=False)
    total_requests = db.Column(db.Integer, nullable=False)
    cpu_usage = db.Column(db.Double, nullable=False)
    ram_usage = db.Column(db.Double, nullable=False)
    num_containers = db.Column(db.Integer, nullable=False)
    cpu_threshold = db.Column(db.Double, nullable=False)
    owner = db.Column(db.Integer, nullable=False)
    model_age = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String(200), nullable=False)
    min_num_nodes = db.Column(db.Integer, nullable=False, default=1)
    max_num_nodes = db.Column(db.Integer, nullable=False, default=3)
    desired_num_nodes = db.Column(db.Integer, nullable=False, default=1)


    def __repr__(self):
        return '<Project %r>' % self.name

    def __init__(self, name, status, deployment, build_environment, total_prediction, total_requests, cpu_usage, ram_usage, num_containers, cpu_threshold, owner, model_age, date_created):
        self.name = name
        self.status = status
        self.deployment = deployment
        self.build_environment = build_environment
        self.total_prediction = total_prediction
        self.total_requests = total_requests
        self.cpu_usage = cpu_usage
        self.ram_usage = ram_usage
        self.num_containers = num_containers
        self.cpu_threshold = cpu_threshold
        self.owner = owner
        self.model_age = model_age
        self.date_created = date_created





class Performance(db.Model):
    __tablename__='performance'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, primary_key=True)
    total_prediction = db.Column(db.Integer, nullable=False)
    total_requests = db.Column(db.Integer, nullable=False)
    # average_response_time = db.Column(db.Double, nullable=False)
    cpu_usage = db.Column(db.Double, nullable=False)
    ram_usage = db.Column(db.Double, nullable=False)
    num_containers = db.Column(db.Integer, nullable=False)


    def __repr__(self):
        return '<Peformance %r>' % self.project_id

    def __init__(self, project_id, total_prediction, total_requests, cpu_usage, ram_usage, num_containers):
        self.project_id = project_id
        self.total_prediction = total_prediction
        self.total_requests = total_requests
        # self.average_response_time = average_response_time
        self.cpu_usage = cpu_usage
        self.ram_usage = ram_usage
        self.num_containers = num_containers



class Data_Drift(db.Model):
    __tablename__='data_drift'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, primary_key=True)
    logloss = db.Column(db.Double, nullable=False)
    auc_roc = db.Column(db.Double, nullable=False)
    ks_score = db.Column(db.Double, nullable=False)
    gini_norm = db.Column(db.Double, nullable=False)
    rate_top10 = db.Column(db.Double, nullable=False)
    


    def __repr__(self):
        return '<Data Drift %r>' % self.project_id

    def __init__(self, project_id, logloss, auc_roc, ks_score, gini_norm, rate_top10):
        self.project_id = project_id
        self.logloss = logloss
        self.auc_roc = auc_roc
        self.ks_score = ks_score
        self.gini_norm = gini_norm
        self.rate_top10 = rate_top10

       