from datetime import date
from difflib import SequenceMatcher
from itertools import combinations
from typing import List, Tuple
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from config.condb import get_db
from models.model import AktivitasMhs
from schemas.am import GetAktivits, UpdateAktivits, AmSchema, Analisis

from config.auth_bearer import get_current_active_user

Aktivitas = APIRouter()


def similarity(a: str, b: str) -> float:
    """Returns the percentage of similarity between two strings."""
    matcher = SequenceMatcher(None, a, b)
    return matcher.ratio() * 100


def get_all_judul(db: Session) -> List[str]:
    """Returns a list of all the 'judul' values from the database."""
    return [row.judul for row in db.query(AktivitasMhs.judul).all()]


def calculate_similarity_matrix(juduls: List[str]) -> List[Tuple[str, str, float]]:
    """Returns a matrix of similarity percentages between all pairs of 'judul' values."""
    return [(a, b, similarity(a, b)) for a, b in combinations(juduls, 2)]


@Aktivitas.get("/api/am", tags=["Aktivitas_mhs"], response_model=List[Analisis])
async def get_aktivitas(db: Session = Depends(get_db), IsAktiv=Depends(get_current_active_user)):
    if not IsAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")
    aktivitas = db.query(AktivitasMhs).all()
    all_juduls = get_all_judul(db)
    similarity_matrix = calculate_similarity_matrix(all_juduls)
    for am in aktivitas:
        # hitung lama tugas
        am.lama_tugas = hitung_lama_tugas(am.tanggal_sk_tugas)
        similarity_scores = [
            (b, score) for a, b, score in similarity_matrix if a == am.judul and score > 85]
        # sort by descending similarity score
        similarity_scores.sort(key=lambda x: x[1], reverse=True)
        # list of similar juduls
        am.mirip_juduls = [b for b, score in similarity_scores]
        # list of (judul, score) tuples
        am.similarity_scores = similarity_scores

        # calculate average similarity score
        total_score = sum(score for _, score in similarity_scores)
        num_scores = len(similarity_scores)
        if num_scores > 0:
            am.average_similarity_score = total_score / num_scores
        else:
            am.average_similarity_score = 0

    return aktivitas


def hitung_lama_tugas(tanggal_sk_tugas: date) -> str:
    today = date.today()
    delta = today - tanggal_sk_tugas
    total_days = delta.days
    total_months = int(total_days / 30.44)  # Average number of days per month

    if total_months >= 12:
        years = int(total_months / 12)
        months = total_months % 12
        if years == 1:
            year_string = "1 year"
        else:
            year_string = f"{years} years"
        if months == 1:
            month_string = "1 month"
        else:
            month_string = f"{months} months"
        return f"{year_string}, {month_string}"
    else:
        if total_months == 1:
            return "1 month"
        elif total_days == 1:
            return "1 day"
        else:
            return f"{total_days} days"


@Aktivitas.post("/api/am", tags=["Aktivitas_mhs"], response_model=GetAktivits)
async def add_aktivitas(am: AmSchema, db: Session = Depends(get_db), isAktiv=Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")

    data = AktivitasMhs(
        jenis_anggota=am.jenis_anggota,
        id_jenis_aktivitas=am.id_jenis_aktivitas,
        id_prodi=am.id_prodi,
        judul=am.judul,
        lokasi=am.lokasi,
        sk_tugas=am.sk_tugas,
        tanggal_sk_tugas=am.tanggal_sk_tugas
    )
    db.add(data)
    db.commit()
    db.refresh(data)
    return data
