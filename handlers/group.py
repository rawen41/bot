from aiogram import Router, F
from aiogram.types import Message
from config import MAIN_ADMIN_ID
from database.supabase import get_explanation_mode, set_explanation_mode, is_manager
from utils.helpers import send_db_response

router = Router()
router.message.filter((F.chat.type == "group") | (F.chat.type == "supergroup"))


@router.message(F.text == "بسم الله")
async def enable_explanation_mode(message: Message) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    if user_id != MAIN_ADMIN_ID and not is_manager(user_id):
        return

    set_explanation_mode(True)
    try:
        await message.delete()
    except Exception:
        pass

    await message.answer("🧩 تم تفعيل وضع الشرح ✅")


@router.message(F.text == "الحمد لله")
async def disable_explanation_mode(message: Message) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id
    if user_id != MAIN_ADMIN_ID and not is_manager(user_id):
        return

    set_explanation_mode(False)
    try:
        await message.delete()
    except Exception:
        pass

    await message.answer("🧩 تم إلغاء وضع الشرح ⛔️")


@router.message()
async def group_auto_moderation(message: Message) -> None:
    if not message.from_user or message.from_user.is_bot:
        return

    text = (message.text or message.caption or "").strip()
    if not text:
        return

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
