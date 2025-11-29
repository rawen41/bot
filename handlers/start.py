from aiogram import Router, F
from aiogram.types import Message


from config import bot_config
from utils.keyboards import main_menu_kb
from database.supabase import get_or_create_user, increment_referral
from database.supabase import has_reward_announcement_sent, mark_reward_sent

router = Router()


@router.message(F.chat.type == "private", F.text.startswith("/start"))
async def start_private(message: Message) -> None:
    """Handle any private message (no text commands, only buttons-based navigation).

    We also parse referral if the user opened bot with ?start=referrer_id
    """

    tg_id = message.from_user.id
    username = message.from_user.username

    # Referral: t.me/bot?start=123
    referrer_id = None
    if message.text and message.text.startswith("/start") and " " in message.text:
        payload = message.text.split(" ", 1)[1].strip()
        if payload.isdigit():
            referrer_id = int(payload)

    user = get_or_create_user(tg_id=tg_id, username=username, referred_by=referrer_id)
    is_new = bool(user.get("__created__"))

    # If referral is valid, not self-referral, and this is a new user -> count referral
    if referrer_id and referrer_id != tg_id and is_new:
        from database.supabase import get_user_stats

        new_count = increment_referral(referrer_id, user["id"])

        ref_stats = get_user_stats(referrer_id) or {}
        ref_username = ref_stats.get("username") or str(referrer_id)
        new_username = username or str(tg_id)

        await message.bot.send_message(
            chat_id=bot_config.managed_group_id,
            text=f"🎉 إحالة جديدة! 🌟\n\n"
                 f"👤 العضو: @{new_username}\n"
                 f"🤝 بواسطة: @{ref_username}\n"
                 f"🔢 إجمالي إحالات @{ref_username}: {new_count}\n\n"
                 f"🚀 استمر في النجاح! 💪"
        )

        if new_count >= 100 and not has_reward_announcement_sent(referrer_id):
            await message.bot.send_message(
                chat_id=bot_config.managed_group_id,
                text=f"🏆 مبروك @{ref_username}! تحصلت على الجائزة (متجر إلكتروني جاهز) 🎉",
            )
            mark_reward_sent(referrer_id)

    text = (
        "🔹 مرحبًا بك في بوت Arinas Helper!\n\n"
        "⚙️ استخدم الأزرار الموجودة في الأسفل للتنقل في البوت 🌟\n"
        "👇👇👇"
    )

    await message.answer(text, reply_markup=main_menu_kb(tg_id))


@router.message(F.chat.type == "private")
async def handle_main_menu_buttons(message: Message) -> None:
    text = (message.text or "").strip()
    tg_id = message.from_user.id

    if text == "🌐 رابط المجموعة":
        await message.answer(
            f"🌐 رابط الانضمام للمجموعة:\n{bot_config.group_invite_link}\n\n"
            "✨ لمزيد من النجاحات وفرص العمر، انضم لفريقنا اليوم! 🚀\n"
            "نحن هنا لندعمك ونحقق معًا أهدافك! 💪🔥")

    elif text == "💬 الدعم الفني":
        await message.answer(
            f"💬 للتواصل مع الدعم الفني:\n{bot_config.support_username}")

    elif text == "🔗 رابط الإحالة الخاص بي":
        link = f"https://t.me/{bot_config.bot_username.lstrip('@')}?start={tg_id}"
        await message.answer(
            "🔗 رابط الإحالة الخاص بك:\n"
            f"{link}\n\n"
            "📌 شارك هذا الرابط مع أصدقائك لتحصل على إحالات ومكافآت!"
        )

    elif text == "📜 قانون المجموعة":
        await message.answer(
            "📜 قانون المجموعة:\n"
            "1️⃣ الاحترام المتبادل بين جميع الأعضاء.\n"
            "2️⃣ يمنع السب والشتم والإعلانات العشوائية.\n"
            "3️⃣ الالتزام بتعليمات الإدارة.\n"
        )

    elif text == "🧮 إحصائياتي":
        from database.supabase import get_user_stats, get_user_referrals

        stats = get_user_stats(tg_id)
        if not stats:
            await message.answer("لم يتم العثور على بياناتك بعد.")
            return
        
        referrals = get_user_referrals(tg_id)
        referral_names = []
        for ref in referrals:
            name = ref.get("username")
            if name:
                referral_names.append(f"@{name}")
            else:
                referral_names.append(f"مستخدم {ref['tg_id']}")
        
        names_text = "\n".join(referral_names) if referral_names else "لا توجد إحالات بعد"
        
        await message.answer(
            "🧮 إحصائياتك:\n\n"
            f"👤 المعرف: @{message.from_user.username or 'بدون'}\n"
            f"🔗 عدد الإحالات الناجحة: {stats.get('referral_count', 0)}\n\n"
            f"👥 قائمة إحالاتك:\n{names_text}"
        )

    elif text == "🎁 المكافآت":
        from database.supabase import get_user_stats

        stats = get_user_stats(tg_id)
        count = stats.get("referral_count", 0) if stats else 0
        status = "✅ مؤهل" if count >= 100 else "❌ غير مؤهل بعد"
        await message.answer(
            "🎁 نظام المكافآت:\n\n"
            "كل عضو يصل إلى 100 إحالة ناجحة يحصل على:\n"
            "🏆 متجر إلكتروني جاهز 🎉\n\n"
            f"🔗 إحالاتك الحالية: {count}\n"
            f"📌 حالتك: {status}"
        )

    elif text == "🧰 لوحة التحكم":
        from config import MAIN_ADMIN_ID
        from utils.keyboards import admin_panel_kb

        if tg_id != MAIN_ADMIN_ID:
            return
        await message.answer("🧰 لوحة تحكم الأدمن الرئيسي:", reply_markup=admin_panel_kb())

