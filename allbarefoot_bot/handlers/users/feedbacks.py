import datetime
import logging
import random
import json

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ContentType, MediaGroup, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, PreCheckoutQuery
from aiogram.types.input_media import InputMediaPhoto
from aiogram.utils.exceptions import BotBlocked, ChatNotFound, BadRequest
import asyncio

from data.config import admin_id
from loader import dp
from states import states
from utils.db_api import quick_commands
from keyboards.inline import main_keyboards
from keyboards.default.keyboards import contact_keyboard, back_keyboard



def toJSON(class_self):
    return json.dumps(
        class_self, 
        default=lambda o: o.__dict__, 
        indent=4
    )


# -------------------------- О Т З Ы В Ы ---------------------------------


@dp.callback_query_handler(text='feedbacks')
async def feedbacks(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    feedbacks = await quick_commands.select_all_feedbacks_confirmed()
    feedbacks.reverse()
    if len(feedbacks) > 0:
        feedback_i = 0
        await state.update_data(feedbacks=toJSON(feedbacks), feedback_i=feedback_i)
        msg = await call.message.answer_photo(
            photo=feedbacks[feedback_i].photo,
            caption=f"{feedbacks[feedback_i].text}\n\n{feedback_i+1}/{len(feedbacks)}",
            reply_markup=main_keyboards.slider_keyboard
        )
    else:
        await call.message.answer(
            "Отзывов пока нет",
            reply_markup=main_keyboards.backtomenu_keyboard
        )


@dp.callback_query_handler(text='feedbacks_VIP')
async def feedbacks_VIP(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    feedbacks = await quick_commands.select_all_feedbacks_confirmed()
    feedbacks.reverse()
    if len(feedbacks) > 0:
        feedback_i = 0
        await state.update_data(feedbacks=toJSON(feedbacks), feedback_i=feedback_i)
        msg = await call.message.answer_photo(
            photo=feedbacks[feedback_i].photo,
            caption=f"{feedbacks[feedback_i].text}\n\n{feedback_i+1}/{len(feedbacks)}",
            reply_markup=main_keyboards.slider_keyboard_VIP_2
        )
    else:
        await call.message.answer(
            "Отзывов пока нет",
            reply_markup=main_keyboards.backtomenu_keyboard
        )


@dp.callback_query_handler(text='minus')
async def minus(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    feedbacks = data.get('feedbacks')
    feedbacks = json.loads(feedbacks)
    feedback_i = data.get('feedback_i')
    if feedback_i == 0:
        pass
    else:
        feedback_i -= 1
        await state.update_data(feedback_i=feedback_i)
        await call.message.edit_media(
            InputMediaPhoto(feedbacks[feedback_i]['__values__']['photo'],
            caption=f"{feedbacks[feedback_i]['__values__']['text']}\n\n{feedback_i+1}/{len(feedbacks)}"),
            reply_markup=main_keyboards.slider_keyboard
        )


@dp.callback_query_handler(text='plus')
async def plus(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    feedbacks = data.get('feedbacks')
    feedbacks = json.loads(feedbacks)
    feedback_i = data.get('feedback_i')
    if feedback_i == len(feedbacks)-1:
        pass
    else:
        feedback_i += 1
        await state.update_data(feedback_i=feedback_i)
        await call.message.edit_media(
            InputMediaPhoto(media=feedbacks[feedback_i]['__values__']['photo'],
            caption=f"{feedbacks[feedback_i]['__values__']['text']}\n\n{feedback_i+1}/{len(feedbacks)}"),
            reply_markup=main_keyboards.slider_keyboard
        )


@dp.callback_query_handler(text='minus_VIP_2')
async def minus_VIP_2(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    feedbacks = data.get('feedbacks')
    feedbacks = json.loads(feedbacks)
    feedback_i = data.get('feedback_i')
    if feedback_i == 0:
        pass
    else:
        feedback_i -= 1
        await state.update_data(feedback_i=feedback_i, feedback_id=feedbacks[feedback_i]['__values__']['id'])
        await call.message.edit_media(
            InputMediaPhoto(feedbacks[feedback_i]['__values__']['photo'],
            caption=f"{feedbacks[feedback_i]['__values__']['text']}\n\n{feedback_i+1}/{len(feedbacks)}"),
            reply_markup=main_keyboards.slider_keyboard_VIP_2
        )


@dp.callback_query_handler(text='plus_VIP_2')
async def plus_VIP_2(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    feedbacks = data.get('feedbacks')
    feedbacks = json.loads(feedbacks)
    feedback_i = data.get('feedback_i')
    if feedback_i == len(feedbacks)-1:
        pass
    else:
        feedback_i += 1
        await state.update_data(feedback_i=feedback_i, feedback_id=feedbacks[feedback_i]['__values__']['id'])
        await call.message.edit_media(
            InputMediaPhoto(media=feedbacks[feedback_i]['__values__']['photo'],
            caption=f"{feedbacks[feedback_i]['__values__']['text']}\n\n{feedback_i+1}/{len(feedbacks)}"),
            reply_markup=main_keyboards.slider_keyboard_VIP_2
        )


@dp.callback_query_handler(text='not_confirm_2')
async def not_confirm_2(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    data = await state.get_data()   
    feedbacks = data.get('feedbacks')
    feedbacks = json.loads(feedbacks)
    feedback_i = data.get('feedback_i')
    feedback_id = data.get('feedback_id')

    feedbacks.pop(feedback_i)
    await state.update_data(feedbacks=toJSON(feedbacks))
    await quick_commands.delete_feedback(feedback_id)

    await call.message.answer(
        text=f'Отзыв удалён',
        reply_markup=main_keyboards.slider_keyboard_VIP_empty_2
    )


@dp.callback_query_handler(text='check_feedbacks_again_2')
async def check_feedbacks_again_2(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.delete()
    data = await state.get_data()   
    feedbacks = data.get('feedbacks')
    feedbacks = json.loads(feedbacks)
    if len(feedbacks) > 0:
        feedback_i = 0
        await state.update_data(feedbacks=toJSON(feedbacks), feedback_i=feedback_i, feedback_id=feedbacks[feedback_i]['__values__']['id'])
        await call.message.answer_photo(
            photo=feedbacks[feedback_i]['__values__']['photo'],
            caption=f"{feedbacks[feedback_i]['__values__']['text']}\n\n{feedback_i+1}/{len(feedbacks)}",
            reply_markup=main_keyboards.slider_keyboard_VIP_2
        )
    else:
        await call.message.answer(
            "Отзывов пока нет", 
            reply_markup=main_keyboards.backtomenu_keyboard
        )


# ----------------------------- Н А П И С А Т Ь   О Т З Ы В -----------------------------------



@dp.callback_query_handler(text='writefeedback')
async def payment(call: CallbackQuery, state: FSMContext):
	await call.answer()
	await call.message.delete()
	msg = await call.message.answer("Введите текст", reply_markup=main_keyboards.skip_keyboard)
	await state.update_data(msg_id=msg.message_id)
	await states.States.FeedbackText.set()


@dp.callback_query_handler(state=states.States.FeedbackText, text='skip')
async def payment(call: CallbackQuery, state: FSMContext):
	msg = await call.message.edit_text('Теперь пришлите ОДНУ фотографию', reply_markup=main_keyboards.cancel_keyboard)
	await state.update_data(msg_id=msg.message_id, text='')
	await states.States.FeedbackPhoto.set()


@dp.message_handler(state=states.States.FeedbackText)
async def get_location(message: Message, state: FSMContext):
	await message.delete()
	data = await state.get_data()
	await dp.bot.delete_message(message.from_user.id, data.get('msg_id'))
	
	text = message.text	
	
	msg = await message.answer('Теперь пришлите ОДНУ фотографию')
	await state.update_data(msg_id=msg.message_id, text=text)
	await states.States.FeedbackPhoto.set()


@dp.message_handler(state=states.States.FeedbackPhoto, content_types=ContentType.PHOTO)
async def get_location(message: Message, state: FSMContext):
	await message.delete()
	data = await state.get_data()
	await dp.bot.delete_message(message.from_user.id, data.get('msg_id'))
	
	photo = message.photo[-1].file_id
	await asyncio.sleep(1)

	await quick_commands.add_feedback(photo=photo, text=data.get('text'))
	await message.answer(
		'Спасибо за Ваш отзыв! ❤️', 
		reply_markup=main_keyboards.backtomenu_keyboard
	)
	await state.finish()


# ---------------------------- П Р О В Е Р К А   О Т З Ы В О В ---------------------------------


@dp.callback_query_handler(text='check_feedbacks')
async def start(call: CallbackQuery, state: FSMContext):
	await call.answer()
	await call.message.delete()
	feedbacks = await quick_commands.select_all_feedbacks_not_confirmed()
	if len(feedbacks) > 0:
		feedback_i = 0
		await state.update_data(feedbacks=toJSON(feedbacks), feedback_i=feedback_i, feedback_id=feedbacks[feedback_i].id)
		await call.message.answer_photo(
			photo=feedbacks[feedback_i].photo,
			caption=f"{feedbacks[feedback_i].text}\n\n{feedback_i+1}/{len(feedbacks)}",
			reply_markup=main_keyboards.slider_keyboard_VIP
		)
	else:
		await call.message.answer(
			"Новых отзывов пока нет", 
			reply_markup=main_keyboards.backtomenu_keyboard
		)


@dp.callback_query_handler(text='check_feedbacks_again')
async def start(call: CallbackQuery, state: FSMContext):
	await call.answer()
	await call.message.delete()
	data = await state.get_data()	
	feedbacks = data.get('feedbacks')
	feedbacks = json.loads(feedbacks)
	if len(feedbacks) > 0:
		feedback_i = 0
		await state.update_data(feedbacks=toJSON(feedbacks), feedback_i=feedback_i, feedback_id=feedbacks[feedback_i]['__values__']['id'])
		await call.message.answer_photo(
			photo=feedbacks[feedback_i]['__values__']['photo'],
			caption=f"{feedbacks[feedback_i]['__values__']['text']}\n\n{feedback_i+1}/{len(feedbacks)}",
			reply_markup=main_keyboards.slider_keyboard_VIP
		)
	else:
		await call.message.answer(
			"Новых отзывов пока нет", 
			reply_markup=main_keyboards.backtomenu_keyboard
		)



@dp.callback_query_handler(text='minus_VIP')
async def payment(call: CallbackQuery, state: FSMContext):
	await call.answer()
	data = await state.get_data()
	feedbacks = data.get('feedbacks')
	feedbacks = json.loads(feedbacks)
	feedback_i = data.get('feedback_i')
	if feedback_i == 0:
		pass
	else:
		feedback_i -= 1
		await state.update_data(feedback_i=feedback_i, feedback_id=feedbacks[feedback_i]['__values__']['id'])
		await call.message.edit_media(
			InputMediaPhoto(feedbacks[feedback_i]['__values__']['photo'],
			caption=f"{feedbacks[feedback_i]['__values__']['text']}\n\n{feedback_i+1}/{len(feedbacks)}"),
			reply_markup=main_keyboards.slider_keyboard_VIP
		)


@dp.callback_query_handler(text='plus_VIP')
async def payment(call: CallbackQuery, state: FSMContext):
	await call.answer()
	data = await state.get_data()
	feedbacks = data.get('feedbacks')
	feedbacks = json.loads(feedbacks)
	feedback_i = data.get('feedback_i')
	if feedback_i == len(feedbacks)-1:
		pass
	else:
		feedback_i += 1
		await state.update_data(feedback_i=feedback_i, feedback_id=feedbacks[feedback_i]['__values__']['id'])
		await call.message.edit_media(
			InputMediaPhoto(media=feedbacks[feedback_i]['__values__']['photo'],
			caption=f"{feedbacks[feedback_i]['__values__']['text']}\n\n{feedback_i+1}/{len(feedbacks)}"),
			reply_markup=main_keyboards.slider_keyboard_VIP
		)


@dp.callback_query_handler(text='change_photo')
async def get_location(call: CallbackQuery, state: FSMContext):
	await call.message.delete()

	msg = await call.message.answer('Пришлите фотографию на замену')
	await state.update_data(msg_id=msg.message_id)
	await states.States.FeedbackPhoto_Change.set()


@dp.message_handler(state=states.States.FeedbackPhoto_Change, content_types=ContentType.PHOTO)
async def get_location(message: Message, state: FSMContext):
	await message.delete()
	data = await state.get_data()	
	feedbacks = data.get('feedbacks')
	feedbacks = json.loads(feedbacks)
	feedback_i = data.get('feedback_i')
	feedback_id = data.get('feedback_id')
	await dp.bot.delete_message(message.from_user.id, data.get('msg_id'))
	
	photo = message.photo[-1].file_id
	feedbacks[feedback_i]['__values__']['photo'] = photo
	
	await quick_commands.update_feedback_photo(feedback_id, photo)

	await state.finish()
	await state.update_data(feedbacks=toJSON(feedbacks))
	await message.answer_photo(
			photo=photo,
			caption=f"{feedbacks[feedback_i]['__values__']['text']}\n\n{feedback_i+1}/{len(feedbacks)}",
			reply_markup=main_keyboards.slider_keyboard_VIP
		)


@dp.callback_query_handler(text='confirm')
async def start(call: CallbackQuery, state: FSMContext):
	await call.answer()
	await call.message.delete()
	data = await state.get_data()	
	feedbacks = data.get('feedbacks')
	feedbacks = json.loads(feedbacks)
	feedback_i = data.get('feedback_i')
	feedback_id = data.get('feedback_id')

	feedbacks.pop(feedback_i)
	await state.update_data(feedbacks=toJSON(feedbacks))
	await quick_commands.update_feedback_confirmed(feedback_id, '1')

	await call.message.answer(
		text=f'Отзыв одобрен',
		reply_markup=main_keyboards.slider_keyboard_VIP_empty
	)


@dp.callback_query_handler(text='not_confirm')
async def start(call: CallbackQuery, state: FSMContext):
	await call.answer()
	await call.message.delete()
	data = await state.get_data()	
	feedbacks = data.get('feedbacks')
	feedbacks = json.loads(feedbacks)
	feedback_i = data.get('feedback_i')
	feedback_id = data.get('feedback_id')

	feedbacks.pop(feedback_i)
	await state.update_data(feedbacks=toJSON(feedbacks))
	await quick_commands.delete_feedback(feedback_id)

	await call.message.answer(
		text=f'Отзыв удалён',
		reply_markup=main_keyboards.slider_keyboard_VIP_empty
	)