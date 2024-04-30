import datetime
import operator
import asyncio
from utils.db_api.db_gino import db
from utils.db_api.schemas.user import User
from utils.db_api.schemas.order import Order
from utils.db_api.schemas.purchase import Purchase
from utils.db_api.schemas.feedback import Feedback
from utils.db_api.schemas.settings import Settings
from asyncpg import UniqueViolationError


async def add_user(
        user_id: int, 
        username: str,
        referer: int,
        balance: int=0,
        zarabotok: int=0, 
        bloger: bool=False,
        percent: int=3
    ):
    try:
        user = User(
            user_id=user_id,
            username=username,
            referer=referer,
            balance=balance,
            zarabotok=zarabotok,
            bloger=bloger,
            percent=percent
        )
        await user.create()
    except UniqueViolationError:
        pass


async def select_all_users():
    users = await User.query.gino.all()
    return users


async def select_user(user_id: int):
    user = await User.query.where(User.user_id == user_id).gino.first()
    return user


async def update_user_balance(user_id: int, balance: int):
    user = await User.query.where(User.user_id == user_id).gino.first()
    await user.update(balance=balance).apply()


async def add_purchase(
        user_id: int,
        item: str,
        amount: float,
        currency: str,
        status: str
    ):
    try:
        purchase = Purchase(
            user_id=user_id,
            item=item,
            amount=amount,
            currency=currency,
            status=status
        )
        await purchase.create()
    except UniqueViolationError:
        pass


async def select_all_purchases_by_user_id(user_id: int):
    purchases = await Purchase.query.where(Purchase.user_id == user_id).gino.all()
    return purchases


async def sum_purchases_by_user_id(user_id: int):
    purchases = await Purchase.query.where(Purchase.user_id == user_id).gino.all()
    summ = 0
    for purchase in purchases:
        summ += purchase.amount
    return summ


async def add_feedback(photo: str, text: str, confirmed: str='0'):
    try:
        feedback = Feedback(
            photo=photo, 
            text=text,
            confirmed=confirmed
        )
        await feedback.create()
    except UniqueViolationError:  
        pass


async def select_feedback(id: int):
    feedback = await Feedback.query.where(Feedback.id == id).gino.first()
    return feedback


async def select_all_feedbacks_not_confirmed():
    feedbacks = await Feedback.query.where(Feedback.confirmed == '0').gino.all()
    return feedbacks


async def select_all_feedbacks_confirmed():
    feedbacks = await Feedback.query.where(Feedback.confirmed == '1').gino.all()
    return feedbacks


async def update_feedback_photo(id, photo):
    feedback = await Feedback.get(id)
    await feedback.update(photo=photo).apply()


async def update_feedback_confirmed(id, confirmed):
    feedback = await Feedback.get(id)
    await feedback.update(confirmed=confirmed).apply()


async def delete_feedback(id):
    feedback = await Feedback.query.where(Feedback.id == id).gino.first()
    await feedback.delete()


async def add_order(
        user_id: int,
        time_created: str,
        link_name_number: str, 
        name_user: str, 
        address: str, 
        phone: str, 
        model_name: str, 
        model_color: str, 
        model_size: str, 
        model_price: str, 
        currency: str,
        screen: str,
        bonus: int
    ):
    try:
        order = Order(
            user_id=user_id,
            time_created=time_created,
            link_name_number=link_name_number, 
            name_user=name_user, 
            address=address, 
            phone=phone, 
            model_name=model_name, 
            model_color=model_color, 
            model_size=model_size, 
            model_price=model_price, 
            currency=currency,
            screen=screen,
            bonus=bonus 
        )
        await order.create()
        return order
    except UniqueViolationError:
        pass


async def sum_orders_by_user_id(user_id: int):
    orders = await Order.query.where(Order.user_id == user_id).gino.all()
    summ = 0
    for order in orders:
        summ += int(order.model_price)
    return summ


async def select_order(order_id: int):
    order = await Order.query.where(Order.id == order_id).gino.first()
    return order


async def select_orders_by_user_id(user_id: int):
    orders = await Order.query.where(Order.user_id == user_id).gino.all()
    return orders


async def select_all_orders():
    orders = await Order.query.gino.all()
    return orders


async def add_settings(
        coeff_2vetka: int,
        coeff_3vetka: int,
        coeff_4vetka: int,
        button_1vetka: str,
        button_2vetka: str,
        button_3vetka: str,
        button_4vetka: str,
        button1_active: bool,
        button2_active: bool,
        button3_active: bool,
        button4_active: bool,
        text_1vetka: str,
        text_2vetka: str,
        text_3vetka: str,
        text_4vetka: str,
        text_card: str,
        text_sbp: str,
        percent: int,
    ):
    try:
        settings = Settings(
            coeff_2vetka=coeff_2vetka,
            coeff_3vetka=coeff_3vetka,
            coeff_4vetka=coeff_4vetka,
            button_1vetka=button_1vetka,
            button_2vetka=button_2vetka,
            button_3vetka=button_3vetka,
            button_4vetka=button_4vetka,
            button1_active=button1_active,
            button2_active=button2_active,
            button3_active=button3_active,
            button4_active=button4_active,
            text_1vetka=text_1vetka,
            text_2vetka=text_2vetka,
            text_3vetka=text_3vetka,
            text_4vetka=text_4vetka,
            text_card=text_card,
            text_sbp=text_sbp,
            percent=percent
        )
        await settings.create()
    except UniqueViolationError:
        pass


async def select_settings():
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    return settings


async def select_coeff_2vetka():
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    return settings.coeff_2vetka


async def select_coeff_3vetka():
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    return settings.coeff_3vetka


async def select_coeff_4vetka():
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    return settings.coeff_4vetka


async def select_text_1vetka():
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    return settings.text_1vetka


async def select_text_2vetka():
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    return settings.text_2vetka


async def select_text_3vetka():
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    return settings.text_3vetka


async def select_text_4vetka():
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    return settings.text_4vetka


async def select_text_card():
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    return settings.text_card


async def select_text_sbp():
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    return settings.text_sbp


async def update_coeff_2(coeff_2):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(coeff_2vetka=coeff_2).apply()


async def update_coeff_3(coeff_3):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(coeff_3vetka=coeff_3).apply()


async def update_coeff_4(coeff_4):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(coeff_4vetka=coeff_4).apply()


async def update_text_1vetka(text_1vetka):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(text_1vetka=text_1vetka).apply()


async def update_text_2vetka(text_2vetka):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(text_2vetka=text_2vetka).apply()


async def update_text_3vetka(text_3vetka):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(text_3vetka=text_3vetka).apply()


async def update_text_4vetka(text_4vetka):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(text_4vetka=text_4vetka).apply()


async def update_button_1vetka(button_1vetka):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(button_1vetka=button_1vetka).apply()


async def update_button_2vetka(button_2vetka):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(button_2vetka=button_2vetka).apply()


async def update_button_3vetka(button_3vetka):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(button_3vetka=button_3vetka).apply()


async def update_button_4vetka(button_4vetka):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(button_4vetka=button_4vetka).apply()


async def update_text_card(text_card):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(text_card=text_card).apply()


async def update_text_sbp(text_sbp):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(text_sbp=text_sbp).apply()


async def update_button1_active(active):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(button1_active=active).apply()


async def update_button2_active(active):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(button2_active=active).apply()


async def update_button3_active(active):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(button3_active=active).apply()


async def update_button4_active(active):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(button4_active=active).apply()


async def update_percent(percent):
    settings = await Settings.query.where(Settings.id == 1).gino.first()
    await settings.update(percent=percent).apply()