import os
from pydantic_settings import BaseSettings
from pydantic import Field


class SupabaseConfig(BaseSettings):
    url: str = Field(..., env="SUPABASE_URL")
    key: str = Field(..., env="SUPABASE_KEY")


class BotConfig(BaseSettings):
    token: str = Field(default="8063907641:AAEo6EyElmNEvuYcr-ol31GQDbR0HGpOQp8")
    username: str = Field(default="ar1nas_bot")
    group_invite_link: str = Field(default="https://t.me/+your_group_link")
    managed_group_id: int = Field(default=-1002846994358)
    support_username: str = Field(default="prohacker41")


bot_config = BotConfig()
supabase_config = SupabaseConfig()

# Legacy compatibility
BOT_TOKEN = bot_config.token
BOT_USERNAME = bot_config.username
MAIN_ADMIN_ID = 7112140383
SUPPORT_USERNAME = bot_config.support_username
MANAGED_GROUP_ID = bot_config.managed_group_id
GROUP_INVITE_LINK = bot_config.group_invite_link
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
