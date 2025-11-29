import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import start, referrals, group, admin, responses, support
from database.supabase import init_supabase


async def main() -> None:
    # Initialize Supabase client and ensure tables exist
    init_supabase()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(referrals.router)
    dp.include_router(group.router)
    dp.include_router(admin.router)
    dp.include_router(responses.router)
    dp.include_router(support.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
