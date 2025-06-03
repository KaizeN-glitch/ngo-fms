from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth_service.app.database import get_db
from app import schemas, models, auth
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Check if role exists
    db_role = db.query(models.Role).filter(models.Role.name == user.role_name).first()
    if not db_role:
        raise HTTPException(status_code=400, detail="Role does not exist")

    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        password_hash=hashed_password,
        role_id=db_role.role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create access token
    access_token = auth.create_access_token(data={"sub": db_user.username, "role_name": db_role.name})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    # Find user
    user = db.query(models.User).filter(models.User.username == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not auth.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Get role name
    role = db.query(models.Role).filter(models.Role.role_id == user.role_id).first()
    role_name = role.name if role else None

    # Create access token
    access_token = auth.create_access_token(data={"sub": user.username, "role_name": role_name})
    return {"access_token": access_token, "token_type": "bearer"}
