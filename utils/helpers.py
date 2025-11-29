import time
from typing import Dict, Tuple

from aiogram.types import Message
from aiogram.types.input_file import BufferedInputFile

from database.supabase import get_response, decode_base64_to_bytes


_last_trigger_times: Dict[Tuple[int, str], float] = {}


def is_spam(user_id: int, trigger: str, window_seconds: float = 5.0) -> bool:
    """منع التكرار السريع لنفس الكلمة من نفس العضو."""
    now = time.time()
    key = (user_id, trigger.lower())
    last = _last_trigger_times.get(key)
    if last and now - last < window_seconds:
        return True
    _last_trigger_times[key] = now
    return False


async def send_db_response(message: Message, trigger: str) -> bool:
    """إرسال الرد المناسب من قاعدة البيانات إذا وُجد."""
    trigger = (trigger or "").strip().lower()
    if not trigger or not message.from_user:
        return False

    if is_spam(message.from_user.id, trigger):
        return False

    resp = get_response(trigger)
    if not resp:
        return False

    rtype = resp.get("response_type")
    content = resp.get("content") or ""

    if rtype in ("text", "link"):
        await message.answer(content)
        return True

    if rtype in ("photo", "video", "audio", "document"):
        data = decode_base64_to_bytes(content)
        if rtype == "photo":
            await message.answer_photo(BufferedInputFile(data, filename="image.jpg"))
        elif rtype == "video":
            await message.answer_video(BufferedInputFile(data, filename="video.mp4"))
        elif rtype == "audio":
            await message.answer_audio(BufferedInputFile(data, filename="audio.mp3"))
        else:
            await message.answer_document(BufferedInputFile(data, filename="file.bin"))
        return True

    return False
