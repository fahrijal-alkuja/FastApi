from config.db import Base
from sqlalchemy import Column, Integer, String


class Prodi(Base):
    __tablename__ = "prodi"
    id = Column(Integer, primary_key=True, index=True)
    code_prodi = Column(String(10), unique=True)
    nama_prodi = Column(String(20))
