from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.db_api import quick_commands


back_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад 🔙", callback_data='back')]])


to_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')]
])

to_menu_keyboard_add_order = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu_order')]
])


async def tracking_keyboard(user_id):
        markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Отправить трек ℹ️", callback_data=f'sendtrack_{user_id}')]
        ])
        return markup


async def user_info_keyboard(user_id, name):
        markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"Информация о пользователе 🙂", callback_data=f'info_{user_id}_{name}')],
                [InlineKeyboardButton(text=f"История переписки 📝", callback_data=f'doc_{user_id}')],
                [InlineKeyboardButton(text=f"Завершить диалог ❎", callback_data=f'close_dialog')]

        ])
        return markup


async def texts_keyboard():
        settings = await quick_commands.select_settings()
        buttons = []

        if settings.button1_active == True:
                buttons.append([InlineKeyboardButton(text=f"Условия {settings.button_1vetka}", callback_data='text1vetka')])
        if settings.button2_active == True:
                buttons.append([InlineKeyboardButton(text=f"Условия {settings.button_2vetka}", callback_data='text2vetka')])
        if settings.button3_active == True:
                buttons.append([InlineKeyboardButton(text=f"Условия {settings.button_3vetka}", callback_data='text3vetka')])
        if settings.button4_active == True:
                buttons.append([InlineKeyboardButton(text=f"Условия {settings.button_4vetka}", callback_data='text4vetka')])
        
        buttons.append([InlineKeyboardButton(text="Текст КАРТА ТИНЬКОФФ", callback_data='textcard')])
        buttons.append([InlineKeyboardButton(text="Текст СБП", callback_data='textsbp')])
        buttons.append([InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')])
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        return markup


async def buttons_keyboard():
        settings = await quick_commands.select_settings()
        buttons = []

        if settings.button1_active == True:
                buttons.append([InlineKeyboardButton(text=f"Изменить {settings.button_1vetka}", callback_data='button1vetka')])
        if settings.button2_active == True:
                buttons.append([InlineKeyboardButton(text=f"Изменить {settings.button_2vetka}", callback_data='button2vetka')])
        if settings.button3_active == True:
                buttons.append([InlineKeyboardButton(text=f"Изменить {settings.button_3vetka}", callback_data='button3vetka')])
        if settings.button4_active == True:
                buttons.append([InlineKeyboardButton(text=f"Изменить {settings.button_4vetka}", callback_data='button4vetka')])
        
        buttons.append([InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')])
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        return markup


async def close_buttons_keyboard():
        settings = await quick_commands.select_settings()
        buttons = []

        if settings.button1_active == True:
                buttons.append([InlineKeyboardButton(text=f"{settings.button_1vetka}", callback_data='button1_close')])
        if settings.button2_active == True:
                buttons.append([InlineKeyboardButton(text=f"{settings.button_2vetka}", callback_data='button2_close')])
        if settings.button3_active == True:
                buttons.append([InlineKeyboardButton(text=f"{settings.button_3vetka}", callback_data='button3_close')])
        if settings.button4_active == True:
                buttons.append([InlineKeyboardButton(text=f"{settings.button_4vetka}", callback_data='button4_close')])
        
        buttons.append([InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')])
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        return markup


async def open_buttons_keyboard():
        settings = await quick_commands.select_settings()
        buttons = []

        if settings.button1_active == False:
                buttons.append([InlineKeyboardButton(text=f"{settings.button_1vetka}", callback_data='button1_open')])
        if settings.button2_active == False:
                buttons.append([InlineKeyboardButton(text=f"{settings.button_2vetka}", callback_data='button2_open')])
        if settings.button3_active == False:
                buttons.append([InlineKeyboardButton(text=f"{settings.button_3vetka}", callback_data='button3_open')])
        if settings.button4_active == False:
                buttons.append([InlineKeyboardButton(text=f"{settings.button_4vetka}", callback_data='button4_open')])
        
        buttons.append([InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')])
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        return markup


VIP_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Рассылка ✉️ ", callback_data='mailing'),
        InlineKeyboardButton(text="📗 Excel", callback_data='excel')],
        [InlineKeyboardButton(text="Отзывы ℹ️", callback_data='feedbacks_VIP'),
        InlineKeyboardButton(text="Написать отзыв ✍️", callback_data='writefeedback')],
        [InlineKeyboardButton(text="Одобрить отзывы ✅", callback_data='check_feedbacks'),
        InlineKeyboardButton(text="Сменить коэффициент", callback_data='coeffs')],
        [InlineKeyboardButton(text="Сменить текст", callback_data='change_texts'),
        InlineKeyboardButton(text="Сменить кнопки", callback_data='change_buttons')],
        [InlineKeyboardButton(text="Вкл/выкл кнопки", callback_data='close_buttons'),
        InlineKeyboardButton(text="Сменить %", callback_data='change_percent')],
        [InlineKeyboardButton(text="Связаться с клиентом ⚙️", callback_data='support_2')]

])


close_open_buttons_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Включить ✅", callback_data='open'),
        InlineKeyboardButton(text="Выключить ❌", callback_data='close')],
        [InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')]
])


async def coeffs_keyboard():
        settings = await quick_commands.select_settings()
        markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"Коэффициент {settings.button_2vetka}", callback_data='coeff_2')],
                [InlineKeyboardButton(text=f"Коэффициент {settings.button_3vetka}", callback_data='coeff_3')],
                [InlineKeyboardButton(text=f"Коэффициент {settings.button_4vetka}", callback_data='coeff_4')],
                [InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')]
        ])
        return markup


