import datetime
from sqlalchemy.sql import func
from sqlalchemy import Column, Boolean, Integer, BigInteger, String, DateTime, Float, sql

from utils.db_api.db_gino import BaseModel


class Order(BaseModel):
    __tablename__ = 'order'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    time_created = Column(String(50))
    link_name_number = Column(String(300))
    name_user = Column(String(100))
    address = Column(String(300))
    phone = Column(String(50))
    model_name = Column(String(300))
    model_color = Column(String(100))
    model_size = Column(String(50))
    model_price = Column(String(10))
    currency = Column(String(3))
    screen = Column(String(100))
    bonus = Column(String(10))

    query: sql.Select
