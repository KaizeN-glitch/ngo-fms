# auth_service/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud, models, schemas, dependencies
from database import engine

# Create all tables if they don’t exist yet (roles + users)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")


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

    # 2. Create the user (ValueError if role_name doesn’t exist)
    try:
        user = crud.create_user(db, user_in.username, user_in.password, user_in.role_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3. Issue JWT with "sub" = username and "role_name" = user.role.name
    access_token = dependencies.create_access_token(
        data={"sub": user.username, "role_name": user.role.name}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: schemas.UserCreate,  # role_name in payload is ignored here
    db: Session = Depends(dependencies.get_db),
):
    """
    Login endpoint. Expects payload:
      {
        "username": "<string>",
        "password": "<string>",
        "role_name": "<ignored on login>"
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

    # Issue a new JWT, embedding the user’s role_name
    access_token = dependencies.create_access_token(
        data={"sub": user.username, "role_name": user.role.name}
    )
    return {"access_token": access_token, "token_type": "bearer"}
