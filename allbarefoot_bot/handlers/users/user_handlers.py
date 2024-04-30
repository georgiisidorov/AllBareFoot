import logging
import random
import json

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ContentType, MediaGroup, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, PreCheckoutQuery
from aiogram.types.input_media import InputMediaPhoto
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, BadRequest
import asyncio
import yahoo_fin.stock_info as si
from datetime import datetime, timedelta
import gspread_asyncio
from google.oauth2.service_account import Credentials

from data.config import admin_id
from data import config
from loader import dp
from states import states
from utils.db_api import quick_commands
from keyboards.inline import main_keyboards, order_keyboards
from handlers.users.cryptocloud import Payment



def convert_currency_yahoofin(src, dst, amount):
    symbol = f"{src}{dst}=X"
    live_price = si.get_live_price(symbol)
    return live_price * amount


def get_creds():
    creds = Credentials.from_service_account_file("allbarefoot-a3149ccc3f08.json")
    scoped = creds.with_scopes([
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ])
    return scoped


agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)


async def check_google_sheets(agcm):
    agc = await agcm.authorize()
    ss = await agc.open_by_url(config.spreadsheet_url)
    worksheet = await ss.get_worksheet(0)

    return worksheet
    

# ----------------------------- B E L E N K A -----------------------------------


@dp.callback_query_handler(text='belenka_sale')
async def belenka_sale(call: CallbackQuery, state: FSMContext):
    await call.answer()
    text = await quick_commands.select_text_1vetka()
    msg = await call.message.edit_text(
        text=text, 
        reply_markup=main_keyboards.to_menu_keyboard,
        parse_mode='html',
        disable_web_page_preview=True
    )
    
    await state.update_data(msg_id=msg.message_id)
    await states.Belenka.LinkNameNumber.set()


