from fastapi import FastAPI
from app.routes import router
from app.db import engine
from app.models import Base

app = FastAPI(title="Payables Service")

# Create database tables
Base.metadata.create_all(bind=engine)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
