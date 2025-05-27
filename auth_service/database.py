# auth_service/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Expect DATABASE_URL in the form:
#   postgresql://username:password@host:port/dbname
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:vishalgi8@localhost:5432/fms_db")

# Create SQLAlchemy engine pointing to PostgreSQL
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
