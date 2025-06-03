from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InvoiceBase(BaseModel):
    invoice_number: str
    amount: float
    vendor: str
    description: str
    due_date: datetime
    status: str

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
