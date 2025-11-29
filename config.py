import os


# Simple configuration without pydantic
class SupabaseConfig:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "")
        self.key = os.getenv("SUPABASE_KEY", "")


class BotConfig:
    def __init__(self):
        self.token = "8063907641:AAEo6EyElmNEvuYcr-ol31GQDbR0HGpOQp8"
        self.username = "ar1nas_bot"
        self.group_invite_link = "https://t.me/+your_group_link"
        self.managed_group_id = -1002846994358
        self.support_username = "prohacker41"


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
