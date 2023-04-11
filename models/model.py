from config.db import Base
from sqlalchemy import Column, Integer, String


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(50))
    email = Column(String(100), unique=True)
    password = Column(String(100))
    rule = Column(String(20))


class Prodi(Base):
    __tablename__ = "prodi"
    id = Column(Integer, primary_key=True, index=True)
    code_prodi = Column(String(10), unique=True)
    nama_prodi = Column(String(20))
