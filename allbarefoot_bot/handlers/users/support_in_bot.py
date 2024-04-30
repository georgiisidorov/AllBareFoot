import datetime
import logging
import random
import json
import docx
import io

from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InputFile, Message, CallbackQuery, ContentType, MediaGroup, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, PreCheckoutQuery
from aiogram.types.input_media import InputMediaPhoto
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, BadRequest
import asyncio

from data.config import admin_id
from loader import dp
from states import states
from utils.db_api import quick_commands
from keyboards.inline import main_keyboards
from keyboards.default.keyboards import contact_keyboard, back_keyboard, dialog_keyboard


@dp.callback_query_handler(text='support')
async def support(call: CallbackQuery, state: FSMContext):
	await call.answer()
	await call.message.edit_text('Ожидайте администратора...')
	await states.States.TalkingUser.set()
	fsm = dp.current_state(chat=admin_id[1], user=admin_id[1])

	markup = await main_keyboards.user_info_keyboard(call.from_user.id, call.from_user.full_name)

	if await fsm.get_state() is not None:
		while True:
			if await fsm.get_state() is None:
				await dp.bot.send_message(
					admin_id[1], 
					f'<i>Установлена связь с клиентом <b>ID{call.from_user.id}</b></i>',
					reply_markup=markup
				)
				await fsm.update_data(client_id=call.from_user.id)
				await fsm.set_state(states.States.TalkingAdmin)
				break
			await asyncio.sleep(5)
	else:
		await dp.bot.send_message(
			admin_id[1], 
			f'<i>Установлена связь с клиентом <b>ID{call.from_user.id}</b></i>',
			reply_markup=markup
		)
		await fsm.update_data(client_id=call.from_user.id)
		await fsm.set_state(states.States.TalkingAdmin)


