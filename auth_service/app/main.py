from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud import get_password_hash

from . import models, schemas, crud, dependencies
from .database import SessionLocal, engine

# Create all tables if they don't exist yet (roles + users)
models.Base.metadata.create_all(bind=engine)

from fastapi import Security
from .dependencies import get_current_user,get_db, create_access_token  # Assuming you have this
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="Auth Service")

@app.put("/users/{username}/role")
def update_user_role(
    username: str,
    new_role: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # ✅ Only Superadmin can change roles
    if current_user.role.name.lower() != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can change roles")

    # 🔍 Check if user exists
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔍 Check if target role exists
    role = db.query(models.Role).filter(models.Role.name == new_role).first()
    if not role:
        raise HTTPException(status_code=404, detail="Target role not found")

    # ✅ Update role
    user.role_id = role.role_id
    db.commit()
    db.refresh(user)

    return {"message": f"User '{username}' updated to role '{new_role}'"}


# Function to create default roles if they don't exist
def create_default_roles():
    db = None
    try:
        db = SessionLocal() # Use the sessionmaker from database.py
        default_roles = ["Volunteer", "Admin", "Superadmin"]
        for role_name in default_roles:
            existing_role = crud.get_role_by_name(db, role_name)
            if not existing_role:
                print(f"Creating default role: {role_name}")
                crud.create_role(db, role_name)
    except Exception as e:
        print(f"Error creating default roles: {e}")
    finally:
        if db:
            db.close()

# Call this function after creating tables
create_default_roles()
def create_superadmin():
    db = SessionLocal()
    try:
        username = "superadmin@gmail.com"
        password = "12345"

        # Ensure Superadmin role exists
        role = crud.get_role_by_name(db, "Superadmin")
        if not role:
            role = crud.create_role(db, "Superadmin")

        # Check if user already exists
        existing = crud.get_user_by_username(db, username)
        if not existing:
            hashed_pw = get_password_hash(password)
            db_user = models.User(username=username, password_hash=hashed_pw, role_id=role.role_id)
            db.add(db_user)
            db.commit()
            print("[✅] Superadmin user created.")
    finally:
        db.close()
create_superadmin()


@app.post("/auth/register", response_model=schemas.Token)
def register_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(dependencies.get_db),
):
    """
    Register a new user. Expects payload:
      {
        "username": "<string>",
        "password": "<string>",
        "role_name": "<existing role name>"
      }
    Returns: { "access_token": "<JWT>", "token_type": "bearer" }
    """
    # 1. Ensure the username is not already taken
    existing = crud.get_user_by_username(db, user_in.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    # 2. Create the user (ValueError if role_name doesn't exist)
    try:
        user = crud.create_user(db, user_in.username, user_in.password, user_in.role_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3. Issue JWT with "sub" = username and "role_name" = user.role.name
    access_token = dependencies.create_access_token(
        data={"sub": user.username, "role_name": user.role.name}
    )
    return {"access_token": access_token, "token_type": "bearer", "role_name": user.role.name}


@app.post("/auth/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: schemas.UserLogin,  # Changed from UserCreate to new UserLogin schema
    db: Session = Depends(dependencies.get_db),
):
    """
    Login endpoint. Expects payload:
      {
        "username": "<string>",
        "password": "<string>"
      }
    Returns: { "access_token": "<JWT>", "token_type": "bearer" }
    """
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not crud.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    role_name = user.role.name
    access_token = dependencies.create_access_token(
        data={"sub": user.username, "role_name": user.role.name}
    )
    return {"access_token": access_token, "token_type": "bearer","role_name": role_name }

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Auth Service",
        version="1.0.0",
        description="Handles user authentication and role management",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"BearerAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi