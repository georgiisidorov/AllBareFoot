from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2


bot = Bot(
	token='6852884711:AAHPxALB5TduGW9ST_ioLNRGJxX5wQTicIQ', 
	parse_mode=types.ParseMode.HTML
)
storage = RedisStorage2(prefix='allbarefoot')
dp = Dispatcher(bot, storage=storage)
