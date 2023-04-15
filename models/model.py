
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from config.db import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    password = Column(String(100))
    rule = Column(String(20))
    prodi_id = Column(Integer, ForeignKey(
        'prodi.id', ondelete="CASCADE"), nullable=False)
    prodi = relationship("Prodi")


class Prodi(Base):
    __tablename__ = "prodi"

    id = Column(Integer, primary_key=True, index=True)
    code_prodi = Column(String(10), unique=True)
    nama_prodi = Column(String(20))


class AktivitasMhs(Base):
    __tablename__ = "aktivitas_mahasiswa"

    id = Column(Integer, primary_key=True, index=True)
    jenis_anggota = Column(String(4))
    id_jenis_aktivitas = Column(String(4))
    id_prodi = Column(String(9))
    judul = Column(String(100))
    lokasi = Column(String(50))
    sk_tugas = Column(String(50))
    tanggal_sk_tugas = Column(Date, nullable=False,
                              server_default="1970-01-01")
