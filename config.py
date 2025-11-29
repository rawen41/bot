import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class BotConfig:
    bot_token: str
    bot_username: str
    main_admin_id: int
    support_username: str
    managed_group_id: int
    group_invite_link: str


@dataclass
class SupabaseConfig:
    url: str
    key: str

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8063907641:AAFmre8HFV32Og1qNbmcmCfSYKoJfjyCtGc")
BOT_USERNAME = os.getenv("BOT_USERNAME", "@ar1nas_bot")
MAIN_ADMIN_ID = int(os.getenv("MAIN_ADMIN_ID", "7112140383"))
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@prohacker41")
MANAGED_GROUP_ID = int(os.getenv("MANAGED_GROUP_ID", "-1002846994358"))
GROUP_INVITE_LINK = os.getenv("GROUP_INVITE_LINK", "https://t.me/+eNwR-cX_ZRxmMGRk")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

bot_config = BotConfig(
    bot_token=BOT_TOKEN,
    bot_username=BOT_USERNAME,
    main_admin_id=MAIN_ADMIN_ID,
    support_username=SUPPORT_USERNAME,
    managed_group_id=MANAGED_GROUP_ID,
    group_invite_link=GROUP_INVITE_LINK,
)

supabase_config = SupabaseConfig(url=SUPABASE_URL, key=SUPABASE_KEY)
