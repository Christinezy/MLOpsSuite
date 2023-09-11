from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

ENV = os.environ.get('ENV')

# Postgres Database
if ENV == "DEV":
    engine = create_engine('postgresql://user:password@localhost:5455/MLOps_Suite')
else:
    engine = create_engine('postgresql://user:password@db:5455/MLOps_Suite')

DB_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()