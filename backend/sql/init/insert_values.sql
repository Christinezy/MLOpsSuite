-- Insert values into users
INSERT INTO users
	(firstname, lastname, email, salt, password, role, date_created, github_id, github_credentials)
	VALUES
    ('Chad', 'Richman', 'chad@example.com', 'a67afa5b26eca0a9', 'pbkdf2:sha256:260000$947yJFGdC3eZ336t$db70ec5df6a68e825898e4a6894c9b1d88101a9ab19caf9692ef2114537b179d', '0', '2023-03-13 20:46:43.90241', 'sidharthgohil', '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'),
    ('Grace', 'Tan', 'grace@example.com', '73a188834b4c81b2', 'pbkdf2:sha256:260000$cNK3ISYTp3K2dEO1$daa09bab36ad366f8bf1c468bb3f851875205de21ec406527ec073c998e37635', '1', '2023-03-13 20:46:43.90241', 'sidharthgohil', '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'),
	('Emily', 'Ang', 'emily@example.com', '6240a232521611d0', 'pbkdf2:sha256:260000$LdWINhPBouzCt6PJ$8ee93b1ed06a390fd0eec6f246ebca73a386d7959a7c950afab51951e9eaf72f', '2', '2023-03-13 20:46:43.90241', 'sidharthgohil', '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'),
	('Jack', 'Pot', 'jack@example.com', '6240a232521611d0', 'pbkdf2:sha256:260000$LdWINhPBouzCt6PJ$8ee93b1ed06a390fd0eec6f246ebca73a386d7959a7c950afab51951e9eaf72f', '3', '2023-03-13 20:46:43.90241', 'sidharthgohil', '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')
	
	ON CONFLICT (email) DO UPDATE
	SET
		firstname = excluded.firstname,
		lastname = excluded.lastname,
		email = excluded.email,
		salt = excluded.salt,
		password = excluded.password,
		role = excluded.role,
		date_created = excluded.date_created,
		github_id = excluded.github_id,
		github_credentials = excluded.github_credentials
;



-- Insert values into projects
INSERT INTO projects
	(id, name, status, deployment, build_environment, total_prediction, total_requests, cpu_usage, ram_usage, num_containers, cpu_threshold, owner, model_age, date_created, url, min_num_nodes, max_num_nodes, desired_num_nodes)
	VALUES
    (1, 'Fraud Detection Model', 'Live', 'blue', 'Python', 900, 1000, 80.0, 10.0, 2, 90.0, 3, '10', '2023-03-03 20:46:43.90241', 'http://localhost/project1', 1, 3, 1),
    (2, 'Loan Prediction Model', 'Down', 'green', 'Python', 900, 1000, 80.0, 10.0, 2, 90.0, 3, '10', '2023-03-03 20:46:43.90241', 'http://localhost/project2', 1, 3, 1)
	
	ON CONFLICT (id) DO UPDATE
	SET
		name = excluded.name,
		status = excluded.status,
		deployment = excluded.deployment,
		build_environment = excluded.build_environment,
		total_prediction = excluded.total_prediction,
		total_requests = excluded.total_requests,
		cpu_usage = excluded.cpu_usage,
		ram_usage = excluded.ram_usage,
		num_containers = excluded.num_containers,
		cpu_threshold = excluded.cpu_threshold,
-- 		owner = excluded.owner,
		model_age = excluded.model_age,
		date_created = excluded.date_created
;



