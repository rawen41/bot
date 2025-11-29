from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
import logging

from config import MAIN_ADMIN_ID, bot_config
from database.supabase import (
    get_top_referrers,
    get_explanation_mode,
    add_manager,
    remove_manager,
    is_manager,
    get_client,
)
from utils.keyboards import (
    admin_panel_kb,
    responses_manage_kb,
    managers_manage_kb,
    main_menu_kb,
)
from utils.states import (
    BroadcastState,
    ManagerAddState,
    ManagerRemoveState,
)

router = Router()
# Log everything for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _is_main_admin(message: Message) -> bool:
    return bool(message.from_user and message.from_user.id == MAIN_ADMIN_ID)


@router.message(F.text == "📂 إدارة الردود الجاهزة")
async def open_responses_menu(message: Message) -> None:
    logger.info(f"Admin button pressed: {message.text} from user {message.from_user.id}")
    if not _is_main_admin(message):
        await message.answer("❌ هذه الميزة متاحة فقط للأدمن الرئيسي.")
        return
    await message.answer("📂 اختر العملية المطلوبة:", reply_markup=responses_manage_kb())


@router.message(F.text == "👨‍💼 إدارة المدراء")
async def open_managers_menu(message: Message) -> None:
    logger.info(f"Admin button pressed: {message.text} from user {message.from_user.id}")
    if not _is_main_admin(message):
        await message.answer("❌ هذه الميزة متاحة فقط للأدمن الرئيسي.")
        return
    await message.answer("👨‍💼 إدارة المدراء:", reply_markup=managers_manage_kb())


@router.message(F.text == "📊 الإحالات و المكافآت")
async def show_referrals_and_rewards(message: Message) -> None:
    logger.info(f"Admin button pressed: {message.text} from user {message.from_user.id}")
    if not _is_main_admin(message):
        await message.answer("❌ هذه الميزة متاحة فقط للأدمن الرئيسي.")
        return

    top = get_top_referrers(10)
    if not top:
        await message.answer("لا يوجد إحالات مسجّلة بعد.")
        return

    lines = ["📊 أفضل المحيلين:"]
    for idx, row in enumerate(top, start=1):
        username = row.get("username") or f"ID {row.get('tg_id')}"
        lines.append(f"{idx}. {username} → {row.get('referral_count', 0)} إحالة")

    await message.answer("\n".join(lines))


@router.message(F.text == "📢 رسالة للمجموعة")
async def start_broadcast(message: Message, state: FSMContext) -> None:
    logger.info(f"Admin button pressed: {message.text} from user {message.from_user.id}")
    if not _is_main_admin(message):
        await message.answer("❌ هذه الميزة متاحة فقط للأدمن الرئيسي.")
        return

    await state.set_state(BroadcastState.waiting_for_text)
    await message.answer("✉️ أرسل الآن الرسالة التي تريد إرسالها إلى المجموعة:")


@router.message(BroadcastState.waiting_for_text)
async def send_broadcast(message: Message, state: FSMContext) -> None:
    if not _is_main_admin(message):
        await state.clear()
        return

    text = (message.text or "").strip()
    if not text:
        await message.answer("❌ الرجاء إرسال نص الرسالة.")
        return

    await message.bot.send_message(
        chat_id=bot_config.managed_group_id,
        text=f"📢 رسالة من الإدارة:\n\n{text}",
    )
    await message.answer("✅ تم إرسال الرسالة إلى المجموعة.")
    await state.clear()


@router.message(F.text == "⚙️ إعدادات البوت")
async def show_settings(message: Message) -> None:
    logger.info(f"Admin button pressed: {message.text} from user {message.from_user.id}")
    if not _is_main_admin(message):
        await message.answer("❌ هذه الميزة متاحة فقط للأدمن الرئيسي.")
        return

    mode = get_explanation_mode()
    await message.answer(
        "⚙️ إعدادات البوت الحالية:\n"
        f"🧩 وضع الشرح: {'مفعل ✅' if mode else 'متوقف ⛔️'}\n\n"
        "لتفعيل وضع الشرح في المجموعة اكتب: بسم الله\n"
        "ولإلغائه اكتب: الحمد لله"
    )


@router.message(F.text == "⬅️ رجوع للقائمة الرئيسية")
async def back_to_main_menu(message: Message) -> None:
    logger.info(f"Admin button pressed: {message.text} from user {message.from_user.id}")
    if not _is_main_admin(message):
        await message.answer("❌ هذه الميزة متاحة فقط للأدمن الرئيسي.")
        return

    await message.answer(
        "🔙 تم الرجوع إلى القائمة الرئيسية.",
        reply_markup=main_menu_kb(message.from_user.id),
    )


# إدارة المدراء


@router.message(F.text == "➕ إضافة مدير")
async def manager_add_start(message: Message, state: FSMContext) -> None:
    logger.info(f"Admin button pressed: {message.text} from user {message.from_user.id}")
    if not _is_main_admin(message):
        await message.answer("❌ هذه الميزة متاحة فقط للأدمن الرئيسي.")
        return

    await state.set_state(ManagerAddState.waiting_for_tg_id)
    await message.answer("👤 أرسل الآن آيدي تيليجرام للمدير الجديد (أرقام فقط):")


@router.message(ManagerAddState.waiting_for_tg_id)
async def manager_add_finish(message: Message, state: FSMContext) -> None:
    if not _is_main_admin(message):
        await state.clear()
        return

    if not message.text or not message.text.isdigit():
        await message.answer("❌ الرجاء إرسال آيدي صالح (أرقام فقط).")
        return

    manager_id = int(message.text)
    add_manager(manager_id, added_by=message.from_user.id)
    await message.answer(f"✅ تم إضافة المدير: {manager_id}")
    await state.clear()


@router.message(F.text == "➖ حذف مدير")
async def manager_remove_start(message: Message, state: FSMContext) -> None:
    logger.info(f"Admin button pressed: {message.text} from user {message.from_user.id}")
    if not _is_main_admin(message):
        await message.answer("❌ هذه الميزة متاحة فقط للأدمن الرئيسي.")
        return

    await state.set_state(ManagerRemoveState.waiting_for_tg_id)
    await message.answer("🗑 أرسل آيدي المدير الذي تريد حذفه:")


@router.message(ManagerRemoveState.waiting_for_tg_id)
async def manager_remove_finish(message: Message, state: FSMContext) -> None:
    if not _is_main_admin(message):
        await state.clear()
        return

    if not message.text or not message.text.isdigit():
        await message.answer("❌ الرجاء إرسال آيدي صالح (أرقام فقط).")
        return

    manager_id = int(message.text)
    remove_manager(manager_id)
    await message.answer(f"✅ تم حذف المدير: {manager_id}")
    await state.clear()


@router.message(F.text == "📋 قائمة المدراء")
async def list_managers(message: Message) -> None:
    logger.info(f"Admin button pressed: {message.text} from user {message.from_user.id}")
    if not _is_main_admin(message):
        await message.answer("❌ هذه الميزة متاحة فقط للأدمن الرئيسي.")
        return

    client = get_client()
    res = client.table("managers").select("tg_id").execute()
    managers = res.data or []
    if not managers:
        await message.answer("لا يوجد مدراء مضافون بعد.")
        return

    lines = ["📋 قائمة المدراء:"]
    for row in managers:
        lines.append(f"• {row['tg_id']}")

    await message.answer("\n".join(lines))
