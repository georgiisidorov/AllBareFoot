from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def markup_pay(invoice):
    markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Перейти к оплате", url=invoice)],
                [InlineKeyboardButton(text="✅ Проверить оплату", callback_data="paid")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data='menu')]
            ]
        )

    return markup




