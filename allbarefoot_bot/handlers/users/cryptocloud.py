from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import xlsxwriter
import io
import os

from data.config import admin_id, CRYPTOCLOUD_APIKEY, CRYPTOCLOUD_SHOPID
from loader import dp, bot
from utils.db_api import quick_commands
from keyboards.inline import main_keyboards

from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
import copy
import hashlib
import json
import operator
import uuid

from data import config


class NoPaymentFound(Exception):
    pass


class NotEnoughMoney(Exception):
    pass


@dataclass
class Payment:
    amount: int
    uuid: str=''
    status: str=''
    currency: str=''

    async def check_payment(self):
        checkout = {
            "uuids": [self.uuid]
        }

        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.2.13) Gecko/20101203 SUSE/3.6.13-0.2.1 Firefox/3.6.13',
            'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Authorization': f'Token {CRYPTOCLOUD_APIKEY}',
            'Content-Type': 'application/json'
        }
       
        async with aiohttp.ClientSession() as session:
            async with session.post(url='https://api.cryptocloud.plus/v2/invoice/merchant/info', headers=HEADERS, json=checkout) as resp: 
                response = await resp.json()
                if response['status'] == 'success':
                    return response['result'][0]['status']
                


    @property
    async def init(self):
        request = {
            "amount": float(self.amount), 
            "shop_id": f'{CRYPTOCLOUD_SHOPID}', 
            'available_currencies': ['USDT_TCR20', 'ETH', 'BTC']
        }

        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; ru; rv:1.9.2.13) Gecko/20101203 SUSE/3.6.13-0.2.1 Firefox/3.6.13',
            'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Authorization': f'Token {CRYPTOCLOUD_APIKEY}',
            'Content-Type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url='https://api.cryptocloud.plus/v2/invoice/create', headers=HEADERS, json=request) as resp: 

                response = await resp.json()
                if response['status'] == 'success':
                    self.uuid = response['result']['uuid']
                    self.status = response['result']['status']
                    self.currency = response['result']['currency']
                    return response['result']['link']
                else:
                    return response