from pydantic import BaseModel, EmailStr
from datetime import date
from enum import Enum

class InvoiceStatusEnum(str, Enum):
    pending = "Pending Posting"
    posted = "Posted"

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
    created_by: str
    status: InvoiceStatusEnum = InvoiceStatusEnum.pending
    expense_account: str
    payable_account: str

class InvoiceResponse(InvoiceCreate):
    class Config:
        orm_mode = True

class InvoiceErrorResponse(BaseModel):
    invoice_id: str
    message: str
    error: str
