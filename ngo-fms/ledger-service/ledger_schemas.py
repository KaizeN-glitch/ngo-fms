from pydantic import BaseModel
from typing import List, Literal

class Entry(BaseModel):
    account: str
    type: Literal["debit", "credit"]
    amount: float
    description: str

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

    class Config:
        orm_mode = True