-- Insert values into performance
INSERT INTO performance
	(timestamp, project_id, total_prediction, total_requests, cpu_usage, ram_usage, num_containers)
	VALUES
	('2023-03-23 15:03:23.61539', 1, 900, 1000, 80.0, 10.0, 2),
	('2023-03-23 15:04:23.61539', 1, 900, 1000, 80.0, 10.0, 2),
	('2023-03-23 15:05:23.61539', 1, 900, 1000, 80.0, 10.0, 2),
	('2023-03-23 15:06:23.61539', 1, 900, 1000, 80.0, 10.0, 2),
	('2023-03-23 15:07:23.61539', 1, 900, 1000, 80.0, 10.0, 2),
	('2023-03-23 15:08:23.61539', 1, 900, 1000, 80.0, 10.0, 2),
	('2023-03-23 15:09:23.61539', 2, 80, 110, 30.0, 3.0, 4),
	('2023-03-23 15:10:23.61539', 2, 80, 110, 30.0, 3.0, 4),
	('2023-03-23 15:11:23.61539', 2, 80, 110, 30.0, 3.0, 4),
	('2023-03-23 15:12:23.61539', 2, 80, 110, 30.0, 3.0, 4),
	('2023-03-23 15:13:23.61539', 2, 80, 110, 30.0, 3.0, 4),
	('2023-03-23 15:14:23.61539', 2, 80, 110, 30.0, 3.0, 4)
	
	ON CONFLICT (timestamp, project_id) DO UPDATE
	SET
		timestamp = excluded.timestamp,
		total_prediction = excluded.total_prediction, 
		total_requests = excluded.total_requests, 
		cpu_usage = excluded.cpu_usage, 
		ram_usage = excluded.ram_usage, 
		num_containers = excluded.num_containers
;



-- Insert values into data_drift
INSERT INTO data_drift
	(timestamp, project_id, logloss, auc_roc, ks_score, gini_norm, rate_top10)
	VALUES
    ('2023-03-23 15:03:23.61539', 1, 0.627, 0.710, 0.34, 0.454, 0.6666),
	('2023-03-23 15:03:23.61539', 2, 0.7269472, 0.79268295, 0.7098284, 0.74897116, 0.1),
	('2023-03-23 15:04:23.61539', 1, 0.627, 0.710, 0.34, 0.454, 0.6666),
	('2023-03-23 15:05:23.61539', 1, 0.627, 0.710, 0.34, 0.454, 0.6666),
	('2023-03-23 15:06:23.61539', 1, 0.627, 0.710, 0.34, 0.454, 0.6666),
	('2023-03-23 15:07:23.61539', 1, 0.627, 0.710, 0.34, 0.454, 0.6666),
	('2023-03-23 15:08:23.61539', 1, 0.627, 0.710, 0.34, 0.454, 0.6666),
	('2023-03-23 15:09:23.61539', 1, 0.6314, 0.7088, 0.32978, 0.41698, 0.6598),
	('2023-03-23 15:10:23.61539', 1, 0.6314, 0.7088, 0.32978, 0.41698, 0.6598),
	('2023-03-23 15:11:23.61539', 1, 0.6314, 0.7088, 0.32978, 0.41698, 0.6598),
	('2023-03-23 15:12:23.61539', 1, 0.6314, 0.7088, 0.32978, 0.41698, 0.6598),
	('2023-03-23 15:13:23.61539', 1, 0.6314, 0.7088, 0.32978, 0.41698, 0.6598),
	('2023-03-23 15:14:23.61539', 1, 0.6314, 0.7088, 0.32978, 0.41698, 0.6598)
	
	ON CONFLICT (timestamp, project_id) DO UPDATE
	SET
		timestamp = excluded.timestamp,
	    project_id = excluded.project_id,
			logloss = excluded.logloss,
			auc_roc = excluded.auc_roc,
			ks_score = excluded.ks_score,
			gini_norm = excluded.gini_norm,
			rate_top10 = excluded.rate_top10
;




-- Insert values into versions
INSERT INTO versions
	(project_id, version_number, description, created_time, last_updated, traffic_percentage, uploaded, test_status, active_status, 
	deploy_status, deploy_test, deployed_before, deployment_environment, approval_status, pending_approval, who_deploy, 
	logloss, auc_roc, ks_score, gini_norm, rate_top10)