async def menu_keyboard():
        settings = await quick_commands.select_settings()
        buttons = []

        if settings.button1_active == True:
                buttons.append([InlineKeyboardButton(text=settings.button_1vetka, callback_data='belenka_sale')])
        if settings.button2_active == True:
                buttons.append([InlineKeyboardButton(text=settings.button_2vetka, callback_data='bosoobuv')])
        if settings.button3_active == True:
                buttons.append([InlineKeyboardButton(text=settings.button_3vetka, callback_data='littleshoes')])
        if settings.button4_active == True:
                buttons.append([InlineKeyboardButton(text=settings.button_4vetka, callback_data='fare')])
        
        buttons.append([InlineKeyboardButton(text="Написать отзыв ✍️", callback_data='writefeedback'),
                InlineKeyboardButton(text="Отзывы ℹ️", callback_data='feedbacks')])
        buttons.append([InlineKeyboardButton(text="Партнёрка 🤝", callback_data='partnerka'),
                InlineKeyboardButton(text="Техподдержка ⚙️", callback_data='support')])
        buttons.append([InlineKeyboardButton(text="Мои заказы 🗃", callback_data='my_orders')])
        buttons.append([InlineKeyboardButton(text="О сервисе ℹ️", callback_data='service_info')])

        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        return markup


async def orders_keyboard(user_id):
        orders = await quick_commands.select_orders_by_user_id(user_id)
        lst_buttons = [[InlineKeyboardButton(text=f"№ | 💚 | создан", callback_data='xxx')]]
        for order in orders:
                lst_buttons.append([InlineKeyboardButton(text=f"{order.id} | 💚 | {order.time_created}", callback_data=f'order;{order.id}')])
        lst_buttons.append([InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')])
        markup = InlineKeyboardMarkup(inline_keyboard=lst_buttons)
        return markup


async def orders_keyboard_without_menu(user_id):
        orders = await quick_commands.select_orders_by_user_id(user_id)
        lst_buttons = [[InlineKeyboardButton(text=f"№ | 💚 | создан", callback_data='xxx')]]
        for order in orders:
                lst_buttons.append([InlineKeyboardButton(text=f"{order.id} | 💚 | {order.time_created}", callback_data=f'order;{order.id}')])
        lst_buttons.append([InlineKeyboardButton(text="Закрыть ❌", callback_data='close_info')])
        markup = InlineKeyboardMarkup(inline_keyboard=lst_buttons)
        return markup



mailing_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Тестировать рассылку ❓", callback_data='test')],
        [InlineKeyboardButton(text="Разослать рассылку 📨", callback_data='send')],
        [InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')]
])


skip_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить ввод текста ▶️", callback_data='skip')],
        [InlineKeyboardButton(text="Отмена 🚫", callback_data='cancel')]
])


cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отмена 🚫", callback_data='cancel')]
])


oplata_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="На номер карты Тинькофф", callback_data='tinkoff')],
        [InlineKeyboardButton(text="Через СБП", callback_data='SBP')],
        [InlineKeyboardButton(text="Криптовалютой", callback_data='crypto')],
        [InlineKeyboardButton(text="Списать бонусы 🤩", callback_data='bonus')],
        [InlineKeyboardButton(text="Отмена 🚫", callback_data='cancel')]
])

bonus_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='ДА! 🥰', callback_data='yes')],
        [InlineKeyboardButton(text="Назад 🔙", callback_data='back')]
])

slider_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️", callback_data='minus'),
        InlineKeyboardButton(text="▶️", callback_data='plus')],
        [InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')]
])


slider_keyboard_VIP = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️", callback_data='minus_VIP'),
        InlineKeyboardButton(text="▶️", callback_data='plus_VIP')],
        [InlineKeyboardButton(text="Сменить фотографию", callback_data='change_photo')],
        [InlineKeyboardButton(text="Удалить ❌", callback_data='not_confirm'),
        InlineKeyboardButton(text="Одобрить ✅", callback_data='confirm')],
        [InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')]
])


confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отмена ❌", callback_data='not_confirm'),
        InlineKeyboardButton(text="Подтвердить ✅", callback_data='confirm')],
])


async def confirm_keyboard_transaction(msg_id, user_id):
        markup  = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Отмена ❌", callback_data=f'not_confirm_{msg_id}_{user_id}'),
                InlineKeyboardButton(text="Подтвердить ✅", callback_data=f'confirm_{msg_id}_{user_id}')],
        ])
        return markup


slider_keyboard_VIP_2 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️", callback_data='minus_VIP_2'),
        InlineKeyboardButton(text="▶️", callback_data='plus_VIP_2')],
        [InlineKeyboardButton(text="Удалить отзыв ❌", callback_data='not_confirm_2')],
        [InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')]
])


slider_keyboard_VIP_empty = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться к отзывам", callback_data='check_feedbacks_again')],
        [InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')]
])


slider_keyboard_VIP_empty_2 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться к отзывам", callback_data='check_feedbacks_again_2')],
        [InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')]
])


backtomenu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu')]
])

backtomenu_del_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Главное меню ↩️", callback_data='menu_del')]
])

close_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Закрыть ❌", callback_data='close_info')]
])