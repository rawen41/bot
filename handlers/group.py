from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from config import MAIN_ADMIN_ID, bot_config
from database.supabase import get_explanation_mode, set_explanation_mode, is_manager
from utils.helpers import send_db_response
import logging

router = Router()
logger = logging.getLogger(__name__)


# DEBUG: Catch all messages to see if bot receives anything
@router.message()
async def debug_all_messages(message: Message) -> None:
    """Debug handler to see all messages the bot receives."""
    logger.info(f"DEBUG: Message received in chat {message.chat.id} (type: {message.chat.type}) from user {message.from_user.id}: {message.text or message.caption or 'No text'}")
    
    # If it's a group/supergroup, continue to other handlers
    if message.chat.type in ["group", "supergroup"]:
        # Continue processing
        await handle_group_message(message)
    else:
        # Don't handle private messages here
        pass


async def handle_group_message(message: Message) -> None:
    """Handle actual group message logic."""
    if not message.from_user or message.from_user.is_bot:
        return

    text = (message.text or message.caption or "").strip()
    if not text:
        return

    logger.info(f"Processing group message: {text} from user {message.from_user.id} in chat {message.chat.id}")

    # Check for specific commands
    if text == "بسم الله":
        await enable_explanation_mode(message)
        return
    elif text == "الحمد لله":
        await disable_explanation_mode(message)
        return
    elif text.startswith("/start"):
        await group_start(message)
        return

    # Handle auto-responses
    explanation_mode = get_explanation_mode()

    if explanation_mode:
        # أثناء وضع الشرح: حذف كل الرسائل والرد فقط من قاعدة البيانات
        try:
            await message.delete()
        except Exception:
            pass

        await send_db_response(message, text)
        return

    # وضع عادي: إذا كتب عضو كلمة من الردود الجاهزة → يرسل الرد المناسب (بدون حذف الرسالة)
    await send_db_response(message, text)


@router.message(Command("start"))
async def group_start(message: Message) -> None:
    """Handle /start in groups to check if bot is working."""
    logger.info(f"Group /start from user {message.from_user.id} in chat {message.chat.id}")
    await message.answer("🤖 البوت يعمل بنجاح في المجموعة!")


@router.message(F.text == "بسم الله")
async def enable_explanation_mode(message: Message) -> None:
    logger.info(f"بسم الله from user {message.from_user.id} in group {message.chat.id}")
    if not message.from_user:
        return
    user_id = message.from_user.id
    if user_id != MAIN_ADMIN_ID and not is_manager(user_id):
        await message.reply("❌ هذا الأمر متاح فقط للأدمن والمدراء!")
        return

    set_explanation_mode(True)
    try:
        await message.delete()
    except Exception:
        pass

    await message.answer("✅ تم تفعيل وضع الشرح يرجى من الجميع الإنتباه.")


@router.message(F.text == "الحمد لله")
async def disable_explanation_mode(message: Message) -> None:
    logger.info(f"الحمد لله from user {message.from_user.id} in group {message.chat.id}")
    if not message.from_user:
        return
    user_id = message.from_user.id
    if user_id != MAIN_ADMIN_ID and not is_manager(user_id):
        await message.reply("❌ هذا الأمر متاح فقط للأدمن والمدراء!")
        return

    set_explanation_mode(False)
    try:
        await message.delete()
    except Exception:
        pass

    await message.answer("✅ تم إنهاء وضع الشرح بإمكانكم طرح الأسئلة نشكركم لحسن الإستماع .")
