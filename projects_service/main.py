from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Project, Base
from schemas import ProjectCreate, ProjectOut
from database import engine, SessionLocal
import requests
from typing import List
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

Base.metadata.create_all(bind=engine)
app = FastAPI()

load_dotenv()
SERVICE_SECRET = os.getenv("SERVICE_SECRET", "shared-service-secret")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_service_token():
    return jwt.encode(
        {
            "service": "projects-service",
            "exp": datetime.utcnow() + timedelta(minutes=5)
        },
        SERVICE_SECRET,
        algorithm=ALGORITHM
    )

@app.post("/projects", response_model=ProjectOut)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/{project_id}/transactions")
async def get_project_transactions(project_id: str):
    # Proxy to Ledger Service
    LEDGER_SERVICE_URL = "http://ledger_service:8000/api/v1/ledger/transactions"
    headers = {
        "Authorization": f"Bearer {get_service_token()}"
    }
    try:
        response = requests.get(
            LEDGER_SERVICE_URL,
            params={"project_id": project_id},
            headers=headers,
            timeout=5  # 5 seconds timeout
        )
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        return response.json()
    except requests.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Ledger Service timeout"
        )
    except requests.ConnectionError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to Ledger Service"
        )
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Project transactions not found"
            )
        raise HTTPException(
            status_code=502,
            detail=f"Ledger Service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 