@dp.message_handler(text='Завершить диалог ❎', state=states.States.TalkingAdmin)
async def button(message: Message, state: FSMContext):
	await message.delete()
	data = await state.get_data()
	await state.finish()
	fsm = dp.current_state(chat=data['client_id'], user=data['client_id'])
	await fsm.finish()
	await dp.bot.send_message(data['client_id'], 'Диалог с администратором завершен, нажмите /start для открытия меню')
	await message.answer('Диалог с клиентом завершен, нажмите /start для открытия меню', reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query_handler(text='close_dialog', state=states.States.TalkingAdmin)
async def support(call: CallbackQuery, state: FSMContext):
	await call.answer()
	await call.message.delete()
	data = await state.get_data()
	await state.finish()
	fsm = dp.current_state(chat=data['client_id'], user=data['client_id'])
	await fsm.finish()
	await dp.bot.send_message(data['client_id'], 'Диалог с администратором завершен, нажмите /start для открытия меню')
	await call.message.answer('Диалог с клиентом завершен, нажмите /start для открытия меню', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(content_types=types.ContentType.ANY, state=states.Command.TestMailing)
async def mailing_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    call_msg = data.get("call_msg")
    await message.delete()
    if message.text is not None:
        await state.update_data(text=message.html_text)
        markup = main_keyboards.confirm_keyboard
        await dp.bot.edit_message_text(
            'Подтверждаете выбранное сообщение?',
            chat_id=message.chat.id,
            message_id=call_msg,
            reply_markup=markup
        )
        await states.Command.TestMailingConfirm.set()

    elif message.photo != []:
        await state.update_data(photo=message.photo[-1].file_id, caption=message.caption)
        markup = main_keyboards.confirm_keyboard
        await dp.bot.edit_message_text(
            'Подтверждаете выбранное сообщение?',
            chat_id=message.chat.id,
            message_id=call_msg,
            reply_markup=markup
        )
        await states.Command.TestMailingConfirm.set()

    else:
        markup = main_keyboards.to_menu_keyboard
        await dp.bot.edit_message_text(
            'Сообщение не подходит под формат (одна картинка с подписью или текст). КОМАНДА ОТМЕНЕНА',
            chat_id=message.chat.id,
            message_id=call_msg,
            reply_markup=markup
        )
        await state.finish()


@dp.message_handler(state=states.States.TalkingAdmin)
async def button(message: Message, state: FSMContext):
	data = await state.get_data()
	time = datetime.datetime.now().strftime('%d.%m.%y %H:%M:%S')
	client_id = data['client_id']

	f = open(f'/root/allbarefoot_bot/data/{client_id}.txt', 'a', encoding="utf-8")
	f.write(f'Администратор {time}\n')
	f.write(f'{message.text}\n\n')
	f.close()

	await dp.bot.send_message(client_id, message.text)


@dp.message_handler(content_types=types.ContentType.ANY, state=states.States.TalkingUser)
async def button(message: Message, state: FSMContext):
	time = datetime.datetime.now().strftime('%d.%m.%y %H:%M:%S')

	f = open(f'/root/allbarefoot_bot/data/{message.from_user.id}.txt', 'a', encoding="utf-8")
	f.write(f'Пользователь {time}\n')

	if message.text is not None:
		await dp.bot.send_message(
			admin_id[1], 
			message.text, 
			reply_markup=dialog_keyboard
		)
		f.write(f'{message.text}\n\n')
	elif message.photo != []:
		await dp.bot.send_photo(
			admin_id[1], 
			photo=message.photo[-1].file_id, 
			caption=message.caption, 	
			reply_markup=dialog_keyboard
		)
		f.write(f'Пользователь прислал фото\n\n')

	f.close()


@dp.callback_query_handler(text='support_2')
async def support_2(call: CallbackQuery, state: FSMContext):
	await call.answer()
	msg = await call.message.edit_text('Напишите ID клиента целым числом', reply_markup=main_keyboards.cancel_keyboard)
	await state.update_data(msg_id=msg.message_id)
	await states.States.TalkingClientID.set()


@dp.message_handler(state=states.States.TalkingClientID)
async def button(message: Message, state: FSMContext):
	data = await state.get_data()
	try:
		id_client = int(message.text)
		user = await quick_commands.select_user(id_client)
		if user is not None:
			await message.delete()
			await dp.bot.delete_message(
				chat_id=message.chat.id,
				message_id=data['msg_id']
			)
			await message.answer(
				f'<i>Установлена связь с клиентом <b>ID{id_client}</b></i>',
				reply_markup=dialog_keyboard
			)
			await dp.bot.send_message(
				id_client,
				f'<i>Установлена связь с администратором</i>'
			)
			await states.States.TalkingAdmin.set()
			fsm = dp.current_state(chat=id_client, user=id_client)
			await fsm.set_state(states.States.TalkingUser)
			await state.update_data(client_id=id_client)

		else:
			await message.delete()
			await dp.bot.edit_message_text(
				'Такого пользователя не существует, будьте внимательны! Попробуйте ввести ID ещё раз',
				chat_id=message.chat.id,
				message_id=data['msg_id'],
				reply_markup=main_keyboards.cancel_keyboard
			)
	except ValueError:
		await message.delete()
		await dp.bot.edit_message_text(
			f'Неверный формат данных, введите целое число',
			chat_id=message.chat.id,
			message_id=data['msg_id'],
			reply_markup=main_keyboards.cancel_keyboard
		)

	
@dp.callback_query_handler(text_contains='info_', state=states.States.TalkingAdmin)
async def support_2(call: CallbackQuery, state: FSMContext):
	await call.answer()
	user_id = int(call.data.split('_')[1])
	fullname = call.data.split('_')[2]
	user = await quick_commands.select_user(user_id)
	orders = await quick_commands.select_orders_by_user_id(user_id)
	if len(orders) > 0:
		markup = await main_keyboards.orders_keyboard_without_menu(user_id)
		await call.message.answer(
			text=f"""💚 <b>Кол-во заказов:</b> {len(orders)}\n\n<b>Список всех заказов 👇</b>""",
			reply_markup=markup,
			parse_mode='html'
		)
	else:
		await call.message.answer('Заказов ещё не было.', reply_markup=main_keyboards.close_keyboard, parse_mode='html')


@dp.callback_query_handler(text='close_info', state='*')
async def support_2(call: CallbackQuery, state: FSMContext):
	await call.message.delete()


@dp.callback_query_handler(text_contains='doc_', state=states.States.TalkingAdmin)
async def support_2(call: CallbackQuery, state: FSMContext):
	await call.answer()
	user_id = call.data.split('_')[1]

	try:
		with open(f'/root/allbarefoot_bot/data/{user_id}.txt', "rb") as fh:
			buf = io.BytesIO(fh.read())

		doc = InputFile(buf, filename='История переписки.txt')
		markup = main_keyboards.close_keyboard
		await call.message.answer_document(doc, reply_markup=markup)
	except FileNotFoundError:
		markup = main_keyboards.close_keyboard
		await call.message.answer('С данным пользователем Вы ещё не переписывались', reply_markup=markup)
