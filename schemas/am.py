from datetime import date
from typing import List, Tuple
from pydantic import BaseModel


class AmSchema(BaseModel):
    jenis_anggota: str
    id_jenis_aktivitas: str
    id_prodi: str
    judul: str
    lokasi: str
    sk_tugas: str
    tanggal_sk_tugas: date

    class Config:
        orm_mode = True


class GetAktivits(AmSchema):
    id: int


class UpdateAktivits(AmSchema):
    id: int


class Analisis(AmSchema):
    lama_tugas: str
    similarity_scores: List[Tuple[str, float]] = []
    # mirip_juduls: List[str] = []
    average_similarity_score: float = 0.0
