import datetime
from sqlalchemy.sql import func
from sqlalchemy import Column, Boolean, Integer, BigInteger, String, DateTime, Float, sql

from utils.db_api.db_gino import BaseModel


class Feedback(BaseModel):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True, autoincrement=True)
    photo = Column(String(100))
    text = Column(String(1024))
    confirmed = Column(String(1))

    query: sql.Select