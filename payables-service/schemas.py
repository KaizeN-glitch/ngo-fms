from pydantic import BaseModel, EmailStr
from datetime import date
from enum import Enum

# Enum for invoice status
class InvoiceStatusEnum(str, Enum):
    pending = "Pending Posting"
    posted = "Posted"

# Input schema for creating an invoice (from user input)
class InvoiceCreate(BaseModel):
    invoice_id: str
    vendor_name: str
    vendor_email: EmailStr
    vendor_number: str
    invoice_date: date
    due_date: date
    amount: float
    payment_method: str
    payment_status: str
    expense_account: str
    payable_account: str

# Response schema including extra fields injected by backend
class InvoiceResponse(BaseModel):
    invoice_id: str
    vendor_name: str
    vendor_email: EmailStr
    vendor_number: str
    invoice_date: date
    due_date: date
    amount: float
    payment_method: str
    payment_status: str
    created_by: str
    status: InvoiceStatusEnum
    expense_account: str
    payable_account: str

    class Config:
        orm_mode = True

# Error response schema
class InvoiceErrorResponse(BaseModel):
    invoice_id: str
    message: str
    error: str
