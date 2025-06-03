from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True)
    amount = Column(Float)
    vendor = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    status = Column(String)  # pending, paid, overdue
