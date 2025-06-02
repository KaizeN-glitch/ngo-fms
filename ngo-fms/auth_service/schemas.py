# auth_service/schemas.py

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    role_name: str   # e.g. "Accountant", must already exist in roles table

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    role_name: str | None = None
