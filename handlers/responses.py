from io import BytesIO
import logging

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from config import MAIN_ADMIN_ID
from database.supabase import (
    add_response,
    delete_response,
    update_response_content,
    get_response,
    encode_file_to_base64,
)
from utils.keyboards import response_type_kb
from utils.states import AddResponseState, DeleteResponseState, EditResponseState

router = Router()
logger = logging.getLogger(__name__)


def _is_main_admin(message: Message) -> bool:
    return bool(message.from_user and message.from_user.id == MAIN_ADMIN_ID)


# إضافة رد جديد


@router.message(F.text == "➕ إضافة رد جديد", StateFilter(None))
async def add_response_start(message: Message, state: FSMContext) -> None:
    logger.info(f"Response button pressed: {message.text} from user {message.from_user.id}")
    if not _is_main_admin(message):
        await message.answer("❌ هذه الميزة متاحة فقط للأدمن الرئيسي.")
        return

    await state.set_state(AddResponseState.waiting_for_trigger)
    await message.answer("📝 أرسل الكلمة أو العبارة المحفّزة للرد:")


@router.message(AddResponseState.waiting_for_trigger)
async def add_response_set_trigger(message: Message, state: FSMContext) -> None:
    if not _is_main_admin(message):
        await state.clear()
        return

    trigger = (message.text or "").strip().lower()
    if not trigger:
        await message.answer("❌ الرجاء إرسال كلمة صالحة.")
        return

    if get_response(trigger):
        await message.answer("⚠️ هذا الرد موجود بالفعل، يمكنك تعديله من قائمة التعديل.")
        await state.clear()
        return

    await state.update_data(trigger_word=trigger)
    await state.set_state(AddResponseState.waiting_for_type)
    await message.answer(
        "اختر نوع الرد:",
        reply_markup=response_type_kb(),
    )


def _map_type_label(label: str) -> str | None:
    mapping = {
        "نص": "text",
        "صورة": "photo",
        "فيديو": "video",
        "صوت": "audio",
        "ملف": "document",
        "رابط": "link",
    }
    return mapping.get(label)


@router.message(AddResponseState.waiting_for_type)
async def add_response_set_type(message: Message, state: FSMContext) -> None:
    if not _is_main_admin(message):
        await state.clear()
        return

    label = (message.text or "").strip()
    rtype = _map_type_label(label)
    if not rtype:
        await message.answer("❌ الرجاء اختيار نوع صحيح (نص / صورة / فيديو / صوت / ملف / رابط).")
        return

    await state.update_data(response_type=rtype)
    await state.set_state(AddResponseState.waiting_for_content)

    if rtype == "text":
        await message.answer("✏️ أرسل الآن نص الرد:")
    elif rtype == "link":
        await message.answer("🔗 أرسل الآن الرابط الذي سيتم إرساله:")
    elif rtype == "photo":
        await message.answer("🖼 أرسل الآن الصورة المطلوبة:")
    elif rtype == "video":
        await message.answer("🎬 أرسل الآن الفيديو المطلوب:")
    elif rtype == "audio":
        await message.answer("🎧 أرسل الآن الملف الصوتي:")
    elif rtype == "document":
        await message.answer("📎 أرسل الآن الملف المطلوب:")


@router.message(AddResponseState.waiting_for_content)
async def add_response_save(message: Message, state: FSMContext) -> None:
    if not _is_main_admin(message):
        await state.clear()
        return

    data = await state.get_data()
    trigger = data.get("trigger_word")
    rtype = data.get("response_type")

    if not trigger or not rtype:
        await message.answer("حدث خطأ، حاول من جديد.")
        await state.clear()
        return

    content_str: str | None = None

    if rtype in ("text", "link"):
        if not message.text:
            await message.answer("❌ الرجاء إرسال نص صالح.")
            return
        content_str = message.text
    else:
        file_obj = None
        if rtype == "photo" and message.photo:
            file_obj = message.photo[-1]
        elif rtype == "video" and message.video:
            file_obj = message.video
        elif rtype == "audio" and (message.audio or message.voice):
            file_obj = message.audio or message.voice
        elif rtype == "document" and message.document:
            file_obj = message.document

        if not file_obj:
            await message.answer("❌ لم يتم العثور على ملف مناسب، حاول مرة أخرى.")
            return

        buf = BytesIO()
        await message.bot.download(file_obj, destination=buf)
        buf.seek(0)
        content_bytes = buf.read()
        content_str = encode_file_to_base64(content_bytes)

    add_response(trigger, rtype, content_str)
    await message.answer("✅ تم حفظ الرد بنجاح.")
    await state.clear()


# حذف رد


