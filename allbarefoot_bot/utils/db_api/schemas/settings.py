import datetime
from sqlalchemy.sql import func
from sqlalchemy import Column, Boolean, Integer, BigInteger, String, DateTime, Float, sql

from utils.db_api.db_gino import BaseModel


class Settings(BaseModel):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    coeff_2vetka = Column(Integer)
    coeff_3vetka = Column(Integer)
    coeff_4vetka = Column(Integer)
    button_1vetka = Column(String(50))
    button_2vetka = Column(String(50))
    button_3vetka = Column(String(50))
    button_4vetka = Column(String(50))
    button1_active = Column(Boolean)
    button2_active = Column(Boolean)
    button3_active = Column(Boolean)
    button4_active = Column(Boolean)
    text_1vetka = Column(String(1024))
    text_2vetka = Column(String(1024))
    text_3vetka = Column(String(1024))
    text_4vetka = Column(String(1024))
    text_card = Column(String(1024))
    text_sbp = Column(String(1024))
    percent = Column(Integer)

    query: sql.Select