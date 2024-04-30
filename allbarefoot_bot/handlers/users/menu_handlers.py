from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import admin_id
from loader import dp
import asyncio
from states import states
from utils.db_api import quick_commands
from keyboards.inline import main_keyboards



@dp.callback_query_handler(text='mailing')
async def mailing(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    markup = main_keyboards.mailing_keyboard
    await call.message.edit_text(
        'Выберите действие',
        reply_markup=markup
    )


@dp.callback_query_handler(text='test')
async def mailing(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    markup = main_keyboards.cancel_keyboard
    await call.message.edit_text(
        'Присылайте сообщение, которое собираетесь разослать только админам',
        reply_markup=markup
    )
    await state.update_data(call_msg=call.message.message_id)
    await states.Command.TestMailing.set()


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


@dp.callback_query_handler(text='confirm', state=states.Command.TestMailingConfirm)
async def button(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    ids_list = await quick_commands.select_all_users()

    await states.Command.ProcessMailing.set()

    data = await state.get_data()
    text = data.get('text')
    photo = data.get('photo')
    caption = data.get('caption')
    for index in admin_id:
        try:
            if text is not None:
                await dp.bot.send_message(index, text, parse_mode='html')
            else:
                if caption is None:
                    await dp.bot.send_photo(index, photo=photo)
                else:
                    await dp.bot.send_photo(index, photo=photo, caption=caption)

        except BotBlocked:
            pass
        except ChatNotFound:
            pass
        except UserDeactivated:
            pass
        except Exception as err:
            await dp.bot.send_message(admin_id[0], f'ошибка - {err}')

        await asyncio.sleep(0.03)
    markup = main_keyboards.to_menu_keyboard
    await call.message.edit_text(
        'Тестовое сообщение разослано!',
        reply_markup=markup
    )
    await state.finish()


@dp.callback_query_handler(text='not_confirm', state=states.Command.TestMailingConfirm)
async def start(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(
        text=f'Рассылка отменена.',
        reply_markup=main_keyboards.to_menu_keyboard
    )


@dp.callback_query_handler(text='send')
async def mailing(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    markup = main_keyboards.cancel_keyboard
    await call.message.edit_text(
        'Присылайте сообщение, которое собираетесь разослать всем пользователям.',
        reply_markup=markup
    )
    await state.update_data(call_msg=call.message.message_id)
    await states.Command.Mailing.set()


@dp.message_handler(content_types=types.ContentType.ANY, state=states.Command.Mailing)
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
        await states.Command.ConfirmMailing.set()

    elif message.photo != []:
        await state.update_data(photo=message.photo[-1].file_id, caption=message.caption)
        markup = main_keyboards.confirm_keyboard
        await dp.bot.edit_message_text(
            'Подтверждаете выбранное сообщение?',
            chat_id=message.chat.id,
            message_id=call_msg,
            reply_markup=markup
        )
        await states.Command.ConfirmMailing.set()

    else:
        markup = main_keyboards.to_menu_keyboard
        await dp.bot.edit_message_text(
            'Сообщение не подходит под формат (одна картинка с подписью или текст). КОМАНДА ОТМЕНЕНА',
            chat_id=message.chat.id,
            message_id=call_msg,
            reply_markup=markup
        )
        await state.finish()


@dp.callback_query_handler(text='confirm', state=states.Command.ConfirmMailing)
async def button(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    ids_list = await quick_commands.select_all_users()

    await states.Command.ProcessMailing.set()

    data = await state.get_data()
    text = data.get('text')
    photo = data.get('photo')
    caption = data.get('caption')
    progress = 'Сообщение рассылается...\n'
    await call.message.edit_text(progress)
    for index, user in enumerate(ids_list):
        if len(ids_list) >= 10:
            if (index%(len(ids_list)//10) == 0) and (index != 0):
                progress += '🟩'
                await call.message.edit_text(progress)
        try:
            if text is not None:
                await dp.bot.send_message(int(user.user_id), text, parse_mode='html')
            else:
                if caption is None:
                    await dp.bot.send_photo(int(user.user_id), photo=photo)
                else:
                    await dp.bot.send_photo(int(user.user_id), photo=photo, caption=caption)

        except BotBlocked:
            pass
        except ChatNotFound:
            pass
        except UserDeactivated:
            pass
        except Exception as err:
            await dp.bot.send_message(admin_id[0], f'ошибка - {err}')

        await asyncio.sleep(0.03)
    markup = main_keyboards.to_menu_keyboard
    await call.message.edit_text(
        'Сообщение разослано!',
        reply_markup=markup
    )
    await state.finish()


@dp.callback_query_handler(text='not_confirm', state=states.Command.ConfirmMailing)
async def start(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(
        text=f'Рассылка отменена.',
        reply_markup=main_keyboards.to_menu_keyboard
    )


@dp.callback_query_handler(text='coeffs')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    settings = await quick_commands.select_settings()
    markup = await main_keyboards.coeffs_keyboard()
    await call.message.edit_text(f'Выберите коэффициент, который хотите поменять\n\nНа данный момент коэффициент <b>{settings.button_2vetka}</b> - {settings.coeff_2vetka}, коэффициент <b>{settings.button_3vetka}</b> - {settings.coeff_3vetka}, коэффициент <b>{settings.button_4vetka}</b> - {settings.coeff_4vetka}', reply_markup=markup)


@dp.callback_query_handler(text='coeff_2')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите целое число', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.Coeff2.set()


@dp.message_handler(state=states.Command.Coeff2)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try: 
        coeff = int(message.text)
        await message.delete()
        await quick_commands.update_coeff_2(coeff)
        await dp.bot.edit_message_text(
            'Коэффициент изменен!',
            chat_id=message.chat.id,
            message_id=data['msg_id'],
            reply_markup=main_keyboards.to_menu_keyboard
        )
        await state.finish()

    except ValueError:
        await dp.bot.edit_message_text(
            'Неверный формат, введите целое число',
            chat_id=message.chat.id,
            message_id=data['msg_id'],
            reply_markup=main_keyboards.cancel_keyboard
        )


@dp.callback_query_handler(text='coeff_3')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите целое число', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.Coeff3.set()


@dp.message_handler(state=states.Command.Coeff3)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try: 
        coeff = int(message.text)
        await message.delete()
        await quick_commands.update_coeff_3(coeff)
        await dp.bot.edit_message_text(
            'Коэффициент изменен!',
            chat_id=message.chat.id,
            message_id=data['msg_id'],
            reply_markup=main_keyboards.to_menu_keyboard
        )
        await state.finish()

    except ValueError:
        await dp.bot.edit_message_text(
            'Неверный формат, введите целое число',
            chat_id=message.chat.id,
            message_id=data['msg_id'],
            reply_markup=main_keyboards.cancel_keyboard
        )


@dp.callback_query_handler(text='coeff_4')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите целое число', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.Coeff4.set()


@dp.message_handler(state=states.Command.Coeff4)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try: 
        coeff = int(message.text)
        await message.delete()
        await quick_commands.update_coeff_4(coeff)
        await dp.bot.edit_message_text(
            'Коэффициент изменен!',
            chat_id=message.chat.id,
            message_id=data['msg_id'],
            reply_markup=main_keyboards.to_menu_keyboard
        )
        await state.finish()

    except ValueError:
        await dp.bot.edit_message_text(
            'Неверный формат, введите целое число',
            chat_id=message.chat.id,
            message_id=data['msg_id'],
            reply_markup=main_keyboards.cancel_keyboard
        )


@dp.callback_query_handler(text='change_texts')
async def change_texts(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    settings = await quick_commands.select_settings()
    markup = await main_keyboards.texts_keyboard()
    await call.message.edit_text(f'Выберите текст, который хотите поменять 👇', reply_markup=markup)


@dp.callback_query_handler(text='text1vetka')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите текст', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.Text1Vetka.set()


@dp.message_handler(state=states.Command.Text1Vetka)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await quick_commands.update_text_1vetka(message.html_text)
    await dp.bot.edit_message_text(
        'Текст изменен!',
        chat_id=message.chat.id,
        message_id=data['msg_id'],
        reply_markup=main_keyboards.to_menu_keyboard
    )
    await state.finish()


@dp.callback_query_handler(text='text2vetka')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите текст', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.Text2Vetka.set()


@dp.message_handler(state=states.Command.Text2Vetka)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await quick_commands.update_text_2vetka(message.html_text)
    await dp.bot.edit_message_text(
        'Текст изменен!',
        chat_id=message.chat.id,
        message_id=data['msg_id'],
        reply_markup=main_keyboards.to_menu_keyboard
    )
    await state.finish()


@dp.callback_query_handler(text='text3vetka')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите текст', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.Text3Vetka.set()


@dp.message_handler(state=states.Command.Text3Vetka)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await quick_commands.update_text_3vetka(message.html_text)
    await dp.bot.edit_message_text(
        'Текст изменен!',
        chat_id=message.chat.id,
        message_id=data['msg_id'],
        reply_markup=main_keyboards.to_menu_keyboard
    )
    await state.finish()


@dp.callback_query_handler(text='text4vetka')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите текст', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.Text4Vetka.set()


@dp.message_handler(state=states.Command.Text4Vetka)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await quick_commands.update_text_4vetka(message.html_text)
    await dp.bot.edit_message_text(
        'Текст изменен!',
        chat_id=message.chat.id,
        message_id=data['msg_id'],
        reply_markup=main_keyboards.to_menu_keyboard
    )
    await state.finish()

@dp.callback_query_handler(text='textcard')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите текст', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.TextCard.set()


@dp.message_handler(state=states.Command.TextCard)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await quick_commands.update_text_card(message.html_text)
    await dp.bot.edit_message_text(
        'Текст изменен!',
        chat_id=message.chat.id,
        message_id=data['msg_id'],
        reply_markup=main_keyboards.to_menu_keyboard
    )
    await state.finish()


@dp.callback_query_handler(text='textsbp')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите текст', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.TextSBP.set()


@dp.message_handler(state=states.Command.TextSBP)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await quick_commands.update_text_sbp(message.html_text)
    await dp.bot.edit_message_text(
        'Текст изменен!',
        chat_id=message.chat.id,
        message_id=data['msg_id'],
        reply_markup=main_keyboards.to_menu_keyboard
    )
    await state.finish()


@dp.callback_query_handler(text='change_buttons')
async def change_buttons(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    settings = await quick_commands.select_settings()
    markup = await main_keyboards.buttons_keyboard() 
    await call.message.edit_text(f'Выберите кнопку, название которой хотите поменять', reply_markup=markup)


@dp.callback_query_handler(text='button1vetka')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите название кнопки', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.Button1.set()


@dp.message_handler(state=states.Command.Button1)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await quick_commands.update_button_1vetka(message.text)
    await dp.bot.edit_message_text(
        'Название кнопки изменено!',
        chat_id=message.chat.id,
        message_id=data['msg_id'],
        reply_markup=main_keyboards.to_menu_keyboard
    )
    await state.finish()


@dp.callback_query_handler(text='button2vetka')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите название кнопки', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.Button2.set()


@dp.message_handler(state=states.Command.Button2)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await quick_commands.update_button_2vetka(message.text)
    await dp.bot.edit_message_text(
        'Название кнопки изменено!',
        chat_id=message.chat.id,
        message_id=data['msg_id'],
        reply_markup=main_keyboards.to_menu_keyboard
    )
    await state.finish()


@dp.callback_query_handler(text='button3vetka')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите название кнопки', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.Button3.set()


@dp.message_handler(state=states.Command.Button3)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await quick_commands.update_button_3vetka(message.text)
    await dp.bot.edit_message_text(
        'Название кнопки изменено!',
        chat_id=message.chat.id,
        message_id=data['msg_id'],
        reply_markup=main_keyboards.to_menu_keyboard
    )
    await state.finish()


@dp.callback_query_handler(text='button4vetka')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите название кнопки', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.Button4.set()


@dp.message_handler(state=states.Command.Button4)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()

    await message.delete()
    await quick_commands.update_button_4vetka(message.text)
    await dp.bot.edit_message_text(
        'Название кнопки изменено!',
        chat_id=message.chat.id,
        message_id=data['msg_id'],
        reply_markup=main_keyboards.to_menu_keyboard
    )
    await state.finish()


# --------------------------- С М Е Н И Т Ь   % ---------------------------------


@dp.callback_query_handler(text='change_percent')
async def coeffs(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    msg = await call.message.edit_text('Введите новый процент, целое число', reply_markup=main_keyboards.cancel_keyboard)

    await state.update_data(msg_id=msg.message_id)
    await states.Command.Percent.set()


@dp.message_handler(state=states.Command.Percent)
async def button(message: types.Message, state: FSMContext):
    data = await state.get_data()

    try: 
        percent = int(message.text)
        await message.delete()
        await quick_commands.update_percent(percent)
        await dp.bot.edit_message_text(
            'Процент изменен!',
            chat_id=message.chat.id,
            message_id=data['msg_id'],
            reply_markup=main_keyboards.to_menu_keyboard
        )
        await state.finish()

    except ValueError:
        await dp.bot.edit_message_text(
            'Неверный формат, введите целое число',
            chat_id=message.chat.id,
            message_id=data['msg_id'],
            reply_markup=main_keyboards.cancel_keyboard
        )


# ------------------- О Т К Л Ю Ч И Т Ь   К Н О П К И ---------------------------


@dp.callback_query_handler(text='close_buttons')
async def partnerka(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text('Выберите действие для кнопок', reply_markup=main_keyboards.close_open_buttons_keyboard)


@dp.callback_query_handler(text='close')
async def partnerka(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    markup = await main_keyboards.close_buttons_keyboard()
    await call.message.edit_text('Выберите кнопку, какую Вы хотите выключить', reply_markup=markup)


@dp.callback_query_handler(text='open')
async def partnerka(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    markup = await main_keyboards.open_buttons_keyboard()
    await call.message.edit_text('Выберите кнопку, какую Вы хотите включить', reply_markup=markup)


@dp.callback_query_handler(text_contains='_close')
async def partnerka(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    button = call.data.split('_')[0]
    if button == 'button1':
        await quick_commands.update_button1_active(False)
    elif button == 'button2':
        await quick_commands.update_button2_active(False)
    elif button == 'button3':
        await quick_commands.update_button3_active(False)
    elif button == 'button4':
        await quick_commands.update_button4_active(False)

    await call.message.edit_text('Кнопка выключена', reply_markup=main_keyboards.to_menu_keyboard)


@dp.callback_query_handler(text_contains='_open')
async def partnerka(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    button = call.data.split('_')[0]
    if button == 'button1':
        await quick_commands.update_button1_active(True)
    elif button == 'button2':
        await quick_commands.update_button2_active(True)
    elif button == 'button3':
        await quick_commands.update_button3_active(True)
    elif button == 'button4':
        await quick_commands.update_button4_active(True)

    await call.message.edit_text('Кнопка включена', reply_markup=main_keyboards.to_menu_keyboard)

