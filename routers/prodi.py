from typing import List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from models.prodi import Prodi
from schemas.prodis import ProdiGetSchema, ProdiSchema, ProdiUpdate
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config.condb import get_db

from config.auth_bearer import get_current_active_user

prodi = APIRouter()


@prodi.get("/api/prodi", tags=["Prodi"], response_model=List[ProdiGetSchema])
async def get_prodi(db: Session = Depends(get_db), IsAktiv=Depends(get_current_active_user)):
    if not IsAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")
    return db.query(Prodi).all()


@prodi.get("/api/prodi/{code_prodi}", tags=["Prodi"], response_model=ProdiGetSchema)
async def get_prodi_byid(code_prodi: int, db: Session = Depends(get_db), isAktiv=Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")
    dataProdi = db.query(Prodi).filter(Prodi.code_prodi == code_prodi).first()
    if not dataProdi:
        raise HTTPException(status_code=404, detail="Prodi not found")
    return dataProdi


@prodi.post("/api/prodi", tags=["Prodi"], response_model=ProdiGetSchema)
async def add_prodi(prodi: ProdiSchema, db: Session = Depends(get_db), isAktiv=Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")

    data = Prodi(code_prodi=prodi.code_prodi, nama_prodi=prodi.nama_prodi)
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


@prodi.put("/api/prodi/{id_prodi}", tags=["Prodi"], response_model=ProdiUpdate)
async def update_prodi(id_prodi: int, prodi: ProdiSchema, db: Session = Depends(get_db), isAktiv=Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Prodi Tidak Bisa Diupdate, akun tidak aktif")
    try:
        data = db.query(Prodi).filter(Prodi.id == id_prodi).first()
        data.code_prodi = prodi.code_prodi
        data.nama_prodi = prodi.nama_prodi

        db.add(data)
        db.commit()
        db.refresh(data)
        return data
    except:
        return HTTPException(status_code=404, detail="Prodi tidak ada")


@prodi.delete("/api/prodi/{id}", tags=["Prodi"], response_class=JSONResponse)
async def delete_user(id: int, db: Session = Depends(get_db), isAktiv: bool = Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat menghapus user, akun tidak aktif")
    try:
        prodi = db.query(Prodi).filter(Prodi.id == id).first()
        if not prodi:
            raise HTTPException(
                status_code=404, detail=f"User dengan id {id} tidak ditemukan")
        db.delete(prodi)
        db.commit()
        return {f"Prodi dengan Id {id} berhasil dihapus": True}
    except:
        raise HTTPException(
            status_code=500, detail="Terjadi kesalahan saat menghapus user")
