from fastapi import APIRouter, Depends, HTTPException
from app.utils import validate_token
import httpx
import os

router = APIRouter()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
PAYABLES_SERVICE_URL = os.getenv("PAYABLES_SERVICE_URL")

@router.post("/auth/register")
async def register(user_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/register", json=user_data)
        return response.json()

@router.post("/auth/login")
async def login(credentials: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/login", json=credentials)
        return response.json()

@router.get("/payables/invoices")
async def get_invoices(token: str = Depends(validate_token)):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(f"{PAYABLES_SERVICE_URL}/invoices", headers=headers)
        return response.json()
