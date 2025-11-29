from aiogram import Router
from aiogram.types import Message
from aiogram.filters import ChatTypeFilter

from config import bot_config
from database.supabase import get_user_stats, get_top_referrers

router = Router()


@router.message(ChatTypeFilter(chat_type=["private"]))
async def show_referral_info(message: Message) -> None:
    """Optional detailed referral info via buttons in future (reserved)."""
    if (message.text or "").strip() != "إحالاتي":
        return

    stats = get_user_stats(message.from_user.id)
    count = stats.get("referral_count", 0) if stats else 0
    link = f"https://t.me/{bot_config.bot_username.lstrip('@')}?start={message.from_user.id}"

    await message.answer(
        "📊 لوحة الإحالات:\n\n"
        f"🔗 رابط الإحالة الخاص بك:\n{link}\n\n"
        f"👥 عدد الإحالات الناجحة: {count}"
    )


@router.message(ChatTypeFilter(chat_type=["supergroup", "group"]))
async def group_referral_announcement(message: Message) -> None:
    # This router is reserved if we want explicit referral commands in group later.
    return
