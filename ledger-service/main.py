from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from ledger_models import Base, LedgerEntry
from ledger_schemas import JournalEntryRequest, JournalEntryResponse
from ledger_db import engine, get_db
from typing import List
from ledger_schemas import EntryOut
app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post("/api/v1/ledger/journal-entries", response_model=JournalEntryResponse, status_code=201)
def create_journal_entry(entry: JournalEntryRequest, db: Session = Depends(get_db)):
    if len(entry.entries) != 2:
        raise HTTPException(status_code=400, detail="Must provide one debit and one credit entry")

    debit = next((e for e in entry.entries if e.type == "debit"), None)
    credit = next((e for e in entry.entries if e.type == "credit"), None)

    if not debit or not credit:
        raise HTTPException(status_code=400, detail="Both debit and credit required")

    if debit.amount != credit.amount:
        raise HTTPException(status_code=400, detail="Debit and credit amounts must match")

    db_debit = LedgerEntry(account=debit.account, type="debit", amount=debit.amount, description=debit.description)
    db_credit = LedgerEntry(account=credit.account, type="credit", amount=credit.amount, description=credit.description)

    db.add_all([db_debit, db_credit])
    db.commit()

    return {"status": "success", "message": "Journal entry posted"}

@app.get("/api/v1/ledger/journal-entries", response_model=List[EntryOut])
def get_journal_entries(db: Session = Depends(get_db)):
    entries = db.query(LedgerEntry).all()
    return entries