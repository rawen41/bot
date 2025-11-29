from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import MAIN_ADMIN_ID


def main_menu_kb(user_id: int) -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text="🌐 رابط المجموعة"),
            KeyboardButton(text="💬 الدعم الفني"),
        ],
        [
            KeyboardButton(text="🔗 رابط الإحالة الخاص بي"),
            KeyboardButton(text="📜 قانون المجموعة"),
        ],
        [
            KeyboardButton(text="🧮 إحصائياتي"),
            KeyboardButton(text="🎁 المكافآت"),
        ],
    ]

    if user_id == MAIN_ADMIN_ID:
        keyboard.append([KeyboardButton(text="🧰 لوحة التحكم")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="اختر من الأزرار بالأسفل 🌟",
    )


def admin_panel_kb() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="📂 إدارة الردود الجاهزة")],
        [KeyboardButton(text="👨‍💼 إدارة المدراء")],
        [KeyboardButton(text="📊 الإحالات و المكافآت")],
        [KeyboardButton(text="📢 رسالة للمجموعة")],
        [KeyboardButton(text="⚙️ إعدادات البوت")],
        [KeyboardButton(text="⬅️ رجوع للقائمة الرئيسية")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def response_type_kb() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="نص"), KeyboardButton(text="صورة")],
        [KeyboardButton(text="فيديو"), KeyboardButton(text="صوت")],
        [KeyboardButton(text="ملف"), KeyboardButton(text="رابط")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def responses_manage_kb() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="➕ إضافة رد جديد")],
        [KeyboardButton(text="✏️ تعديل رد"), KeyboardButton(text="🗑 حذف رد")],
        [KeyboardButton(text="⬅️ رجوع للوحة التحكم")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def managers_manage_kb() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="➕ إضافة مدير"), KeyboardButton(text="➖ حذف مدير")],
        [KeyboardButton(text="📋 قائمة المدراء")],
        [KeyboardButton(text="⬅️ رجوع للوحة التحكم")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
