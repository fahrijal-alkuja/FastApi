from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from models.model import Users
from config.condb import get_db
from sqlalchemy.orm import Session
from config.auth_handler import SECRET_KEY, check_token_expaid
from config.auth_handler import ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="Bearer")


def get_user(db, email: str):
    return db.query(Users).filter(Users.email == email).first()


# async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")

#         if email is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                 detail="Invalid authentication credentials")

#         if not check_token_expaid(token):
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                 detail="Token has expired")
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail="Invalid authentication credentials")
#     user = get_user(db, email)
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail="Invalid authentication credentials")
#     return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid authentication credentials")

        if not check_token_expaid(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Token has expired")

        user = get_user(db, email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid authentication credentials")
        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")


async def get_current_active_user(current_user: Users = Depends(get_current_user)):
    if not current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
