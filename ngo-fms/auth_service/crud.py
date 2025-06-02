# auth_service/crud.py

import models
from sqlalchemy.orm import Session
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_role_by_name(db: Session, name: str) -> models.Role | None:
    return db.query(models.Role).filter(models.Role.name == name).first()

def create_role(db: Session, name: str) -> models.Role:
    """
    Helper if you want to pre‐populate roles programmatically.
    """
    db_role = models.Role(name=name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(
    db: Session,
    username: str,
    plain_password: str,
    role_name: str
) -> models.User:
    # 1. Find the Role row
    role_obj = get_role_by_name(db, role_name)
    if not role_obj:
        raise ValueError(f"Role '{role_name}' does not exist.")

    # 2. Hash the password
    hashed_pw = pwd_context.hash(plain_password)

    # 3. Insert into users
    db_user = models.User(
        username=username,
        password_hash=hashed_pw,
        role_id=role_obj.role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
