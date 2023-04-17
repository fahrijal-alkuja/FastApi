from datetime import date
from pydantic import BaseModel


class Aktivitas(BaseModel):
    nim: str
    nama: str
    tahun_masuk: str
    judul: str
    lokasi: str
    sk_tugas: str
    tanggal_sk_tugas: date

    class Config:
        orm_mode = True


class ProblemSchema(BaseModel):
    id_aktivitas: int
    keterangan: str

    class Config:
        orm_mode = True


class GetProblem(ProblemSchema):
    aktivitas: Aktivitas


class AddProblem(ProblemSchema):
    pass


class UpdateProblem(ProblemSchema):
    pass
