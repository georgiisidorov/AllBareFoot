from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

contact_keyboard = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text="Передать контакты 📱", request_contact=True)],
		[KeyboardButton(text="Главное меню ↩️")]
	],
	resize_keyboard=True
)

back_keyboard = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text="Пропустить ввод текста ▶️")],
		[KeyboardButton(text="Главное меню ↩️")]
	],
	resize_keyboard=True
)

dialog_keyboard = ReplyKeyboardMarkup(
	keyboard=[
		[KeyboardButton(text="Завершить диалог ❎")]
	],
	resize_keyboard=True
)