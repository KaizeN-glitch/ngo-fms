from fastapi import APIRouter, Depends, HTTPException
from app.utils import validate_token
import httpx
import os

router = APIRouter()

# Provide default values for local development
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
PAYABLES_SERVICE_URL = os.getenv("PAYABLES_SERVICE_URL", "http://localhost:8002")

@router.post("/auth/register")
async def register(user_data: dict):
    if not AUTH_SERVICE_URL:
        raise HTTPException(status_code=500, detail="AUTH_SERVICE_URL not set")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{AUTH_SERVICE_URL}/auth/register", json=user_data)
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Auth service unreachable: {e}")

@router.post("/auth/login")
async def login(credentials: dict):
    if not AUTH_SERVICE_URL:
        raise HTTPException(status_code=500, detail="AUTH_SERVICE_URL not set")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{AUTH_SERVICE_URL}/auth/login", json=credentials)
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Auth service unreachable: {e}")

@router.get("/payables/invoices")
async def get_invoices(token: str = Depends(validate_token)):
    if not PAYABLES_SERVICE_URL:
        raise HTTPException(status_code=500, detail="PAYABLES_SERVICE_URL not set")
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = await client.get(f"{PAYABLES_SERVICE_URL}/invoices", headers=headers)
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Payables service unreachable: {e}")

@router.post("/payables/invoices")
async def create_invoice(invoice_data: dict, token: str = Depends(validate_token)):
    if not PAYABLES_SERVICE_URL:
        raise HTTPException(status_code=500, detail="PAYABLES_SERVICE_URL not set")
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = await client.post(f"{PAYABLES_SERVICE_URL}/invoices", json=invoice_data, headers=headers)
            response.raise_for_status() # Raise an exception for bad status codes
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Payables service unreachable: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())

@router.get("/payables/invoices/{invoice_id}")
async def get_invoice(invoice_id: str, token: str = Depends(validate_token)):
    if not PAYABLES_SERVICE_URL:
        raise HTTPException(status_code=500, detail="PAYABLES_SERVICE_URL not set")
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = await client.get(f"{PAYABLES_SERVICE_URL}/invoices/{invoice_id}", headers=headers)
            response.raise_for_status() # Raise an exception for bad status codes
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Payables service unreachable: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
