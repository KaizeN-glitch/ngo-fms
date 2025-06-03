from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, auth
from app.db import get_db

router = APIRouter()

@router.get("/invoices", response_model=List[schemas.Invoice])
def get_invoices(
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.verify_token)
):
    invoices = db.query(models.Invoice).all()
    return invoices

@router.get("/invoices/{invoice_id}", response_model=schemas.Invoice)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.verify_token)
):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.post("/invoices", response_model=schemas.Invoice)
def create_invoice(
    invoice: schemas.InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.verify_token)
):
    db_invoice = models.Invoice(**invoice.dict())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice
