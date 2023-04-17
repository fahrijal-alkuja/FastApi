from sqlalchemy.orm import Session
from typing import List
from config.condb import get_db
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException
from models.model import Problem
from schemas.problems import ProblemSchema, AddProblem, UpdateProblem, GetProblem
from config.auth_bearer import get_current_active_user
problem = APIRouter()


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