@router.message(F.text == "🗑 حذف رد", StateFilter(None))
async def delete_response_start(message: Message, state: FSMContext) -> None:
    logger.info(f"Response button pressed: {message.text} from user {message.from_user.id}")
    if not _is_main_admin(message):
        await message.answer("❌ هذه الميزة متاحة فقط للأدمن الرئيسي.")
        return

    await state.set_state(DeleteResponseState.waiting_for_trigger)
    await message.answer("🗑 أرسل الكلمة المحفزة للرد الذي تريد حذفه:")


@router.message(DeleteResponseState.waiting_for_trigger)
async def delete_response_finish(message: Message, state: FSMContext) -> None:
    if not _is_main_admin(message):
        await state.clear()
        return

    trigger = (message.text or "").strip().lower()
    if not trigger:
        await message.answer("❌ الرجاء إرسال كلمة صالحة.")
        return

    if not get_response(trigger):
        await message.answer("❌ لم يتم العثور على رد بهذه الكلمة.")
        await state.clear()
        return

    delete_response(trigger)
    await message.answer("✅ تم حذف الرد.")
    await state.clear()


# تعديل رد


@router.message(F.text == "✏️ تعديل رد", StateFilter(None))
async def edit_response_start(message: Message, state: FSMContext) -> None:
    logger.info(f"Response button pressed: {message.text} from user {message.from_user.id}")
    if not _is_main_admin(message):
        await message.answer("❌ هذه الميزة متاحة فقط للأدمن الرئيسي.")
        return

    await state.set_state(EditResponseState.waiting_for_trigger)
    await message.answer("✏️ أرسل الكلمة المحفزة للرد الذي تريد تعديله:")


@router.message(EditResponseState.waiting_for_trigger)
async def edit_response_choose_type(message: Message, state: FSMContext) -> None:
    if not _is_main_admin(message):
        await state.clear()
        return

    trigger = (message.text or "").strip().lower()
    if not trigger:
        await message.answer("❌ الرجاء إرسال كلمة صالحة.")
        return

    if not get_response(trigger):
        await message.answer("❌ لم يتم العثور على رد بهذه الكلمة.")
        await state.clear()
        return

    await state.update_data(trigger_word=trigger)
    await state.set_state(EditResponseState.waiting_for_type)
    await message.answer(
        "اختر نوع الرد الجديد:",
        reply_markup=response_type_kb(),
    )


@router.message(EditResponseState.waiting_for_type)
async def edit_response_set_type(message: Message, state: FSMContext) -> None:
    if not _is_main_admin(message):
        await state.clear()
        return

    label = (message.text or "").strip()
    rtype = _map_type_label(label)
    if not rtype:
        await message.answer("❌ الرجاء اختيار نوع صحيح (نص / صورة / فيديو / صوت / ملف / رابط).")
        return

    await state.update_data(response_type=rtype)
    await state.set_state(EditResponseState.waiting_for_content)

    if rtype == "text":
        await message.answer("✏️ أرسل الآن نص الرد الجديد:")
    elif rtype == "link":
        await message.answer("🔗 أرسل الآن الرابط الجديد:")
    elif rtype == "photo":
        await message.answer("🖼 أرسل الآن الصورة الجديدة:")
    elif rtype == "video":
        await message.answer("🎬 أرسل الآن الفيديو الجديد:")
    elif rtype == "audio":
        await message.answer("🎧 أرسل الآن الملف الصوتي الجديد:")
    elif rtype == "document":
        await message.answer("📎 أرسل الآن الملف الجديد:")


@router.message(EditResponseState.waiting_for_content)
async def edit_response_save(message: Message, state: FSMContext) -> None:
    if not _is_main_admin(message):
        await state.clear()
        return

    data = await state.get_data()
    trigger = data.get("trigger_word")
    rtype = data.get("response_type")

    if not trigger or not rtype:
        await message.answer("حدث خطأ، حاول من جديد.")
        await state.clear()
        return

    content_str: str | None = None

    if rtype in ("text", "link"):
        if not message.text:
            await message.answer("❌ الرجاء إرسال نص صالح.")
            return
        content_str = message.text
    else:
        file_obj = None
        if rtype == "photo" and message.photo:
            file_obj = message.photo[-1]
        elif rtype == "video" and message.video:
            file_obj = message.video
        elif rtype == "audio" and (message.audio or message.voice):
            file_obj = message.audio or message.voice
        elif rtype == "document" and message.document:
            file_obj = message.document

        if not file_obj:
            await message.answer("❌ لم يتم العثور على ملف مناسب، حاول مرة أخرى.")
            return

        buf = BytesIO()
        await message.bot.download(file_obj, destination=buf)
        buf.seek(0)
        content_bytes = buf.read()
        content_str = encode_file_to_base64(content_bytes)

    update_response_content(trigger, rtype, content_str)
    await message.answer("✅ تم تحديث الرد بنجاح.")
    await state.clear()