@dp.message_handler(state=states.Belenka.LinkNameNumber)
async def linknameumber(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Ваше имя и фамилия ЛАТИНСКИМИ буквами для отправки посылки", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(link_name_number=message.text)
    await states.Belenka.NameUser.set()


@dp.message_handler(state=states.Belenka.NameUser)
async def nameuser(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Адрес доставки ЛАТИНСКИМИ буквами (улица, номер дома/квартиры, город, область, индекс). Проверьте корректное заполнение адреса", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(name_user=message.text)
    await states.Belenka.Address.set()


@dp.message_handler(state=states.Belenka.Address)
async def address(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Ваш номер телефона", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(address=message.text)
    await states.Belenka.Phone.set()


@dp.message_handler(state=states.Belenka.Phone)
async def phone(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Ещё раз модель из описания, которую хотите приобрести (для проверки и во избежание ошибки)", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(phone=message.text)
    await states.Belenka.ModelName.set()


@dp.message_handler(state=states.Belenka.ModelName)
async def modelname(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Цвет модели (как указано на сайте belenka)", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(model_name=message.text)
    await states.Belenka.ModelColor.set()


@dp.message_handler(state=states.Belenka.ModelColor)
async def modelcolor(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Размер модели (проверьте наличие на сайте!)", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(model_color=message.text)
    await states.Belenka.ModelSize.set()


@dp.message_handler(state=states.Belenka.ModelSize)
async def modelsize(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Стоимость модели в рублях, просто число без доп.символов", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(model_size=message.text)
    await states.Belenka.ModelPrice.set()


@dp.message_handler(state=states.Belenka.ModelPrice)
async def modelprice(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    try:
        await dp.bot.edit_message_text(
            chat_id=message.from_user.id, 
            message_id=data['msg_id'], 
            text=f"Окончательная сумма к оплате:\n<b>{int(message.text)}RUB</b>\n\nВыберите ниже способ оплаты:", 
            reply_markup=main_keyboards.oplata_keyboard
        )
        await state.update_data(bonus=0, model_price=int(message.text))
        await states.Belenka.Screen.set()

    except ValueError:
        await dp.bot.edit_message_text(
            chat_id=message.from_user.id, 
            message_id=data['msg_id'], 
            text=f"Неправильный формат данных, введите число", 
            reply_markup=main_keyboards.cancel_keyboard
        )


@dp.callback_query_handler(text='tinkoff', state=states.Belenka.Screen)
async def tinkoff(call: CallbackQuery, state: FSMContext):
    await call.answer()
    text = await quick_commands.select_text_card()
    msg = await call.message.edit_text(
        text=text, 
        reply_markup=main_keyboards.cancel_keyboard,
        parse_mode='html'
    )
    
    await state.update_data(option='На карту', msg_id=msg.message_id)


@dp.callback_query_handler(text='SBP', state=states.Belenka.Screen)
async def sbp(call: CallbackQuery, state: FSMContext):
    await call.answer()
    text = await quick_commands.select_text_sbp()
    msg = await call.message.edit_text(
        text=text, 
        reply_markup=main_keyboards.cancel_keyboard,
        parse_mode='html'
    )
    
    await state.update_data(option='СБП', msg_id=msg.message_id)


@dp.callback_query_handler(text='bonus', state=states.Belenka.Screen)
async def bonus(call: CallbackQuery, state: FSMContext):
    await call.answer()
    user = await quick_commands.select_user(call.from_user.id)
    if user.balance == 0:
        await call.message.edit_text(
            text='Ваш баланс пуст! 😔', 
            reply_markup=main_keyboards.back_keyboard,
            parse_mode='html'
        )
    else:
        await call.message.edit_text(
            text=f'Ваш баланс - {user.balance}RUB\n\nСписать в учёт покупки?', 
            reply_markup=main_keyboards.bonus_keyboard,
            parse_mode='html'
        )


@dp.callback_query_handler(text='back', state=states.Belenka.Screen)
async def modelprice(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await call.message.edit_text(
        text=f"Окончательная сумма к оплате:\n<b>{data['model_price']}RUB</b>\n\nВыберите ниже способ оплаты:", 
        reply_markup=main_keyboards.oplata_keyboard
    )


@dp.callback_query_handler(text='yes', state=states.Belenka.Screen)
async def modelprice(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    user = await quick_commands.select_user(call.from_user.id)
    if user.balance >= int(data['model_price']):
        await quick_commands.update_user_balance(call.from_user.id, user.balance-int(data['model_price']))

        await call.message.edit_text("""Ваши бонусы списаны!\n\nПоздравляем и БлагоДарим за покупку. 
👣 Далее мы сделаем все возможное, чтобы Ваш босоногий парк как можно быстрее пополнился еще одной прекрасной парой. 
Номер трека сообщим здесь же.

C любовью, Команда ALL Barefoot""", 
            reply_markup=main_keyboards.to_menu_keyboard
        )

        order = await quick_commands.add_order(
            user_id=call.from_user.id,
            time_created=datetime.now().strftime("%d.%m.%Y %H:%M"),
            link_name_number=data['link_name_number'], 
            name_user=data['name_user'], 
            address=data['address'], 
            phone=data['phone'], 
            model_name=data['model_name'], 
            model_color=data['model_color'], 
            model_size=data['model_size'], 
            model_price=str(data['model_price']),
            currency='USD',
            screen='Бонусы',
            bonus=str(data['bonus'])
        )

        worksheet = await check_google_sheets(agcm)
        col1 = await worksheet.col_values(2)
        await worksheet.update_cell(len(col1)+1, 2, datetime.now().strftime("%d.%m.%Y %H:%M"))
        await worksheet.update_cell(len(col1)+1, 3, order.id)
        await worksheet.update_cell(len(col1)+1, 4, data['name_user'])
        await worksheet.update_cell(len(col1)+1, 5, data['address'])
        await worksheet.update_cell(len(col1)+1, 6, data['phone'])
        await worksheet.update_cell(len(col1)+1, 8, data['link_name_number'])
        await worksheet.update_cell(len(col1)+1, 9, data['model_name'])
        await worksheet.update_cell(len(col1)+1, 10, data['model_color'])
        await worksheet.update_cell(len(col1)+1, 11, data['model_size'])
        await worksheet.update_cell(len(col1)+1, 15, data['model_price'])
        await worksheet.update_cell(len(col1)+1, 16, data['bonus'])
        if call.from_user.username is not None:
            await worksheet.update_cell(len(col1)+1, 23, f't.me/{call.from_user.username}')
        await worksheet.update_cell(len(col1)+1, 24, call.from_user.id)
        await worksheet.update_cell(len(col1)+1, 25, 'Бонусы')

        await state.finish()

    else:

        await call.message.edit_text( 
            text=f"Ваши бонусы списаны!", 
            reply_markup=main_keyboards.back_keyboard
        )

        await state.update_data(bonus=user.balance, model_price=str(int(data['model_price'])))
        await quick_commands.update_user_balance(0)


@dp.callback_query_handler(text='crypto', state=states.Belenka.Screen)
async def crypto(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    amount = int(data['model_price'])

    price = convert_currency_yahoofin('RUB', "USD", amount)
    price = round(price, 2)

    payment = Payment(price)
    link = await payment.init
    uuid = payment.uuid
    await state.update_data(uuid=uuid, link=link, amount=price)
    markup = await order_keyboards.markup_pay(link)

    await call.message.edit_text('''💸 Ваша ссылка для оплаты: {link}

Сумма к оплате: ~ ${price}
Ссылка действительна в течение 2-х часов.

⚠️ ВАЖНО! Необходимо отправить сумму не меньше указанной, иначе вы не получите подтверждение оплаты. Закладывайте расходы на комиссию.'''.format(link=link, price=price), reply_markup=markup)


@dp.callback_query_handler(text='paid', state=states.Belenka.Screen)
async def paid(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    payment = Payment(uuid=data['uuid'], amount=data['amount'])
    user = await quick_commands.select_user(call.from_user.id)

    status = await payment.check_payment()
    try:
        if status == 'created':
            await call.answer('❌ Оплата не найдена!', show_alert=True)
        elif status == 'partial':
            await call.answer('⚠️ Вы отправили недостаточно средств для оплаты, отправьте еще!', show_alert=True)
        elif status == 'paid':
            await call.message.edit_text("""Поздравляем и БлагоДарим за покупку. 
👣 Далее мы сделаем все возможное, чтобы Ваш босоногий парк как можно быстрее пополнился еще одной прекрасной парой. 
Номер трека сообщим здесь же.

C любовью, Команда ALL Barefoot""", 
                reply_markup=main_keyboards.to_menu_keyboard
            )

            order = await quick_commands.add_order(
                user_id=call.from_user.id,
                time_created=datetime.now().strftime("%d.%m.%Y %H:%M"),
                link_name_number=data['link_name_number'], 
                name_user=data['name_user'], 
                address=data['address'], 
                phone=data['phone'], 
                model_name=data['model_name'], 
                model_color=data['model_color'], 
                model_size=data['model_size'], 
                model_price=str(data['model_price']),
                currency='USD',
                screen='Через крипту',
                bonus=str(data['bonus'])
            )

            setts = await quick_commands.select_settings()
            percent = setts.percent

            user = await quick_commands.select_user(call.from_user.id)
            if user.referer is not None:
                referer = await quick_commands.select_user(user.referer)
                await quick_commands.update_user_balance(user.referer, referer.balance+round(int(data['model_price'])*percent/100))

            worksheet = await check_google_sheets(agcm)
            col1 = await worksheet.col_values(2)
            await worksheet.update_cell(len(col1)+1, 2, datetime.now().strftime("%d.%m.%Y %H:%M"))
            await worksheet.update_cell(len(col1)+1, 3, order.id)
            await worksheet.update_cell(len(col1)+1, 4, data['name_user'])
            await worksheet.update_cell(len(col1)+1, 5, data['address'])
            await worksheet.update_cell(len(col1)+1, 6, data['phone'])
            await worksheet.update_cell(len(col1)+1, 8, data['link_name_number'])
            await worksheet.update_cell(len(col1)+1, 9, data['model_name'])
            await worksheet.update_cell(len(col1)+1, 10, data['model_color'])
            await worksheet.update_cell(len(col1)+1, 11, data['model_size'])
            await worksheet.update_cell(len(col1)+1, 15, data['model_price'])
            await worksheet.update_cell(len(col1)+1, 16, data['bonus'])
            if call.from_user.username is not None:
                await worksheet.update_cell(len(col1)+1, 23, f't.me/{call.from_user.username}')
            await worksheet.update_cell(len(col1)+1, 24, call.from_user.id)
            await worksheet.update_cell(len(col1)+1, 25, 'Крипта')

            await state.finish()

    except Exception as err:
        await dp.bot.send_message(admin_id[0], f'{status}')
        await dp.bot.send_message(admin_id[0], f'{err}')


@dp.message_handler(state=states.Belenka.Screen, content_types=ContentType.PHOTO)
async def photo_screen(message: Message, state: FSMContext):
    data = await state.get_data()
    await dp.bot.delete_message(chat_id=message.from_user.id, message_id=data['msg_id'])

    await message.delete()

    await message.answer(
        text=f"""Поздравляем и БлагоДарим за покупку. 
👣 Далее мы сделаем все возможное, чтобы Ваш босоногий парк как можно быстрее пополнился еще одной прекрасной парой. 
Номер трека сообщим здесь же.

C любовью, Команда ALL Barefoot""", 
        reply_markup=main_keyboards.to_menu_keyboard
    )

    ordernew = await quick_commands.add_order(
        user_id=message.from_user.id,
        time_created=datetime.now().strftime("%d.%m.%Y %H:%M"),
        link_name_number=data['link_name_number'], 
        name_user=data['name_user'], 
        address=data['address'], 
        phone=data['phone'], 
        model_name=data['model_name'], 
        model_color=data['model_color'], 
        model_size=data['model_size'], 
        model_price=str(data['model_price']),
        currency='RUB',
        screen=message.photo[-1].file_id,
        bonus=str(data['bonus'])
    )

    await dp.bot.send_photo(admin_id[1], message.photo[-1].file_id, f'Номер заказа: {ordernew.id}\nИмя: {data["name_user"]}\nК оплате: {data["model_price"]}RUB\nСпособ оплаты: {data["option"]}')

    setts = await quick_commands.select_settings()
    percent = setts.percent

    user = await quick_commands.select_user(message.from_user.id)
    if user.referer is not None:
        referer = await quick_commands.select_user(user.referer)
        await quick_commands.update_user_balance(user.referer, referer.balance+round(int(data['model_price'])*percent/100))

    worksheet = await check_google_sheets(agcm)
    col1 = await worksheet.col_values(2)
    await worksheet.update_cell(len(col1)+1, 2, datetime.now().strftime("%d.%m.%Y %H:%M"))
    await worksheet.update_cell(len(col1)+1, 3, ordernew.id)
    await worksheet.update_cell(len(col1)+1, 4, data['name_user'])
    await worksheet.update_cell(len(col1)+1, 5, data['address'])
    await worksheet.update_cell(len(col1)+1, 6, data['phone'])
    await worksheet.update_cell(len(col1)+1, 8, data['link_name_number'])
    await worksheet.update_cell(len(col1)+1, 9, data['model_name'])
    await worksheet.update_cell(len(col1)+1, 10, data['model_color'])
    await worksheet.update_cell(len(col1)+1, 11, data['model_size'])
    await worksheet.update_cell(len(col1)+1, 15, data['model_price'])
    await worksheet.update_cell(len(col1)+1, 16, data['bonus'])
    if message.from_user.username is not None:
        await worksheet.update_cell(len(col1)+1, 23, f't.me/{message.from_user.username}')
    await worksheet.update_cell(len(col1)+1, 24, message.from_user.id)
    await worksheet.update_cell(len(col1)+1, 25, f"t.me/allbarefoot_bot?start=screen{ordernew.id}")


# ------------------------------- Б О С О О Б У В Ь --------------------------------------


@dp.callback_query_handler(text='bosoobuv')
async def bosoobuv(call: CallbackQuery, state: FSMContext):
    await call.answer()
    text = await quick_commands.select_text_2vetka()
    msg = await call.message.edit_text(
        text=text, 
        reply_markup=main_keyboards.to_menu_keyboard,
        parse_mode='html'
    )
    await state.update_data(msg_id=msg.message_id)
    await states.Bosoobuv.LinkNameNumber.set()


@dp.message_handler(state=states.Bosoobuv.LinkNameNumber)
async def linknameumber(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Ваше имя и фамилия ЛАТИНСКИМИ буквами для отправки посылки", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(link_name_number=message.text)
    await states.Bosoobuv.NameUser.set()


@dp.message_handler(state=states.Bosoobuv.NameUser)
async def nameuser(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Адрес доставки ЛАТИНСКИМИ буквами (улица, номер дома/квартиры, город, область, индекс). Проверьте корректное заполнение адреса", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(name_user=message.text)
    await states.Bosoobuv.Address.set()


@dp.message_handler(state=states.Bosoobuv.Address)
async def address(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Ваш номер телефона", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(address=message.text)
    await states.Bosoobuv.Phone.set()


@dp.message_handler(state=states.Bosoobuv.Phone)
async def phone(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Название модели, которую хотите приобрести (для проверки и во избежание ошибки)", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(phone=message.text)
    await states.Bosoobuv.ModelName.set()


@dp.message_handler(state=states.Bosoobuv.ModelName)
async def modelname(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Цвет модели (как указано на сайте)", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(model_name=message.text)
    await states.Bosoobuv.ModelColor.set()


@dp.message_handler(state=states.Bosoobuv.ModelColor)
async def modelcolor(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Размер модели (проверьте наличие на сайте!)", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(model_color=message.text)
    await states.Bosoobuv.ModelSize.set()


@dp.message_handler(state=states.Bosoobuv.ModelSize)
async def modelsize(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Стоимость модели (в ЕВРО!!!), просто число без доп.символов", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(model_size=message.text)
    await states.Bosoobuv.ModelPrice.set()


@dp.message_handler(state=states.Bosoobuv.ModelPrice)
async def modelprice(message: Message, state: FSMContext):
    data = await state.get_data()
    coeff = await quick_commands.select_coeff_2vetka()

    await message.delete()
    try:
        await dp.bot.edit_message_text(
            chat_id=message.from_user.id, 
            message_id=data['msg_id'], 
            text=f"Окончательная сумма к оплате:\n<b>{int(message.text)*coeff}RUB</b>\n\nВыберите ниже способ оплаты:", 
            reply_markup=main_keyboards.oplata_keyboard
        )
        await state.update_data(bonus=0, euro=message.text, model_price=str(int(message.text)*coeff))
        await states.Bosoobuv.Screen.set()

    except ValueError:
        await dp.bot.edit_message_text(
            chat_id=message.from_user.id, 
            message_id=data['msg_id'], 
            text=f"Неправильный формат данных, введите число", 
            reply_markup=main_keyboards.cancel_keyboard
        )
    

@dp.callback_query_handler(text='tinkoff', state=states.Bosoobuv.Screen)
async def tinkoff(call: CallbackQuery, state: FSMContext):
    await call.answer()
    text = await quick_commands.select_text_card()
    msg = await call.message.edit_text(
        text=text, 
        reply_markup=main_keyboards.cancel_keyboard,
        parse_mode='html'
    )
    
    await state.update_data(option='На карту', msg_id=msg.message_id)


@dp.callback_query_handler(text='SBP', state=states.Bosoobuv.Screen)
async def sbp(call: CallbackQuery, state: FSMContext):
    await call.answer()
    text = await quick_commands.select_text_sbp()
    msg = await call.message.edit_text(
        text=text, 
        reply_markup=main_keyboards.cancel_keyboard,
        parse_mode='html'
    )
    
    await state.update_data(option='СБП', msg_id=msg.message_id)


@dp.callback_query_handler(text='bonus', state=states.Bosoobuv.Screen)
async def bonus(call: CallbackQuery, state: FSMContext):
    await call.answer()
    user = await quick_commands.select_user(call.from_user.id)
    if user.balance == 0:
        await call.message.edit_text(
            text='Ваш баланс пуст! 😔', 
            reply_markup=main_keyboards.back_keyboard,
            parse_mode='html'
        )
    else:
        await call.message.edit_text(
            text=f'Ваш баланс - {user.balance}RUB\n\nСписать в учёт покупки?', 
            reply_markup=main_keyboards.bonus_keyboard,
            parse_mode='html'
        )


@dp.callback_query_handler(text='back', state=states.Bosoobuv.Screen)
async def modelprice(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await call.message.edit_text(
        text=f"Окончательная сумма к оплате:\n<b>{data['model_price']}RUB</b>\n\nВыберите ниже способ оплаты:", 
        reply_markup=main_keyboards.oplata_keyboard
    )


@dp.callback_query_handler(text='yes', state=states.Bosoobuv.Screen)
async def modelprice(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    user = await quick_commands.select_user(call.from_user.id)
    if user.balance >= int(data['model_price']):
        await quick_commands.update_user_balance(call.from_user.id, user.balance-int(data['model_price']))

        await call.message.edit_text("""Ваши бонусы списаны!\n\nПоздравляем и БлагоДарим за покупку. 
👣 Далее мы сделаем все возможное, чтобы Ваш босоногий парк как можно быстрее пополнился еще одной прекрасной парой. 
Номер трека сообщим здесь же.

C любовью, Команда ALL Barefoot""", 
            reply_markup=main_keyboards.to_menu_keyboard
        )

        order = await quick_commands.add_order(
            user_id=call.from_user.id,
            time_created=datetime.now().strftime("%d.%m.%Y %H:%M"),
            link_name_number=data['link_name_number'], 
            name_user=data['name_user'], 
            address=data['address'], 
            phone=data['phone'], 
            model_name=data['model_name'], 
            model_color=data['model_color'], 
            model_size=data['model_size'], 
            model_price=data['model_price'],
            currency='USD',
            screen='Бонусы',
            bonus=str(data['bonus'])
        )

        coeff = await quick_commands.select_coeff_2vetka()
        worksheet = await check_google_sheets(agcm)
        col1 = await worksheet.col_values(2)
        await worksheet.update_cell(len(col1)+1, 2, datetime.now().strftime("%d.%m.%Y %H:%M"))
        await worksheet.update_cell(len(col1)+1, 3, order.id)
        await worksheet.update_cell(len(col1)+1, 4, data['name_user'])
        await worksheet.update_cell(len(col1)+1, 5, data['address'])
        await worksheet.update_cell(len(col1)+1, 6, data['phone'])
        await worksheet.update_cell(len(col1)+1, 8, data['link_name_number'])
        await worksheet.update_cell(len(col1)+1, 9, data['model_name'])
        await worksheet.update_cell(len(col1)+1, 10, data['model_color'])
        await worksheet.update_cell(len(col1)+1, 11, data['model_size'])
        await worksheet.update_cell(len(col1)+1, 13, data['euro'])
        await worksheet.update_cell(len(col1)+1, 14, coeff)
        await worksheet.update_cell(len(col1)+1, 15, int(data['euro'])*coeff)
        await worksheet.update_cell(len(col1)+1, 16, data['bonus'])
        if call.from_user.username is not None:
            await worksheet.update_cell(len(col1)+1, 23, f't.me/{call.from_user.username}')
        await worksheet.update_cell(len(col1)+1, 24, call.from_user.id)
        await worksheet.update_cell(len(col1)+1, 25, 'Бонусы')

        await state.finish()

    else:

        await call.message.edit_text( 
            text=f"Ваши бонусы списаны!", 
            reply_markup=main_keyboards.back_keyboard
        )

        await state.update_data(bonus=user.balance, model_price=str(int(data['model_price'])))
        await quick_commands.update_user_balance(0)


@dp.callback_query_handler(text='crypto', state=states.Bosoobuv.Screen)
async def crypto(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    amount = int(data['model_price'])

    price = convert_currency_yahoofin('RUB', "USD", amount)
    price = round(price, 2)

    payment = Payment(price)
    link = await payment.init
    uuid = payment.uuid
    await state.update_data(uuid=uuid, link=link, amount=price)
    markup = await order_keyboards.markup_pay(link)

    await call.message.edit_text('''💸 Ваша ссылка для оплаты: {link}

Сумма к оплате: ~ ${price}
Ссылка действительна в течение 2-х часов.

⚠️ ВАЖНО! Необходимо отправить сумму не меньше указанной, иначе вы не получите подтверждение оплаты. Закладывайте расходы на комиссию.'''.format(link=link, price=price), reply_markup=markup)


@dp.callback_query_handler(text='paid', state=states.Bosoobuv.Screen)
async def paid(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    payment = Payment(uuid=data['uuid'], amount=data['amount'])
    user = await quick_commands.select_user(call.from_user.id)

    status = await payment.check_payment()
    try:
        if status == 'created':
            await call.answer('❌ Оплата не найдена!', show_alert=True)
        elif status == 'partial':
            await call.answer('⚠️ Вы отправили недостаточно средств для оплаты, отправьте еще!', show_alert=True)
        elif status == 'paid':
            await call.message.edit_text("""Поздравляем и БлагоДарим за покупку. 
👣 Далее мы сделаем все возможное, чтобы Ваш босоногий парк как можно быстрее пополнился еще одной прекрасной парой. 
Номер трека сообщим здесь же.

C любовью, Команда ALL Barefoot""", 
                reply_markup=main_keyboards.to_menu_keyboard
            )

            order = await quick_commands.add_order(
                user_id=call.from_user.id,
                time_created=datetime.now().strftime("%d.%m.%Y %H:%M"),
                link_name_number=data['link_name_number'], 
                name_user=data['name_user'], 
                address=data['address'], 
                phone=data['phone'], 
                model_name=data['model_name'], 
                model_color=data['model_color'], 
                model_size=data['model_size'], 
                model_price=data['model_price'],
                currency='USD',
                screen='Через крипту',
                bonus=str(data['bonus'])
            )

            coeff = await quick_commands.select_coeff_2vetka()
            setts = await quick_commands.select_settings()
            percent = setts.percent

            user = await quick_commands.select_user(call.from_user.id)
            if user.referer is not None:
                referer = await quick_commands.select_user(user.referer)
                await quick_commands.update_user_balance(user.referer, referer.balance+round(int(data['euro'])*coeff*percent/100))

            worksheet = await check_google_sheets(agcm)
            col1 = await worksheet.col_values(2)
            await worksheet.update_cell(len(col1)+1, 2, datetime.now().strftime("%d.%m.%Y %H:%M"))
            await worksheet.update_cell(len(col1)+1, 3, order.id)
            await worksheet.update_cell(len(col1)+1, 4, data['name_user'])
            await worksheet.update_cell(len(col1)+1, 5, data['address'])
            await worksheet.update_cell(len(col1)+1, 6, data['phone'])
            await worksheet.update_cell(len(col1)+1, 8, data['link_name_number'])
            await worksheet.update_cell(len(col1)+1, 9, data['model_name'])
            await worksheet.update_cell(len(col1)+1, 10, data['model_color'])
            await worksheet.update_cell(len(col1)+1, 11, data['model_size'])
            await worksheet.update_cell(len(col1)+1, 13, data['euro'])
            await worksheet.update_cell(len(col1)+1, 14, coeff)
            await worksheet.update_cell(len(col1)+1, 15, int(data['euro'])*coeff)
            await worksheet.update_cell(len(col1)+1, 16, data['bonus'])
            if call.from_user.username is not None:
                await worksheet.update_cell(len(col1)+1, 23, f't.me/{call.from_user.username}')
            await worksheet.update_cell(len(col1)+1, 24, call.from_user.id)
            await worksheet.update_cell(len(col1)+1, 25, 'Крипта')

            await state.finish()

    except Exception as err:
        await dp.bot.send_message(admin_id[0], f'{status}')
        await dp.bot.send_message(admin_id[0], f'{err}')


@dp.message_handler(state=states.Bosoobuv.Screen, content_types=ContentType.PHOTO)
async def photo_screen(message: Message, state: FSMContext):
    data = await state.get_data()

    await dp.bot.delete_message(chat_id=message.from_user.id, message_id=data['msg_id'])
    await message.delete()

    await message.answer(
        text=f"""Поздравляем и БлагоДарим за покупку. 
👣 Далее мы сделаем все возможное, чтобы Ваш босоногий парк как можно быстрее пополнился еще одной прекрасной парой. 
Номер трека сообщим здесь же.

C любовью, Команда ALL Barefoot""", 
        reply_markup=main_keyboards.to_menu_keyboard
    )

    order = await quick_commands.add_order(
        user_id=message.from_user.id,
        time_created=datetime.now().strftime("%d.%m.%Y %H:%M"),
        link_name_number=data['link_name_number'], 
        name_user=data['name_user'], 
        address=data['address'], 
        phone=data['phone'], 
        model_name=data['model_name'], 
        model_color=data['model_color'], 
        model_size=data['model_size'], 
        model_price=data['model_price'],
        currency='EUR',
        screen=message.photo[-1].file_id,
        bonus=str(data['bonus'])
    )

    await dp.bot.send_photo(admin_id[1], message.photo[-1].file_id, f'Номер заказа: {order.id}\nИмя: {data["name_user"]}\nК оплате: {data["model_price"]}RUB\nСпособ оплаты: {data["option"]}')

    coeff = await quick_commands.select_coeff_2vetka()
    setts = await quick_commands.select_settings()
    percent = setts.percent

    user = await quick_commands.select_user(message.from_user.id)
    if user.referer is not None:
        referer = await quick_commands.select_user(user.referer)
        await quick_commands.update_user_balance(user.referer, referer.balance+round(int(data['euro'])*coeff*percent/100))

    worksheet = await check_google_sheets(agcm)
    col1 = await worksheet.col_values(2)
    await worksheet.update_cell(len(col1)+1, 2, datetime.now().strftime("%d.%m.%Y %H:%M"))
    await worksheet.update_cell(len(col1)+1, 3, order.id)
    await worksheet.update_cell(len(col1)+1, 4, data['name_user'])
    await worksheet.update_cell(len(col1)+1, 5, data['address'])
    await worksheet.update_cell(len(col1)+1, 6, data['phone'])
    await worksheet.update_cell(len(col1)+1, 8, data['link_name_number'])
    await worksheet.update_cell(len(col1)+1, 9, data['model_name'])
    await worksheet.update_cell(len(col1)+1, 10, data['model_color'])
    await worksheet.update_cell(len(col1)+1, 11, data['model_size'])
    await worksheet.update_cell(len(col1)+1, 13, data['euro'])
    await worksheet.update_cell(len(col1)+1, 14, coeff)
    await worksheet.update_cell(len(col1)+1, 15, int(data['euro'])*coeff)
    await worksheet.update_cell(len(col1)+1, 16, data['bonus'])
    if message.from_user.username is not None:
        await worksheet.update_cell(len(col1)+1, 23, f't.me/{message.from_user.username}')
    await worksheet.update_cell(len(col1)+1, 24, message.from_user.id)
    await worksheet.update_cell(len(col1)+1, 25, f"t.me/allbarefoot_bot?start=screen{order.id}")



# ------------------------------- L I T T L E   S H O E S -------------------------------------


@dp.callback_query_handler(text='littleshoes')
async def littleshoes(call: CallbackQuery, state: FSMContext):
    await call.answer()
    text = await quick_commands.select_text_3vetka()
    msg = await call.message.edit_text(
        text=text, 
        reply_markup=main_keyboards.to_menu_keyboard, 
        parse_mode='html'
    )
    await state.update_data(msg_id=msg.message_id)
    await states.LittleShoes.LinkNameNumber.set()


@dp.message_handler(state=states.LittleShoes.LinkNameNumber)
async def linknameumber(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Ваше имя и фамилия ЛАТИНСКИМИ буквами для отправки посылки", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(link_name_number=message.text)
    await states.LittleShoes.NameUser.set()


@dp.message_handler(state=states.LittleShoes.NameUser)
async def nameuser(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Адрес доставки ЛАТИНСКИМИ буквами (улица, номер дома/квартиры, город, область, индекс). Проверьте корректное заполнение адреса", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(name_user=message.text)
    await states.LittleShoes.Address.set()


@dp.message_handler(state=states.LittleShoes.Address)
async def address(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Ваш номер телефона", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(address=message.text)
    await states.LittleShoes.Phone.set()


@dp.message_handler(state=states.LittleShoes.Phone)
async def phone(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Название модели, которую хотите приобрести (для проверки и во избежание ошибки)", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(phone=message.text)
    await states.LittleShoes.ModelName.set()


@dp.message_handler(state=states.LittleShoes.ModelName)
async def modelname(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Цвет модели (как указано на сайте)", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(model_name=message.text)
    await states.LittleShoes.ModelColor.set()


@dp.message_handler(state=states.LittleShoes.ModelColor)
async def modelcolor(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Размер модели (проверьте наличие на сайте!)", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(model_color=message.text)
    await states.LittleShoes.ModelSize.set()


@dp.message_handler(state=states.LittleShoes.ModelSize)
async def modelsize(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Стоимость модели (в ЕВРО!!!), просто число без доп.символов", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(model_size=message.text)
    await states.LittleShoes.ModelPrice.set()


@dp.message_handler(state=states.LittleShoes.ModelPrice)
async def modelprice(message: Message, state: FSMContext):
    data = await state.get_data()
    coeff = await quick_commands.select_coeff_3vetka()

    await message.delete()
    try:
        await dp.bot.edit_message_text(
            chat_id=message.from_user.id, 
            message_id=data['msg_id'], 
            text=f"Окончательная сумма к оплате:\n<b>{int(message.text)*coeff}RUB</b>\n\nВыберите ниже способ оплаты:", 
            reply_markup=main_keyboards.oplata_keyboard
        )
        await state.update_data(bonus=0, euro=message.text, model_price=str(int(message.text)*coeff))
        await states.LittleShoes.Screen.set()

    except ValueError:
        await dp.bot.edit_message_text(
            chat_id=message.from_user.id, 
            message_id=data['msg_id'], 
            text=f"Неправильный формат данных, введите число", 
            reply_markup=main_keyboards.cancel_keyboard
        )
    

@dp.callback_query_handler(text='tinkoff', state=states.LittleShoes.Screen)
async def tinkoff(call: CallbackQuery, state: FSMContext):
    await call.answer()
    text = await quick_commands.select_text_card()
    msg = await call.message.edit_text(
        text=text, 
        reply_markup=main_keyboards.cancel_keyboard,
        parse_mode='html'
    )
    
    await state.update_data(option='На карту', msg_id=msg.message_id)


@dp.callback_query_handler(text='SBP', state=states.LittleShoes.Screen)
async def sbp(call: CallbackQuery, state: FSMContext):
    await call.answer()
    text = await quick_commands.select_text_sbp()
    msg = await call.message.edit_text(
        text=text, 
        reply_markup=main_keyboards.cancel_keyboard,
        parse_mode='html'
    )
    
    await state.update_data(option='СБП', msg_id=msg.message_id)


@dp.callback_query_handler(text='bonus', state=states.Bosoobuv.Screen)
async def bonus(call: CallbackQuery, state: FSMContext):
    await call.answer()
    user = await quick_commands.select_user(call.from_user.id)
    if user.balance == 0:
        await call.message.edit_text(
            text='Ваш баланс пуст! 😔', 
            reply_markup=main_keyboards.back_keyboard,
            parse_mode='html'
        )
    else:
        await call.message.edit_text(
            text=f'Ваш баланс - {user.balance}RUB\n\nСписать в учёт покупки?', 
            reply_markup=main_keyboards.bonus_keyboard,
            parse_mode='html'
        )


@dp.callback_query_handler(text='back', state=states.Bosoobuv.Screen)
async def modelprice(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await call.message.edit_text(
        text=f"Окончательная сумма к оплате:\n<b>{data['model_price']}RUB</b>\n\nВыберите ниже способ оплаты:", 
        reply_markup=main_keyboards.oplata_keyboard
    )


@dp.callback_query_handler(text='yes', state=states.Bosoobuv.Screen)
async def modelprice(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    user = await quick_commands.select_user(call.from_user.id)
    if user.balance >= int(data['model_price']):
        await quick_commands.update_user_balance(call.from_user.id, user.balance-int(data['model_price']))

        await call.message.edit_text("""Ваши бонусы списаны!\n\nПоздравляем и БлагоДарим за покупку. 
👣 Далее мы сделаем все возможное, чтобы Ваш босоногий парк как можно быстрее пополнился еще одной прекрасной парой. 
Номер трека сообщим здесь же.

C любовью, Команда ALL Barefoot""", 
            reply_markup=main_keyboards.to_menu_keyboard
        )

        order = await quick_commands.add_order(
            user_id=call.from_user.id,
            time_created=datetime.now().strftime("%d.%m.%Y %H:%M"),
            link_name_number=data['link_name_number'], 
            name_user=data['name_user'], 
            address=data['address'], 
            phone=data['phone'], 
            model_name=data['model_name'], 
            model_color=data['model_color'], 
            model_size=data['model_size'], 
            model_price=data['model_price'],
            currency='USD',
            screen='Бонусы',
            bonus=str(data['bonus'])
        )

        coeff = await quick_commands.select_coeff_3vetka()
        worksheet = await check_google_sheets(agcm)
        col1 = await worksheet.col_values(2)
        await worksheet.update_cell(len(col1)+1, 2, datetime.now().strftime("%d.%m.%Y %H:%M"))
        await worksheet.update_cell(len(col1)+1, 3, order.id)
        await worksheet.update_cell(len(col1)+1, 4, data['name_user'])
        await worksheet.update_cell(len(col1)+1, 5, data['address'])
        await worksheet.update_cell(len(col1)+1, 6, data['phone'])
        await worksheet.update_cell(len(col1)+1, 8, data['link_name_number'])
        await worksheet.update_cell(len(col1)+1, 9, data['model_name'])
        await worksheet.update_cell(len(col1)+1, 10, data['model_color'])
        await worksheet.update_cell(len(col1)+1, 11, data['model_size'])
        await worksheet.update_cell(len(col1)+1, 13, data['euro'])
        await worksheet.update_cell(len(col1)+1, 14, coeff)
        await worksheet.update_cell(len(col1)+1, 15, int(data['euro'])*coeff)
        await worksheet.update_cell(len(col1)+1, 16, data['bonus'])
        if call.from_user.username is not None:
            await worksheet.update_cell(len(col1)+1, 23, f't.me/{call.from_user.username}')
        await worksheet.update_cell(len(col1)+1, 24, call.from_user.id)
        await worksheet.update_cell(len(col1)+1, 25, 'Бонусы')

        await state.finish()

    else:

        await call.message.edit_text( 
            text=f"Ваши бонусы списаны!", 
            reply_markup=main_keyboards.back_keyboard
        )

        await state.update_data(bonus=user.balance, model_price=str(int(data['model_price'])))
        await quick_commands.update_user_balance(0)


@dp.callback_query_handler(text='crypto', state=states.LittleShoes.Screen)
async def crypto(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    amount = int(data['model_price'])

    price = convert_currency_yahoofin('RUB', "USD", amount)
    price = round(price, 2)

    payment = Payment(price)
    link = await payment.init
    uuid = payment.uuid
    await state.update_data(uuid=uuid, link=link, amount=price)
    markup = await order_keyboards.markup_pay(link)

    await call.message.edit_text('''💸 Ваша ссылка для оплаты: {link}

Сумма к оплате: ~ ${price}
Ссылка действительна в течение 2-х часов.

⚠️ ВАЖНО! Необходимо отправить сумму не меньше указанной, иначе вы не получите подтверждение оплаты. Закладывайте расходы на комиссию.'''.format(link=link, price=price), reply_markup=markup)


@dp.callback_query_handler(text='paid', state=states.LittleShoes.Screen)
async def paid(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    payment = Payment(uuid=data['uuid'], amount=data['amount'])
    user = await quick_commands.select_user(call.from_user.id)

    status = await payment.check_payment()
    try:
        if status == 'created':
            await call.answer('❌ Оплата не найдена!', show_alert=True)
        elif status == 'partial':
            await call.answer('⚠️ Вы отправили недостаточно средств для оплаты, отправьте еще!', show_alert=True)
        elif status == 'paid':
            await call.message.edit_text("""Поздравляем и БлагоДарим за покупку. 
👣 Далее мы сделаем все возможное, чтобы Ваш босоногий парк как можно быстрее пополнился еще одной прекрасной парой. 
Номер трека сообщим здесь же.

C любовью, Команда ALL Barefoot""", 
                reply_markup=main_keyboards.to_menu_keyboard
            )

            order = await quick_commands.add_order(
                user_id=call.from_user.id,
                time_created=datetime.now().strftime("%d.%m.%Y %H:%M"),
                link_name_number=data['link_name_number'], 
                name_user=data['name_user'], 
                address=data['address'], 
                phone=data['phone'], 
                model_name=data['model_name'], 
                model_color=data['model_color'], 
                model_size=data['model_size'], 
                model_price=data['model_price'],
                currency='USD',
                screen='Через крипту',
                bonus=str(data['bonus'])
            )

            coeff = await quick_commands.select_coeff_3vetka()
            setts = await quick_commands.select_settings()
            percent = setts.percent

            user = await quick_commands.select_user(call.from_user.id)
            if user.referer is not None:
                referer = await quick_commands.select_user(user.referer)
                await quick_commands.update_user_balance(user.referer, referer.balance+round(int(data['euro'])*coeff*percent/100))

            worksheet = await check_google_sheets(agcm)
            col1 = await worksheet.col_values(2)
            await worksheet.update_cell(len(col1)+1, 2, datetime.now().strftime("%d.%m.%Y %H:%M"))
            await worksheet.update_cell(len(col1)+1, 3, order.id)
            await worksheet.update_cell(len(col1)+1, 4, data['name_user'])
            await worksheet.update_cell(len(col1)+1, 5, data['address'])
            await worksheet.update_cell(len(col1)+1, 6, data['phone'])
            await worksheet.update_cell(len(col1)+1, 8, data['link_name_number'])
            await worksheet.update_cell(len(col1)+1, 9, data['model_name'])
            await worksheet.update_cell(len(col1)+1, 10, data['model_color'])
            await worksheet.update_cell(len(col1)+1, 11, data['model_size'])
            await worksheet.update_cell(len(col1)+1, 13, data['euro'])
            await worksheet.update_cell(len(col1)+1, 14, coeff)
            await worksheet.update_cell(len(col1)+1, 15, int(data['euro'])*coeff)
            await worksheet.update_cell(len(col1)+1, 16, data['bonus'])
            if call.from_user.username is not None:
                await worksheet.update_cell(len(col1)+1, 23, f't.me/{call.from_user.username}')
            await worksheet.update_cell(len(col1)+1, 24, call.from_user.id)
            await worksheet.update_cell(len(col1)+1, 25, 'Крипта')

            await state.finish()

    except Exception as err:
        await dp.bot.send_message(admin_id[0], f'{status}')
        await dp.bot.send_message(admin_id[0], f'{err}')


@dp.message_handler(state=states.LittleShoes.Screen, content_types=ContentType.PHOTO)
async def photo_screen(message: Message, state: FSMContext):
    data = await state.get_data()

    await dp.bot.delete_message(chat_id=message.from_user.id, message_id=data['msg_id'])
    await message.delete()

    await message.answer(
        text=f"""Поздравляем и БлагоДарим за покупку. 
👣 Далее мы сделаем все возможное, чтобы Ваш босоногий парк как можно быстрее пополнился еще одной прекрасной парой. 
Номер трека сообщим здесь же.

C любовью, Команда ALL Barefoot""", 
        reply_markup=main_keyboards.to_menu_keyboard
    )

    order = await quick_commands.add_order(
        user_id=message.from_user.id,
        time_created=datetime.now().strftime("%d.%m.%Y %H:%M"),
        link_name_number=data['link_name_number'], 
        name_user=data['name_user'], 
        address=data['address'], 
        phone=data['phone'], 
        model_name=data['model_name'], 
        model_color=data['model_color'], 
        model_size=data['model_size'], 
        model_price=data['model_price'],
        currency='EUR',
        screen=message.photo[-1].file_id,
        bonus=str(data['bonus'])
    )

    await dp.bot.send_photo(admin_id[1], message.photo[-1].file_id, f'Номер заказа: {order.id}\nИмя: {data["name_user"]}\nК оплате: {data["model_price"]}RUB\nСпособ оплаты: {data["option"]}')

    coeff = await quick_commands.select_coeff_3vetka()
    setts = await quick_commands.select_settings()
    percent = setts.percent

    user = await quick_commands.select_user(message.from_user.id)
    if user.referer is not None:
        referer = await quick_commands.select_user(user.referer)
        await quick_commands.update_user_balance(user.referer, referer.balance+round(int(data['euro'])*coeff*percent/100))

    worksheet = await check_google_sheets(agcm)
    col1 = await worksheet.col_values(2)
    await worksheet.update_cell(len(col1)+1, 2, datetime.now().strftime("%d.%m.%Y %H:%M"))
    await worksheet.update_cell(len(col1)+1, 3, order.id)
    await worksheet.update_cell(len(col1)+1, 4, data['name_user'])
    await worksheet.update_cell(len(col1)+1, 5, data['address'])
    await worksheet.update_cell(len(col1)+1, 6, data['phone'])
    await worksheet.update_cell(len(col1)+1, 8, data['link_name_number'])
    await worksheet.update_cell(len(col1)+1, 9, data['model_name'])
    await worksheet.update_cell(len(col1)+1, 10, data['model_color'])
    await worksheet.update_cell(len(col1)+1, 11, data['model_size'])
    await worksheet.update_cell(len(col1)+1, 13, data['euro'])
    await worksheet.update_cell(len(col1)+1, 14, coeff)
    await worksheet.update_cell(len(col1)+1, 15, int(data['euro'])*coeff)
    await worksheet.update_cell(len(col1)+1, 16, data['bonus'])
    if message.from_user.username is not None:
        await worksheet.update_cell(len(col1)+1, 23, f't.me/{message.from_user.username}')
    await worksheet.update_cell(len(col1)+1, 24, message.from_user.id)
    await worksheet.update_cell(len(col1)+1, 25, f"t.me/allbarefoot_bot?start=screen{order.id}")



# ------------------------------------- F A R E -------------------------------------


@dp.callback_query_handler(text='fare')
async def fare(call: CallbackQuery, state: FSMContext):
    await call.answer()
    text = await quick_commands.select_text_4vetka()
    msg = await call.message.edit_text(
        text=text, 
        reply_markup=main_keyboards.to_menu_keyboard, 
        parse_mode='html'
    )
    await state.update_data(msg_id=msg.message_id)
    await states.Fare.LinkNameNumber.set()


@dp.message_handler(state=states.Fare.LinkNameNumber)
async def linknameumber(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Ваше имя и фамилия ЛАТИНСКИМИ буквами для отправки посылки", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(link_name_number=message.text)
    await states.Fare.NameUser.set()


@dp.message_handler(state=states.Fare.NameUser)
async def nameuser(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Адрес доставки ЛАТИНСКИМИ буквами (улица, номер дома/квартиры, город, область, индекс). Проверьте корректное заполнение адреса", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(name_user=message.text)
    await states.Fare.Address.set()


@dp.message_handler(state=states.Fare.Address)
async def address(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Ваш номер телефона", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(address=message.text)
    await states.Fare.Phone.set()


@dp.message_handler(state=states.Fare.Phone)
async def phone(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Название модели, которую хотите приобрести (для проверки и во избежание ошибки)", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(phone=message.text)
    await states.Fare.ModelName.set()


@dp.message_handler(state=states.Fare.ModelName)
async def modelname(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Цвет модели (как указано на сайте)", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(model_name=message.text)
    await states.Fare.ModelColor.set()


@dp.message_handler(state=states.Fare.ModelColor)
async def modelcolor(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Размер модели (проверьте наличие на сайте!)", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(model_color=message.text)
    await states.Fare.ModelSize.set()


@dp.message_handler(state=states.Fare.ModelSize)
async def modelsize(message: Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=data['msg_id'], 
        text="Стоимость модели (в ЕВРО!!!), просто число без доп.символов", 
        reply_markup=main_keyboards.cancel_keyboard
    )

    await state.update_data(model_size=message.text)
    await states.Fare.ModelPrice.set()


@dp.message_handler(state=states.Fare.ModelPrice)
async def modelprice(message: Message, state: FSMContext):
    data = await state.get_data()
    coeff = await quick_commands.select_coeff_4vetka()

    await message.delete()
    try:
        await dp.bot.edit_message_text(
            chat_id=message.from_user.id, 
            message_id=data['msg_id'], 
            text=f"Окончательная сумма к оплате:\n<b>{int(message.text)*coeff}RUB</b>\n\nВыберите ниже способ оплаты:", 
            reply_markup=main_keyboards.oplata_keyboard
        )
        await state.update_data(bonus=0, euro=message.text, model_price=str(int(message.text)*coeff))
        await states.Fare.Screen.set()

    except ValueError:
        await dp.bot.edit_message_text(
            chat_id=message.from_user.id, 
            message_id=data['msg_id'], 
            text=f"Неправильный формат данных, введите число", 
            reply_markup=main_keyboards.cancel_keyboard
        )
    

@dp.callback_query_handler(text='tinkoff', state=states.Fare.Screen)
async def tinkoff(call: CallbackQuery, state: FSMContext):
    await call.answer()
    text = await quick_commands.select_text_card()
    msg = await call.message.edit_text(
        text=text, 
        reply_markup=main_keyboards.cancel_keyboard,
        parse_mode='html'
    )
    
    await state.update_data(option='На карту', msg_id=msg.message_id)


@dp.callback_query_handler(text='SBP', state=states.Fare.Screen)
async def sbp(call: CallbackQuery, state: FSMContext):
    await call.answer()
    text = await quick_commands.select_text_sbp()
    msg = await call.message.edit_text(
        text=text, 
        reply_markup=main_keyboards.cancel_keyboard,
        parse_mode='html'
    )
    
    await state.update_data(option='СБП', msg_id=msg.message_id)


@dp.callback_query_handler(text='bonus', state=states.Bosoobuv.Screen)
async def bonus(call: CallbackQuery, state: FSMContext):
    await call.answer()
    user = await quick_commands.select_user(call.from_user.id)
    if user.balance == 0:
        await call.message.edit_text(
            text='Ваш баланс пуст! 😔', 
            reply_markup=main_keyboards.back_keyboard,
            parse_mode='html'
        )
    else:
        await call.message.edit_text(
            text=f'Ваш баланс - {user.balance}RUB\n\nСписать в учёт покупки?', 
            reply_markup=main_keyboards.bonus_keyboard,
            parse_mode='html'
        )


@dp.callback_query_handler(text='back', state=states.Bosoobuv.Screen)
async def modelprice(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await call.message.edit_text(
        text=f"Окончательная сумма к оплате:\n<b>{data['model_price']}RUB</b>\n\nВыберите ниже способ оплаты:", 
        reply_markup=main_keyboards.oplata_keyboard
    )


@dp.callback_query_handler(text='yes', state=states.Bosoobuv.Screen)
async def modelprice(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    user = await quick_commands.select_user(call.from_user.id)
    if user.balance >= int(data['model_price']):
        await quick_commands.update_user_balance(call.from_user.id, user.balance-int(data['model_price']))

        await call.message.edit_text("""Ваши бонусы списаны!\n\nПоздравляем и БлагоДарим за покупку. 
👣 Далее мы сделаем все возможное, чтобы Ваш босоногий парк как можно быстрее пополнился еще одной прекрасной парой. 
Номер трека сообщим здесь же.

C любовью, Команда ALL Barefoot""", 
            reply_markup=main_keyboards.to_menu_keyboard
        )

        order = await quick_commands.add_order(
            user_id=call.from_user.id,
            time_created=datetime.now().strftime("%d.%m.%Y %H:%M"),
            link_name_number=data['link_name_number'], 
            name_user=data['name_user'], 
            address=data['address'], 
            phone=data['phone'], 
            model_name=data['model_name'], 
            model_color=data['model_color'], 
            model_size=data['model_size'], 
            model_price=data['model_price'],
            currency='USD',
            screen='Бонусы',
            bonus=str(data['bonus'])
        )

        coeff = await quick_commands.select_coeff_4vetka()
        worksheet = await check_google_sheets(agcm)
        col1 = await worksheet.col_values(2)
        await worksheet.update_cell(len(col1)+1, 2, datetime.now().strftime("%d.%m.%Y %H:%M"))
        await worksheet.update_cell(len(col1)+1, 3, order.id)
        await worksheet.update_cell(len(col1)+1, 4, data['name_user'])
        await worksheet.update_cell(len(col1)+1, 5, data['address'])
        await worksheet.update_cell(len(col1)+1, 6, data['phone'])
        await worksheet.update_cell(len(col1)+1, 8, data['link_name_number'])
        await worksheet.update_cell(len(col1)+1, 9, data['model_name'])
        await worksheet.update_cell(len(col1)+1, 10, data['model_color'])
        await worksheet.update_cell(len(col1)+1, 11, data['model_size'])
        await worksheet.update_cell(len(col1)+1, 13, data['euro'])
        await worksheet.update_cell(len(col1)+1, 14, coeff)
        await worksheet.update_cell(len(col1)+1, 15, int(data['euro'])*coeff)
        await worksheet.update_cell(len(col1)+1, 16, data['bonus'])
        if call.from_user.username is not None:
            await worksheet.update_cell(len(col1)+1, 23, f't.me/{call.from_user.username}')
        await worksheet.update_cell(len(col1)+1, 24, call.from_user.id)
        await worksheet.update_cell(len(col1)+1, 25, 'Бонусы')

        await state.finish()

    else:

        await call.message.edit_text( 
            text=f"Ваши бонусы списаны!", 
            reply_markup=main_keyboards.back_keyboard
        )

        await state.update_data(model_price=str(int(data['model_price'])-user.balance))
        await quick_commands.update_user_balance(0)


@dp.callback_query_handler(text='crypto', state=states.Fare.Screen)
async def crypto(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    amount = int(data['model_price'])

    price = convert_currency_yahoofin('RUB', "USD", amount)
    price = round(price, 2)

    payment = Payment(price)
    link = await payment.init
    uuid = payment.uuid
    await state.update_data(uuid=uuid, link=link, amount=price)
    markup = await order_keyboards.markup_pay(link)

    await call.message.edit_text('''💸 Ваша ссылка для оплаты: {link}

Сумма к оплате: ~ ${price}
Ссылка действительна в течение 2-х часов.

⚠️ ВАЖНО! Необходимо отправить сумму не меньше указанной, иначе вы не получите подтверждение оплаты. Закладывайте расходы на комиссию.'''.format(link=link, price=price), reply_markup=markup)


@dp.callback_query_handler(text='paid', state=states.Fare.Screen)
async def paid(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    payment = Payment(uuid=data['uuid'], amount=data['amount'])
    user = await quick_commands.select_user(call.from_user.id)

    status = await payment.check_payment()
    try:
        if status == 'created':
            await call.answer('❌ Оплата не найдена!', show_alert=True)
        elif status == 'partial':
            await call.answer('⚠️ Вы отправили недостаточно средств для оплаты, отправьте еще!', show_alert=True)
        elif status == 'paid':
            await call.message.edit_text("""Поздравляем и БлагоДарим за покупку. 
👣 Далее мы сделаем все возможное, чтобы Ваш босоногий парк как можно быстрее пополнился еще одной прекрасной парой. 
Номер трека сообщим здесь же.

C любовью, Команда ALL Barefoot""", 
                reply_markup=main_keyboards.to_menu_keyboard
            )

            order = await quick_commands.add_order(
                user_id=call.from_user.id,
                time_created=datetime.now().strftime("%d.%m.%Y %H:%M"),
                link_name_number=data['link_name_number'], 
                name_user=data['name_user'], 
                address=data['address'], 
                phone=data['phone'], 
                model_name=data['model_name'], 
                model_color=data['model_color'], 
                model_size=data['model_size'], 
                model_price=data['model_price'],
                currency='USD',
                screen='Через крипту',
                bonus=str(data['bonus'])
            )

            coeff = await quick_commands.select_coeff_4vetka()
            setts = await quick_commands.select_settings()
            percent = setts.percent

            user = await quick_commands.select_user(call.from_user.id)
            if user.referer is not None:
                referer = await quick_commands.select_user(user.referer)
                await quick_commands.update_user_balance(user.referer, referer.balance+round(int(data['euro'])*coeff*percent/100))            

            worksheet = await check_google_sheets(agcm)
            col1 = await worksheet.col_values(2)
            await worksheet.update_cell(len(col1)+1, 2, datetime.now().strftime("%d.%m.%Y %H:%M"))
            await worksheet.update_cell(len(col1)+1, 3, order.id)
            await worksheet.update_cell(len(col1)+1, 4, data['name_user'])
            await worksheet.update_cell(len(col1)+1, 5, data['address'])
            await worksheet.update_cell(len(col1)+1, 6, data['phone'])
            await worksheet.update_cell(len(col1)+1, 8, data['link_name_number'])
            await worksheet.update_cell(len(col1)+1, 9, data['model_name'])
            await worksheet.update_cell(len(col1)+1, 10, data['model_color'])
            await worksheet.update_cell(len(col1)+1, 11, data['model_size'])
            await worksheet.update_cell(len(col1)+1, 13, data['euro'])
            await worksheet.update_cell(len(col1)+1, 14, coeff)
            await worksheet.update_cell(len(col1)+1, 15, int(data['euro'])*coeff)
            await worksheet.update_cell(len(col1)+1, 16, data['bonus'])
            if call.from_user.username is not None:
                await worksheet.update_cell(len(col1)+1, 23, f't.me/{call.from_user.username}')
            await worksheet.update_cell(len(col1)+1, 24, call.from_user.id)
            await worksheet.update_cell(len(col1)+1, 25, 'Крипта')

            await state.finish()

    except Exception as err:
        await dp.bot.send_message(admin_id[0], f'{status}')
        await dp.bot.send_message(admin_id[0], f'{err}')


@dp.message_handler(state=states.Fare.Screen, content_types=ContentType.PHOTO)
async def photo_screen(message: Message, state: FSMContext):
    data = await state.get_data()

    await dp.bot.delete_message(chat_id=message.from_user.id, message_id=data['msg_id'])
    await message.delete()

    await message.answer(
        text=f"""Поздравляем и БлагоДарим за покупку. 
👣 Далее мы сделаем все возможное, чтобы Ваш босоногий парк как можно быстрее пополнился еще одной прекрасной парой. 
Номер трека сообщим здесь же.

C любовью, Команда ALL Barefoot""", 
        reply_markup=main_keyboards.to_menu_keyboard
    )

    order = await quick_commands.add_order(
        user_id=message.from_user.id,
        time_created=datetime.now().strftime("%d.%m.%Y %H:%M"),
        link_name_number=data['link_name_number'], 
        name_user=data['name_user'], 
        address=data['address'], 
        phone=data['phone'], 
        model_name=data['model_name'], 
        model_color=data['model_color'], 
        model_size=data['model_size'], 
        model_price=data['model_price'],
        currency='EUR',
        screen=message.photo[-1].file_id,
        bonus=str(data['bonus'])
    )

    await dp.bot.send_photo(admin_id[1], message.photo[-1].file_id, f'Номер заказа: {order.id}\nИмя: {data["name_user"]}\nК оплате: {data["model_price"]}RUB\nСпособ оплаты: {data["option"]}')

    coeff = await quick_commands.select_coeff_4vetka()
    setts = await quick_commands.select_settings()
    percent = setts.percent

    user = await quick_commands.select_user(message.from_user.id)
    if user.referer is not None:
        referer = await quick_commands.select_user(user.referer)
        await quick_commands.update_user_balance(user.referer, referer.balance+round(int(data['euro'])*coeff*percent/100))

    worksheet = await check_google_sheets(agcm)
    col1 = await worksheet.col_values(2)
    await worksheet.update_cell(len(col1)+1, 2, datetime.now().strftime("%d.%m.%Y %H:%M"))
    await worksheet.update_cell(len(col1)+1, 3, order.id)
    await worksheet.update_cell(len(col1)+1, 4, data['name_user'])
    await worksheet.update_cell(len(col1)+1, 5, data['address'])
    await worksheet.update_cell(len(col1)+1, 6, data['phone'])
    await worksheet.update_cell(len(col1)+1, 8, data['link_name_number'])
    await worksheet.update_cell(len(col1)+1, 9, data['model_name'])
    await worksheet.update_cell(len(col1)+1, 10, data['model_color'])
    await worksheet.update_cell(len(col1)+1, 11, data['model_size'])
    await worksheet.update_cell(len(col1)+1, 13, data['euro'])
    await worksheet.update_cell(len(col1)+1, 14, coeff)
    await worksheet.update_cell(len(col1)+1, 15, int(data['euro'])*coeff)
    await worksheet.update_cell(len(col1)+1, 16, data['bonus'])
    if message.from_user.username is not None:
        await worksheet.update_cell(len(col1)+1, 23, f't.me/{message.from_user.username}')
    await worksheet.update_cell(len(col1)+1, 24, message.from_user.id)
    await worksheet.update_cell(len(col1)+1, 25, f"t.me/allbarefoot_bot?start=screen{order.id}")


# ----------------------------- О Т П Р А В И Т Ь   Т Р Е К -----------------------------


@dp.callback_query_handler(text_contains='sendtrack_')
async def sendtrack(call: CallbackQuery, state: FSMContext):
    user_id = call.data.split('_')[1] 

    msg = await call.message.edit_text('Пришлите трек этого заказа, чтобы переслать его пользователю')
    await state.update_data(user_id=user_id, msg_id=msg.message_id)
    await states.Command.SendTrack.set()


@dp.message_handler(state=states.Command.SendTrack)
async def photo_screen(message: Message, state: FSMContext):
    data = await state.get_data()

    await dp.bot.send_message(int(data['user_id']), f'Трек заказа:\n\n<code>{message.text}</code>', parse_mode='html')
    await message.delete()
    await dp.bot.edit_message_text(
        chat_id=message.from_user.id, 
        message_id=int(data['msg_id']), 
        text="Трек отправлен"
    )

    await state.finish()


# ------------------------------- П А Р Т Н Ё Р К А -------------------------------------


@dp.callback_query_handler(text='partnerka')
async def partnerka(call: CallbackQuery, state: FSMContext):
    await call.answer()
    user = await quick_commands.select_user(call.from_user.id)
    all_users = await quick_commands.select_all_users()

    referals = 0
    money = 0
    balance = user.balance
    zarabotok = user.zarabotok
    setts = await quick_commands.select_settings()
    percent = setts.percent
    if user.percent is not None:
        percent = user.percent
    for i in range(len(all_users)):
        if all_users[i].referer == call.from_user.id:
            referals += 1

    orders = await quick_commands.select_orders_by_user_id(call.from_user.id)


    text=f"""<b>🤝 Партнёрская программа</b>

Зовите друзей и <b>получайте %</b> от их покупок на бонусный счёт.
Бонусы можно тратить на покупки.

https://telegra.ph/PARTNYORSKAYA-PROGRAMMA-01-31

🖖 <b>Вы пригласили:</b> {referals} чел.
💰 <b>Вы заработали:</b> {zarabotok}RUB
🍏 <b>Баланс баллов:</b> {balance}RUB
💯 <b>Ваш процент от покупок:</b> {percent}%"""

    if (user.bloger == True) or (len(orders) > 0):
        text += f"""\n\n👇 <b>Ваша ссылка для приглашений:</b>

<code>t.me/allbarefoot_bot?start={call.from_user.id}</code>

(нажмите на неё, чтобы скопировать)"""

    await call.message.edit_text(
        text, 
        reply_markup=main_keyboards.to_menu_keyboard, 
        parse_mode='html'
    )


# ---------------------------- И С Т О Р И Я   З А К А З О В -------------------------------


@dp.callback_query_handler(text='my_orders')
async def partnerka(call: CallbackQuery, state: FSMContext):
    await call.answer()
    orders = await quick_commands.select_orders_by_user_id(call.from_user.id)
    if len(orders) == 0:
        await call.message.edit_text(
            text=f"""Заказов ещё не было""", 
            reply_markup=main_keyboards.to_menu_keyboard, 
            parse_mode='html'
        )
    else:
        markup = await main_keyboards.orders_keyboard(call.from_user.id)
        await call.message.edit_text(
            text=f"""💚 <b>Кол-во заказов:</b> {len(orders)}\n\n<b>Список всех заказов 👇</b>""", 
            reply_markup=markup, 
            parse_mode='html'
        )


@dp.callback_query_handler(text_contains='order;')
async def partnerka(call: CallbackQuery, state: FSMContext):
    await call.answer()
    order_id = int(call.data.split(';')[1])
    order = await quick_commands.select_order(order_id)
    await call.message.answer(
        f'''<b>№{order_id}</b> | 💚 | {order.time_created}


<b>Состав заказа:</b>
<b>Название модели:</b> {order.model_name}
<b>Цвет:</b> {order.model_color}
<b>Размер:</b> {order.model_size}
<b>Цена:</b> {order.model_price} RUB

<b>Имя:</b> {order.name_user}
<b>Адрес:</b> {order.address}
<b>Телефон:</b> {order.phone}''', reply_markup=main_keyboards.close_keyboard)


@dp.callback_query_handler(text='xxx')
async def partnerka(call: CallbackQuery, state: FSMContext):
    await call.answer()


# ------------------------------------------------------------------------------------

@dp.callback_query_handler(text='service_info')
async def partnerka(call: CallbackQuery, state: FSMContext):
    await call.answer()
    text = '''<b>ALLBarefoot это европейская босоногая обувь по ценам производителя, без переплат. 
Стоимость окончательная, включает доставку, никаких доплат после. Приоритетная доставка и огромный выбор.

КАК РАБОТАЕТ</b> ЧАТ-БОТ ALLBarefoot👣

🛒 Создаете заказ прямо в боте
↓
📮 Вводите данные для доставки (<i>таможенная декларация — наша забота</i>)
↓
💰Бот рассчитывает стоимость (<i>или вводите из спец.предложения</i>)
↓
💳 Оплачиваете в рублях СБП, Тинькоф или USDT криптовалютой
↓
📤 Спустя 3-7 дней получаете здесь же трек для отслеживания
↓
📦 Забираете посылку в почтовом отделении
<b>Примерный срок доставки: 3-4 недели</b>
<a href="https://telegra.ph/Bazovaya-informaciya-01-31">Подробнее об условиях заказа тут.</a>

📣<b>Все главные новости, акции и закупки в</b> <a href="https://t.me/allbarefoot">нашем ТГ канале</a>. Не забудьте подписаться!
🤝Присоединиться к босоногому сообществу, увидеть реальные фото, видео, замеры, <b>опыт и советы бывалых</b> <a href="https://t.me/allbarefoot_ru">можно ТУТ.</a>'''

    await call.message.edit_text(text, reply_markup=main_keyboards.to_menu_keyboard, parse_mode='html', disable_web_page_preview=True)