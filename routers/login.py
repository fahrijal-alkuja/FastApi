from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from sqlalchemy.orm import Session
from config.auth_bearer import get_current_active_user
from config.condb import get_db
from models.users import Users
from schemas.users import UserSchema

from config.auth_handler import authenticate_user, create_access_token
from config.auth_handler import ACCESS_TOKEN_EXPIRE_MINUTES

login = APIRouter()


@login.post("/login", tags=["Users"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@login.get("/me/", tags=["Users"], response_model=UserSchema)
async def read_users_me(current_user: Users = Depends(get_current_active_user)):
    return current_user
