import asyncio
import logging
from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import user_handlers
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

# Инициализируем логгер
logger = logging.getLogger(__name__)

# Загружаем конфиг в переменную config
config: Config = load_config()

# Инициализируем бот и диспетчер
bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Регистрация роутеров в диспетчере
dp.include_router(user_handlers.router)

# Функция для получения бота
def get_bot():
    return bot

# Функция для получения диспетчера
def get_dispatcher():
    return dp

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
