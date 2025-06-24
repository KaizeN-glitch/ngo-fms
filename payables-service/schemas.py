from pydantic import BaseModel, EmailStr
from datetime import date
from enum import Enum
from typing import Optional

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
    project_id: Optional[str] = None
    expense_account_code: Optional[str] = None
    payable_account_code: Optional[str] = None

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
    project_id: Optional[str] = None
    expense_account_code: Optional[str] = None
    payable_account_code: Optional[str] = None

    class Config:
        from_attributes = True

# Error response schema
class InvoiceErrorResponse(BaseModel):
    invoice_id: str
    message: str
    error: str
