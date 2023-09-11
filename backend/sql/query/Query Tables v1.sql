SELECT * 
FROM users;

SELECT * 
FROM projects;

SELECT * 
FROM data_drift
ORDER BY timestamp DESC;

SELECT * 
FROM performance
ORDER BY timestamp DESC;

SELECT * 
FROM versions
ORDER BY (project_id, version_number);