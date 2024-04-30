from datetime import datetime
import io
import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
import xlsxwriter

from data.config import admin_id
from loader import dp, bot
from utils.db_api import quick_commands
from keyboards.inline import main_keyboards


@dp.callback_query_handler(text='excel')
async def question1(call: types.CallbackQuery, state: FSMContext): 
    workbook = xlsxwriter.Workbook(f'/root/allbarefoot_bot/Report.xlsx')
    worksheet_transactions = workbook.add_worksheet('Заказы')
    bold = workbook.add_format({'bold': True, 'border': 1})

    worksheet_transactions.write('A1', 'Дата заявки', bold)
    worksheet_transactions.write('B1', '№ заявки в боте', bold)
    worksheet_transactions.write('C1', 'Имя, фамилия', bold)
    worksheet_transactions.write('D1', 'Адрес', bold)
    worksheet_transactions.write('E1', 'Номер телефона', bold)
    worksheet_transactions.write('F1', 'Ссылка на модель', bold)
    worksheet_transactions.write('G1', 'Модель', bold)
    worksheet_transactions.write('H1', 'Цвет модели', bold)
    worksheet_transactions.write('I1', 'Размер модели', bold)
    worksheet_transactions.write('J1', 'Цена в рублях', bold)
    worksheet_transactions.write('K1', 'Оплата бонусами', bold)
    worksheet_transactions.write('L1', 'Ссылка на клиента', bold)
    worksheet_transactions.write('M1', 'ID клиента', bold)
    worksheet_transactions.write('N1', 'Ссылка на оплату', bold)
    worksheet_transactions.set_column('A:A', 20)
    worksheet_transactions.set_column('B:B', 20)
    worksheet_transactions.set_column('C:C', 30)
    worksheet_transactions.set_column('D:D', 40)
    worksheet_transactions.set_column('E:E', 20)
    worksheet_transactions.set_column('F:F', 40)
    worksheet_transactions.set_column('G:G', 30)
    worksheet_transactions.set_column('H:H', 30)
    worksheet_transactions.set_column('I:I', 20)
    worksheet_transactions.set_column('J:J', 20)
    worksheet_transactions.set_column('K:K', 30)
    worksheet_transactions.set_column('L:L', 30)
    worksheet_transactions.set_column('M:M', 20)
    worksheet_transactions.set_column('N:N', 20)

    orders = await quick_commands.select_all_orders()
    for i in range(len(orders)):
        user = await quick_commands.select_user(orders[i].user_id)
        worksheet_transactions.write(f'A{i+2}', orders[i].time_created)
        worksheet_transactions.write(f'B{i+2}', orders[i].id)
        worksheet_transactions.write(f'C{i+2}', orders[i].name_user)
        worksheet_transactions.write(f'D{i+2}', orders[i].address)
        worksheet_transactions.write(f'E{i+2}', orders[i].phone)
        worksheet_transactions.write(f'F{i+2}', orders[i].link_name_number)
        worksheet_transactions.write(f'G{i+2}', orders[i].model_name)
        worksheet_transactions.write(f'H{i+2}', orders[i].model_color)
        worksheet_transactions.write(f'I{i+2}', orders[i].model_size)
        worksheet_transactions.write(f'J{i+2}', orders[i].model_price)
        worksheet_transactions.write(f'K{i+2}', orders[i].bonus)
        worksheet_transactions.write(f'L{i+2}', f't.me/{user.username}')
        worksheet_transactions.write(f'M{i+2}', orders[i].user_id)
        if orders[i].screen is not None:
            if len(orders[i].screen) > 20:
                worksheet_transactions.write(f'N{i+2}', f't.me/allbarefoot_bot?start=screen{orders[i].id}')
            else:
                worksheet_transactions.write(f'N{i+2}', orders[i].screen)            

    workbook.close()

    with open('/root/allbarefoot_bot/Report.xlsx', "rb") as fh:
        buf = io.BytesIO(fh.read())

    excel = InputFile(buf, filename='Report.xlsx')
    await call.message.delete()
    
    await call.message.answer_document(excel, reply_markup=main_keyboards.to_menu_keyboard)
    os.remove('/root/allbarefoot_bot/Report.xlsx')