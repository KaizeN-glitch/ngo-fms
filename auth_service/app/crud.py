from app import models
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import secrets
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_role_by_name(db: Session, name: str) -> models.Role | None:
    return db.query(models.Role).filter(models.Role.name == name).first()

def create_role(db: Session, name: str) -> models.Role:
    """
    Helper if you want to prepopulate roles programmatically.
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

def generate_password_reset_token(db: Session, username: str, expires_in_minutes: int = 30) -> str:
    """
    Generates a password reset token for the user and stores it in the database with an expiry time.
    """
    user = get_user_by_username(db, username)
    if not user:
        raise ValueError("User does not exist.")
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    user.reset_token = token
    user.reset_token_expiry = expiry
    db.commit()
    return token

def reset_password_with_token(db: Session, token: str, new_password: str) -> bool:
    """
    Resets the user's password if the token is valid and not expired.
    """
    user = db.query(models.User).filter(models.User.reset_token == token).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        return False
    user.password_hash = pwd_context.hash(new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()
    return True
