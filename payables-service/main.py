from fastapi import FastAPI, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models, schemas
from sqlalchemy.exc import IntegrityError
import requests
from typing import Union, Optional, List
import jwt
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT Configuration from environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
SERVICE_SECRET = os.getenv("SERVICE_SECRET", "your-service-secret-here")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8000")

security = HTTPBearer()

# URL of Ledger Service (update as per your actual setup)
LEDGER_SERVICE_URL = "http://ledger-service:8000/api/v1/ledger/journal-entries"

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.fromtimestamp(payload['exp']) < datetime.now():
            raise HTTPException(status_code=401, detail="Token has expired")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# Service-to-service authentication
def get_service_token():
    return jwt.encode(
        {
            "service": "payables-service",
            "exp": datetime.utcnow() + timedelta(minutes=5)
        },
        SERVICE_SECRET,
        algorithm=ALGORITHM
    )

@app.post(
    "/invoices",
    response_model=Union[schemas.InvoiceResponse, schemas.InvoiceErrorResponse],
    status_code=201
)
async def create_invoice(
    invoice: schemas.InvoiceCreate,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    if invoice.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    # Set initial status
    invoice_data = invoice.dict()
    invoice_data['status'] = "Pending Posting"

    # Save invoice to database
    db_invoice = models.Invoice(**invoice_data)
    db.add(db_invoice)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invoice ID already exists")
    db.refresh(db_invoice)

    # Construct Journal Entry data
    journal_entry = {
        "entries": [
            {
                "account": invoice.expense_account,
                "type": "debit",
                "amount": invoice.amount,
                "description": f"Invoice {invoice.invoice_id} expense"
            },
            {
                "account": invoice.payable_account,
                "type": "credit",
                "amount": invoice.amount,
                "description": f"Invoice {invoice.invoice_id} payable"
            }
        ]
    }

    try:
        # Make API call to Ledger Service with service token
        headers = {
            "Authorization": f"Bearer {get_service_token()}"
        }
        response = requests.post(LEDGER_SERVICE_URL, json=journal_entry, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        # Do not update status if ledger call fails
        return {
            "invoice_id": db_invoice.invoice_id,
            "message": "Invoice created, but failed to post journal entry.",
            "error": str(e)
        }

    # Ledger succeeded, update invoice status
    db_invoice.status = "Posted"
    db.commit()
    db.refresh(db_invoice)

    return db_invoice

@app.get("/invoices", response_model=List[schemas.InvoiceResponse])
async def get_invoices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """Get all invoices with pagination"""
    invoices = db.query(models.Invoice).offset(skip).limit(limit).all()
    return invoices

@app.get("/invoices/{invoice_id}", response_model=schemas.InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_token)
):
    """Get a specific invoice by ID"""
    invoice = db.query(models.Invoice).filter(models.Invoice.invoice_id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice
