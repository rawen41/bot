import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import start, referrals, group, admin, responses, support
from database.supabase import init_supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    # Initialize Supabase client and ensure tables exist
    init_supabase()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers - admin first to catch admin commands
    logger.info("Registering admin router...")
    dp.include_router(admin.router)
    logger.info("Registering responses router...")
    dp.include_router(responses.router)
    logger.info("Registering start router...")
    dp.include_router(start.router)
    logger.info("Registering referrals router...")
    dp.include_router(referrals.router)
    logger.info("Registering group router...")
    dp.include_router(group.router)
    logger.info("Registering support router...")
    dp.include_router(support.router)
    logger.info("All routers registered successfully!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
