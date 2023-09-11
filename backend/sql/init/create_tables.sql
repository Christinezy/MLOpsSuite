
-- Create users table
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
	id SERIAL PRIMARY KEY,
    firstname VARCHAR(80) NOT NULL,
    lastname VARCHAR(80) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    salt VARCHAR(120) NOT NULL,
    password VARCHAR(200) NOT NULL,
    role VARCHAR(80) NOT NULL,
    date_created timestamp without time zone DEFAULT (now() at time zone 'utc'),
    github_id VARCHAR(150) DEFAULT NULL,
    github_credentials VARCHAR(150) DEFAULT NULL
);


-- Create projects table
DROP TABLE IF EXISTS projects CASCADE;

CREATE TABLE projects (
	id SERIAL PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    status VARCHAR(80) NOT NULL,
    deployment VARCHAR(120) NOT NULL,
    build_environment VARCHAR(120) NOT NULL,
    total_prediction INTEGER,
    total_requests INTEGER,
    cpu_usage REAL,
    ram_usage REAL,
    num_containers INTEGER,
    cpu_threshold REAL,
    owner INTEGER NOT NULL,
    model_age  INTEGER NOT NULL,
    date_created timestamp without time zone NOT NULL DEFAULT (now() at time zone 'utc'),
    url VARCHAR(200) NOT NULL,
    min_num_nodes INTEGER DEFAULT 1,
    max_num_nodes INTEGER DEFAULT 3,
    desired_num_nodes INTEGER DEFAULT 1,
    CONSTRAINT fk_owner 
        FOREIGN KEY (owner) REFERENCES users(id)
        ON DELETE CASCADE
);


-- Create data_drift table
DROP TABLE IF EXISTS data_drift CASCADE;

CREATE TABLE data_drift (
	timestamp timestamp without time zone NOT NULL DEFAULT (now() at time zone 'utc'),
    project_id INTEGER,
    logloss REAL,
    auc_roc REAL,
    ks_score REAL,
    gini_norm REAL,
    rate_top10 REAL,
    CONSTRAINT comp_name PRIMARY KEY (timestamp, project_id),
    UNIQUE(timestamp, project_id),
    CONSTRAINT fk_project_id 
        FOREIGN KEY (project_id) REFERENCES projects(id)
        ON DELETE CASCADE
);


-- Create performance table
DROP TABLE IF EXISTS performance CASCADE;

CREATE TABLE performance (
	timestamp timestamp without time zone NOT NULL DEFAULT (now() at time zone 'utc'),
    project_id INTEGER,
    total_prediction INTEGER,
    total_requests INTEGER,
    cpu_usage REAL,
    ram_usage REAL,
    num_containers INTEGER,
    PRIMARY KEY (timestamp, project_id),
    UNIQUE(timestamp, project_id),
    CONSTRAINT fk_project_id 
        FOREIGN KEY (project_id) REFERENCES projects(id)
        ON DELETE CASCADE
);

-- Create version table
DROP TABLE IF EXISTS versions CASCADE;

CREATE TABLE versions (
  project_id INTEGER NOT NULL,
  version_number INTEGER NOT NULL,
  description TEXT DEFAULT NULL,
  created_time timestamp without time zone DEFAULT (now() at time zone 'utc'),
  last_updated timestamp without time zone Default (now() at time zone 'utc'),
  traffic_percentage REAL DEFAULT 0,
  uploaded BOOLEAN DEFAULT false,
  test_status VARCHAR(80) DEFAULT 'not passed',
  active_status VARCHAR(80) DEFAULT 'Down',
  deploy_status VARCHAR(80) DEFAULT 'not deployed',
  deploy_test INTEGER DEFAULT 0,
  deployed_before BOOLEAN DEFAULT false,
  deployment_environment VARCHAR(120) DEFAULT NULL,
  approval_status VARCHAR(120) DEFAULT 'not approved',
  pending_approval BOOLEAN DEFAULT false,
  who_deploy VARCHAR(120) DEFAULT NULL,
  logloss REAL,
  auc_roc REAL,
  ks_score REAL,
  gini_norm REAL,
  rate_top10 REAL,
  PRIMARY KEY (project_id, version_number),
  FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
);

-- Create auto last_updated function
CREATE OR REPLACE FUNCTION trigger_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.last_updated = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_update_timestamp
BEFORE UPDATE ON versions
FOR EACH ROW
EXECUTE FUNCTION trigger_update_timestamp();


-- Create request table
DROP TABLE IF EXISTS requests CASCADE;

CREATE TABLE requests (
    request_id SERIAL NOT NULL UNIQUE,
    project_id INTEGER NOT NULL,
    version_number FLOAT NOT NULL,
    created_time timestamp without time zone DEFAULT (now() at time zone 'utc'),
    submit_request_comment TEXT DEFAULT NULL,
    handle_request_comment TEXT DEFAULT NULL,
    who_sumbit_request VARCHAR(120),
    who_handle_request VARCHAR(120),
    request_status VARCHAR(120),

    PRIMARY KEY (request_id, project_id, version_number)
);