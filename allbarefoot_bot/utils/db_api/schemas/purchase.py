import datetime
from sqlalchemy.sql import func
from sqlalchemy import Column, Boolean, Integer, BigInteger, String, DateTime, Float, sql

from utils.db_api.db_gino import BaseModel


class Purchase(BaseModel):
    __tablename__ = 'purchase'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    name = Column(String(50))
    time = Column(DateTime, server_default=func.now())
    amount = Column(Float(20))
    currency = Column(String(10))
    status = Column(String(10))

    query: sql.Select
