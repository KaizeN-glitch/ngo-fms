from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

DATABASE_URL = "postgresql://ledger_user:ledger_pass@ledger_db:5432/ledger_db"

max_retries = 10
retry_interval = 5  # seconds

for i in range(max_retries):
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        conn.close()
        print("Database connection successful")
        break
    except OperationalError as e:
        print(f"Database connection failed ({i+1}/{max_retries}): {e}")
        time.sleep(retry_interval)
else:
    raise Exception("Database connection failed after max retries.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
