from fastapi import FastAPI, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from ledger_models import Base, LedgerEntry
from ledger_schemas import JournalEntryRequest, JournalEntryResponse
from ledger_db import engine, get_db
from typing import List, Optional
from ledger_schemas import EntryOut
import jwt
from datetime import datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# JWT Configuration from environment variables
SERVICE_SECRET = os.getenv("SERVICE_SECRET", "your-service-secret-here")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

security = HTTPBearer()

app = FastAPI()

Base.metadata.create_all(bind=engine)

async def verify_service_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SERVICE_SECRET, algorithms=[ALGORITHM])
        if datetime.fromtimestamp(payload['exp']) < datetime.now():
            raise HTTPException(status_code=401, detail="Service token has expired")
        if not payload.get('service') and payload.get('role_name') not in ["Admin", "Accountant", "User"]:
            raise HTTPException(status_code=403, detail="Unauthorized service or user")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid service token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/api/v1/ledger/journal-entries", response_model=JournalEntryResponse, status_code=201)
async def create_journal_entry(
    entry: JournalEntryRequest,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_service_token)
):
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
async def get_journal_entries(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(verify_service_token)
):
    entries = db.query(LedgerEntry).all()
    return entries