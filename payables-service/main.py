from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models, schemas
from sqlalchemy.exc import IntegrityError
import requests
from typing import Union

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

@app.post(
    "/invoices",
    response_model=Union[schemas.InvoiceResponse, schemas.InvoiceErrorResponse],
    status_code=201
)
def create_invoice(invoice: schemas.InvoiceCreate, db: Session = Depends(get_db)):
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
        # Make API call to Ledger Service
        response = requests.post(LEDGER_SERVICE_URL, json=journal_entry)
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
