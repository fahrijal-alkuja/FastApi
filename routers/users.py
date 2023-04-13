from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from models.model import Users, Prodi
from schemas.users import UserGetSchema, UserSchema, UserAddSChema, UserUpdate
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from config.condb import get_db
from passlib.context import CryptContext


from config.auth_bearer import get_current_active_user

user = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@user.get("/api/users", tags=["Users"], response_model=List[UserGetSchema])
async def get_users(db: Session = Depends(get_db), isAktiv=Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")
    return db.query(Users).all()


@user.get("/api/users/{user_id}", tags=["Users"], response_model=UserGetSchema)
async def get_user_byid(user_id: int, db: Session = Depends(get_db), isAktiv=Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")
    dataUser = db.query(Users).filter(Users.id == user_id).first()
    if not dataUser:
        raise HTTPException(status_code=404, detail="User not found")
    return dataUser


def is_email_exist(email: str, db: Session):
    return db.query(Users).filter(Users.email == email).first() is not None


@user.post("/api/users", tags=["Users"], response_model=UserGetSchema)
async def add_users(user: UserAddSChema, db: Session = Depends(get_db), isAktiv=Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")
    if is_email_exist(user.email, db):
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    hashed_password = pwd_context.hash(user.password)
    data = Users(prodi_id=user.prodi_id, name=user.name, email=user.email,
                 password=hashed_password, rule=user.rule)
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


@user.put("/api/users/{user_id}", tags=["Users"], response_model=UserUpdate)
async def update_users(user_id: int, user: UserSchema, db: Session = Depends(get_db), isAktiv=Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat menghapus user, akun tidak aktif")
    try:
        data = db.query(Users).filter(Users.id == user_id).first()
        data.name = user.name
        data.prodi_id = user.prodi_id
        data.email = user.email
        data.rule = user.rule
        db.add(data)
        db.commit()
        return data
    except:
        return HTTPException(status_code=404, detail="User tidak ada")


@user.delete("/api/users/{user_id}", tags=["Users"], response_class=JSONResponse)
async def delete_user(user_id: int, db: Session = Depends(get_db), isAktiv: bool = Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat menghapus user, akun tidak aktif")
    try:
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404, detail=f"User dengan id {user_id} tidak ditemukan")
        db.delete(user)
        db.commit()
        return {f"User dengan Id {user_id} berhasil dihapus": True}
    except:
        raise HTTPException(
            status_code=500, detail="Terjadi kesalahan saat menghapus user")
