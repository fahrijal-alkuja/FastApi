from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from models.users import Users
from schemas.users import UserSchema, UserAddSChema
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from config.condb import get_db
from passlib.context import CryptContext

user = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@user.get("/users", tags=["Users"], response_model=List[UserSchema])
def get_users(db: Session = Depends(get_db)):
    return db.query(Users).all()


@user.get("/users/{user_id}", tags=["Users"], response_model=UserSchema)
def get_user_byid(user_id: int, db: Session = Depends(get_db)):
    dataUser = db.query(Users).filter(Users.id == user_id).first()
    if not dataUser:
        raise HTTPException(status_code=404, detail="User not found")
    return dataUser


@user.post("/users", tags=["Users"], response_model=UserSchema)
def add_users(user: UserAddSChema, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    data = Users(name=user.name, email=user.email,
                 password=hashed_password, rule=user.rule)
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


@user.put("/users/{user_id}", tags=["Users"], response_model=UserSchema)
def update_users(user_id: int, user: UserSchema, db: Session = Depends(get_db)):
    try:
        data = db.query(Users).filter(Users.id == user_id).first()
        data.name = user.name
        data.email = user.email
        data.rule = user.rule
        db.add(data)
        db.commit()
        return data
    except:
        return HTTPException(status_code=404, detail="User tidak ada")


@user.delete("/users/{user_id}", tags=["Users"], response_class=JSONResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        data = db.query(Users).filter(Users.id == user_id).first()
        db.delete(data)
        db.commit()
        return {f"User Dengan Id {user_id} Berhasil Dihapus": True}
    except:
        return HTTPException(status_code=404, detail="User tidak ada")
