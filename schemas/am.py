from datetime import date
from typing import List, Tuple
from pydantic import BaseModel


class AmSchema(BaseModel):
    nim: str
    nama: str
    tahun_masuk: str
    jenis_anggota: str
    id_jenis_aktivitas: str
    id_prodi: str
    judul: str
    lokasi: str
    sk_tugas: str
    tanggal_sk_tugas: date

    class Config:
        orm_mode = True


class GetAktivitas(AmSchema):
    id: int


class UpdateAktivitas(AmSchema):
    id: int


class Analisis(AmSchema):
    id: int
    lama_tugas: str
    similarity_scores: List[Tuple[str, float]] = []
    # mirip_juduls: List[str] = []
    average_similarity_score: float = 0.0
