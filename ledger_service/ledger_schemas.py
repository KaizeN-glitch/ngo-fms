from pydantic import BaseModel
from typing import List, Literal, Optional

class Entry(BaseModel):
    account: str
    type: Literal["debit", "credit"]
    amount: float
    description: str
    project_id: str = None

class JournalEntryRequest(BaseModel):
    entries: List[Entry]

class JournalEntryResponse(BaseModel):
    status: str
    message: str

class EntryOut(BaseModel):
    id: int
    account: str
    type: Literal["debit", "credit"]
    amount: float
    description: str
    project_id: str = None

    class Config:
        orm_mode = True
