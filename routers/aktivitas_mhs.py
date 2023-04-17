from datetime import date, timedelta
from difflib import SequenceMatcher
from itertools import combinations
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from config.condb import get_db
from models.model import AktivitasMhs
from schemas.am import AddAktivitas, UpdateAktivitas, AmSchema, Analisis

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


def hitung_jadwal_seminar(tanggal_sk_tugas: date, jangka_waktu: Optional[int] = 3) -> date:
    return tanggal_sk_tugas + timedelta(days=30 * jangka_waktu)


def hitung_jadwal_ujian(tanggal_seminar: date, jangka_waktu: Optional[int] = 3) -> date:
    return tanggal_seminar + timedelta(days=30 * jangka_waktu)


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
        # check if seminar date or ujian date has passed
        today = date.today()
        if am.tanggal_seminar and am.tanggal_seminar < today:
            am.pesan_seminar = "Target seminar tidak terpenuhi."
        else:
            am.pesan_seminar = "Dalam Proses Bimbingan"

        if am.tanggal_ujian and am.tanggal_ujian < today:
            am.pesan_ujian = "Target ujian tidak terpenuhi."
        else:
            am.pesan_ujian = "Dalam Proses Bimbingan"

    return aktivitas


@Aktivitas.get("/api/am/{id_prodi}", tags=["Aktivitas_mhs"], response_model=List[Analisis])
async def get_aktivitas_by_prodi(id_prodi: int, db: Session = Depends(get_db), IsAktiv=Depends(get_current_active_user)):
    if not IsAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")
    aktivitas = db.query(AktivitasMhs).filter(
        AktivitasMhs.id_prodi == id_prodi).all()
    if not aktivitas:
        raise HTTPException(
            status_code=404, detail=f"Aktivitas mahasiswa dengan id_prodi {id_prodi} tidak ditemukan")
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

         # check if seminar date or ujian date has passed
        today = date.today()
        if am.tanggal_seminar and am.tanggal_seminar < today:
            am.pesan_seminar = "Target seminar tidak terpenuhi."
        else:
            am.pesan_seminar = "Dalam Proses Bimbingan"

        if am.tanggal_ujian and am.tanggal_ujian < today:
            am.pesan_ujian = "Target ujian tidak terpenuhi."
        else:
            am.pesan_ujian = "Dalam Proses Bimbingan"

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


@Aktivitas.post("/api/am", tags=["Aktivitas_mhs"], response_model=AddAktivitas)
async def add_aktivitas(am: AddAktivitas, db: Session = Depends(get_db), isAktiv: bool = Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")

    data = AktivitasMhs(**am.dict())
    # hitung tanggal seminar dan tanggal ujian
    data.tanggal_seminar = hitung_jadwal_seminar(data.tanggal_sk_tugas)
    data.tanggal_ujian = hitung_jadwal_ujian(data.tanggal_seminar)

    db.add(data)
    db.commit()
    db.refresh(data)
    return data


@Aktivitas.put("/api/am/{id}", tags=["Aktivitas_mhs"], response_model=UpdateAktivitas)
async def update_aktivitas(id: int, aktivitas: UpdateAktivitas, db: Session = Depends(get_db), IsAktiv=Depends(get_current_active_user)):
    if not IsAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")

    db_am = db.query(AktivitasMhs).filter(AktivitasMhs.id == id)

    if not db_am.first():
        raise HTTPException(
            status_code=404, detail="Aktivitas tidak ditemukan")

    db_am.update(aktivitas.dict(exclude_unset=True))
    db.commit()
    db.refresh(db_am.first())

    return db_am.first()


@Aktivitas.delete("/api/am/{id}", tags=["Aktivitas_mhs"], response_class=JSONResponse)
async def delete_Aktivitas_mahasiswa(id: int, db: Session = Depends(get_db), isAktiv: bool = Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat menghapus user, akun tidak aktif")
    try:
        prodi = db.query(AktivitasMhs).filter(AktivitasMhs.id == id).first()
        if not prodi:
            raise HTTPException(
                status_code=404, detail=f"User dengan id {id} tidak ditemukan")
        db.delete(prodi)
        db.commit()
        return {f"Prodi dengan Id {id} berhasil dihapus": True}
    except:
        raise HTTPException(
            status_code=500, detail="Terjadi kesalahan saat menghapus user")
