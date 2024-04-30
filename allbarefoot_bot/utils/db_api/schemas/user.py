import datetime
from sqlalchemy.sql import func
from sqlalchemy import Column, Boolean, Integer, BigInteger, String, DateTime, Float, sql

from utils.db_api.db_gino import BaseModel


class User(BaseModel):
    __tablename__ = 'user'
    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(100))
    referer = Column(BigInteger)
    balance = Column(Integer)
    status = Column(String(100))
    zarabotok = Column(BigInteger)
    bloger = Column(Boolean)
    percent = Column(Integer)

    query: sql.Select
