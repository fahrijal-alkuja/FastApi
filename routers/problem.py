from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from config.condb import get_db
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException
from models.model import Problem
from schemas.problems import ProblemSchema, AddProblem, UpdateProblem, GetProblem
from config.auth_bearer import get_current_active_user
problem = APIRouter()


def hitung_analisis_keterangan(db: Session):
    # Lakukan query untuk menghitung jumlah data untuk setiap keterangan
    results = db.query(Problem.keterangan, func.count(Problem.keterangan).label('jumlah')) \
                .group_by(Problem.keterangan).all()

    # Urutkan hasil berdasarkan jumlah dalam urutan menurun
    results_sorted = sorted(results, key=lambda x: x.jumlah, reverse=True)

    # Hitung total jumlah data
    total = sum(result.jumlah for result in results_sorted)

    # Hitung persentase dari keterangan yang paling banyak muncul
    persentase = (results_sorted[0].jumlah /
                  total) * 100 if results_sorted else 0

    # Ambil solusi terbaik dari keterangan terbanyak
    solusi_terbanyak = db.query(Problem).filter(
        Problem.keterangan == results_sorted[0].keterangan).first()

    return {"Masalah": results_sorted[0].keterangan if results_sorted else None, "persentase": persentase, "Rekomendasi_solusi": solusi_terbanyak.solusi if solusi_terbanyak else None}


@problem.get("/api/analisis-keterangan", tags=["Problem"])
async def analisis_keterangan(db: Session = Depends(get_db), isAktiv=Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")

    # Hitung analisis keterangan
    analisis_keterangan = hitung_analisis_keterangan(db)

    return analisis_keterangan


@problem.get("/api/problem", tags=["Problem"], response_model=List[GetProblem])
async def get_problems(db: Session = Depends(get_db), isAktiv=Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")
    return db.query(Problem).all()


@problem.post("/api/problem", tags=["Problem"], response_model=AddProblem)
async def add_users(problem: AddProblem, db: Session = Depends(get_db), isAktiv=Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")

    data = Problem(**problem.dict())
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


@problem.put("/api/problem/{id}", tags=["Problem"], response_model=UpdateProblem)
async def update_problem(id: int, problem: UpdateProblem, db: Session = Depends(get_db), IsAktiv=Depends(get_current_active_user)):
    if not IsAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")

    data = db.query(Problem).filter(Problem.id == id)

    if not data.first():
        raise HTTPException(
            status_code=404, detail="Data tidak ditemukan")

    data.update(problem.dict(exclude_unset=True))
    db.commit()
    db.refresh(data.first())

    return data.first()


@problem.delete("/api/problem/{id}", tags=["Problem"], response_class=JSONResponse)
async def delete_problem(id: int, db: Session = Depends(get_db), isAktiv: bool = Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat menghapus user, akun tidak aktif")
    try:
        data = db.query(Problem).filter(Problem.id == id).first()
        if not data:
            raise HTTPException(
                status_code=404, detail=f"Data dengan id {id} tidak ditemukan")
        db.delete(data)
        db.commit()
        return {f"Data dengan Id {id} berhasil dihapus": True}
    except:
        raise HTTPException(
            status_code=500, detail="Terjadi kesalahan saat menghapus user")
