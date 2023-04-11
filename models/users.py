from config.db import Base
from sqlalchemy import Column, Integer, String
from models.prodi import Prodi


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    password = Column(String(100))
    rule = Column(String(20))
