import datetime
import logging
import random
import docx

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType, MediaGroup, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, PreCheckoutQuery
from aiogram.types.input_media import InputMediaPhoto
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, BadRequest
import asyncio

from data import config
from keyboards.inline import main_keyboards
from loader import dp
from utils.db_api import quick_commands


@dp.message_handler(commands=['start'], state='*')
async def start(message: Message, state: FSMContext):
	await state.finish()

	try:
		args = message.get_args()
		if 'screen' in args:
			order_id = args[6:]
			order = await quick_commands.select_order(int(order_id))
			await message.answer_photo(order.screen, reply_markup=main_keyboards.close_keyboard)
		else:
			if int(args) != message.from_user.id:
				await quick_commands.add_user(user_id=message.from_user.id, username=message.from_user.username, referer=int(args))
			else:
				pass

			if message.from_user.id in config.admin_id:
				await message.answer(
					'Меню администратора AllBareFoot 👾', 
					reply_markup=main_keyboards.VIP_menu_keyboard
				)
			else:
				markup = await main_keyboards.menu_keyboard()
				await message.answer(
					'Приветствуем Вас, босоногий человек!\n\nhttps://telegra.ph/Bazovaya-informaciya-01-31\n\nЕсли готовы сделать заказ, жмите кнопку ниже 👇\n\n<b>Если бот тормозит, нажмите /start</b>', 
					reply_markup=markup,
					parse_mode='html',
					disable_web_page_preview=True
				)
	

	except Exception:
		await quick_commands.add_user(user_id=message.from_user.id, username=message.from_user.username, referer=None)

		if message.from_user.id in config.admin_id:
			await message.answer(
				'Меню администратора AllBareFoot 👾', 
				reply_markup=main_keyboards.VIP_menu_keyboard
			)
		else:
			markup = await main_keyboards.menu_keyboard()
			await message.answer(
				'Приветствуем Вас, босоногий человек!\n\nhttps://telegra.ph/Bazovaya-informaciya-01-31\n\nЕсли готовы сделать заказ, жмите кнопку ниже 👇\n\n<b>Если бот тормозит, нажмите /start</b>', 
				reply_markup=markup,
				parse_mode='html',
				disable_web_page_preview=True
			)
	

@dp.callback_query_handler(text='menu', state='*')
async def button(call: CallbackQuery, state: FSMContext):
	await call.answer()
	await state.finish()

	if call.from_user.id in config.admin_id:
		await call.message.delete()
		await call.message.answer(
			'Меню администратора AllBareFoot 👾', 
			reply_markup=main_keyboards.VIP_menu_keyboard
		)
	else:
		await call.message.delete()
		markup = await main_keyboards.menu_keyboard()
		await call.message.answer(
			'Приветствуем Вас, босоногий человек!\n\nhttps://telegra.ph/Bazovaya-informaciya-01-31\n\nЕсли готовы сделать заказ, жмите кнопку ниже 👇\n\n<b>Если бот тормозит, нажмите /start</b>', 
			reply_markup=markup,
			parse_mode='html',
			disable_web_page_preview=True
		)


@dp.callback_query_handler(text='cancel', state='*')
async def button(call: CallbackQuery, state: FSMContext):
	await call.answer()
	await state.finish()

	if call.from_user.id in config.admin_id:
		await call.message.delete()
		await call.message.answer(
			'Меню администратора AllBareFoot 👾', 
			reply_markup=main_keyboards.VIP_menu_keyboard
		)
	else:
		await call.message.delete()
		markup = await main_keyboards.menu_keyboard()
		await call.message.answer(
			'Приветствуем Вас, босоногий человек!\n\nhttps://telegra.ph/Bazovaya-informaciya-01-31\n\nЕсли готовы сделать заказ, жмите кнопку ниже 👇\n\n<b>Если бот тормозит, нажмите /start</b>', 
			reply_markup=markup,
			parse_mode='html',
			disable_web_page_preview=True
		)


# Для ручного добавления фоток
# @dp.message_handler(user_id=admin_id, content_types=ContentType.ANY)
# async def frhefh(message: Message):
# 	await message.answer(message)