VALUES
		(1, 1, 'This model predicts the likelihood of a loan application being approved based on various features such as the applicants credit score, income, employment status, loan amount, and loan term. It uses a binary classification algorithm to predict whether a loan application will be approved or not.', '2023-03-03 20:46:43.90241', '2023-03-03 20:46:43.90241', 100, true, 'test passed', 'Active', 'deployed', 5, true, 'dev', 'approved', false, 'chad@example.com', 0.6314, 0.7088, 0.32978, 0.41698, 0.6598),
		(2, 1, 'This model is designed to detect fraudulent transactions in financial transactions data. It uses a combination of supervised and unsupervised learning techniques to identify patterns and anomalies in the data.', '2023-03-03 20:46:43.90241', '2023-03-03 20:46:43.90241', 0, true, 'test passed', 'Down', 'not deployed', 0, false, '', 'pending approval', true, '', 0.6314, 0.7088, 0.32978, 0.41698, 0.6598),
		(2, 2, 'This model utilizes a deep learning algorithm to detect fraudulent transactions in real-time. It is trained on large-scale transaction data and is able to automatically learn complex patterns and relationships in the data.', '2023-03-04 09:46:43.90241', '2023-03-04 10:46:43.90241', 0, true, 'test passed', 'Down', 'not deployed', 0, false, '', 'pending approval', true, '', 0.63998, 0.7625368, 0.420624, 0.5250736, 0.7081468),
		(1, 2, 'This model predicts the likelihood of default on a loan application based on various features such as the applicants credit score, income, employment status, loan amount, and loan term. It uses a binary classification algorithm to predict whether a loan application will be classified as high-risk or low-risk.', '2023-03-20 20:46:43.90241', '2023-03-20 20:46:43.90241', 0, true, 'test passed', 'Down', 'not deployed', 0, false, '', 'approved', false, '', 0.6231, 0.727663, 0.34128695, 0.45476479, 0.6660698),
		(1, 3, 'some test model', '2023-03-23 20:46:43.90241', '2023-03-23 20:46:43.90241', 0, true, 'not passed', 'Down', 'not deployed', 0, false, '', 'not approved', false, '', 0.61046, 0.74058, 0.371394562, 0.48047, 0.677708),
		(1, 4, 'some test model', '2023-03-24 20:46:43.90241', '2023-03-24 20:46:43.90241', 0, false, 'not passed', 'Down', 'not deployed', 0, false, '', 'not approved', false, '', 0.63998, 0.7625368, 0.420624, 0.5250736, 0.7081468)

ON CONFLICT (project_id, version_number) DO UPDATE
SET
		description = excluded.description,
		created_time = excluded.created_time,
		traffic_percentage = excluded.traffic_percentage,
		uploaded = excluded.uploaded,
		test_status = excluded.test_status,
		active_status = excluded.active_status,
		deploy_test = excluded.deploy_test,
		deploy_status = excluded.deploy_status,
		deployed_before = excluded.deployed_before,
		deployment_environment = excluded.deployment_environment,
		approval_status = excluded.approval_status,
		pending_approval = excluded.pending_approval,
		who_deploy = excluded.who_deploy,
		logloss = excluded.logloss,
		auc_roc = excluded.auc_roc,
    ks_score = excluded.ks_score,
		gini_norm = excluded.gini_norm,
		rate_top10 = excluded.rate_top10
;

-- Insert values into requests
INSERT INTO requests
	(project_id, version_number, created_time, submit_request_comment, handle_request_comment, who_sumbit_request, who_handle_request, request_status)
	VALUES
    (1, 1, '2023-03-03 20:46:43.90241', 'The model performed exceptionally well on all of 5 metrics', 'Looks good to me', 'grace@example.com', 'chad@example.com', 'approved'),
		(1, 2, '2023-03-25 20:46:43.90241', 'Higher score in auc-roc, ks score and gini norm', 'Looks good to me', 'grace@example.com', 'chad@example.com', 'approved'),
		(2, 2, '2023-03-05 20:46:43.90241', 'All the metrics shows better score than the previous version', '', 'grace@example.com', 'chad@example.com', 'pending approval'),
		(2, 1, '2023-03-04 20:46:43.90241', 'New model created, test result is quite good', '', 'grace@example.com', 'chad@example.com', 'pending approval')
	
	ON CONFLICT (request_id, project_id,version_number) DO UPDATE
	SET
	    created_time = excluded.created_time,
      submit_request_comment = excluded.submit_request_comment,
      handle_request_comment = excluded.handle_request_comment,
      who_sumbit_request = excluded.who_sumbit_request,
      who_handle_request = excluded.who_handle_request,
      request_status = excluded.request_status
;