from aiogram import Router
from aiogram.types import Message
from aiogram.filters import ChatTypeFilter

from config import bot_config

router = Router()
router.message.filter(ChatTypeFilter(chat_type=["private"]))


@router.message()
async def support_info(message: Message) -> None:
    # معلومات بسيطة عن الدعم، الردود المتقدمة تتم عبر الأزرار في start.py
    if (message.text or "").strip() == "دعم":
        await message.answer(
            "💬 للتواصل مع الدعم الفني:\n"
            f"{bot_config.support_username}"
        )
