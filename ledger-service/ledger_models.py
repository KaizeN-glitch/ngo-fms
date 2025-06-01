from sqlalchemy import Column, Integer, String, Float, Enum
from ledger_db import Base

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    account = Column(String, nullable=False)
    type = Column(Enum("debit", "credit", name="entry_type"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
