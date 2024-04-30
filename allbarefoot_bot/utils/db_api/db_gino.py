from typing import List

from aiogram import Dispatcher
from gino import Gino
import sqlalchemy as sa
from sqlalchemy import Column, String
from datetime import datetime
import pytz

from data import config

db = Gino()

def time_now():
    now = str(datetime.now())
    index_dot = now.index('.')
    now = now[:index_dot] + ' по МСК'
    return now

# Пример из https://github.com/aiogram/bot/blob/master/app/models/db.py

class BaseModel(db.Model):
    __abstract__ = True

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        primary_key_columns: List[sa.Column] = table.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name])
            for column in primary_key_columns
        }
        values_str = " ".join(f"{name}={value!r}" for name, value in values.items())
        return f"<{model} {values_str}>"


class TimedBaseModel(BaseModel):
    __abstract__ = True

    created_at = Column(String(30), server_default=time_now())
    
    updated_at = Column(String(30),
                        default=time_now(),
                        onupdate=time_now(),
                        server_default=time_now())


async def on_startup(dispatcher: Dispatcher):
    await db.set_bind(config.POSTGRES_URI)
    # await db.gino.drop_all()
    await db.gino.create_all()