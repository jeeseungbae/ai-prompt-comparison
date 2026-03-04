from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DATA_GO_KR_API_KEY = os.getenv("DATA_GO_KR_API_KEY", "")
NOTIFICATION_CHANNEL_ID = os.getenv("NOTIFICATION_CHANNEL_ID", "")
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/notifications.db")
BASE_URL = os.getenv("API_BASE_URL", "https://api.odcloud.kr/api")
POLLING_INTERVAL_MINUTES = int(os.getenv("POLLING_INTERVAL_MINUTES", "30"))
NOTIFICATION_CHECK_INTERVAL = POLLING_INTERVAL_MINUTES * 60
DEV_GUILD_ID = os.getenv("DEV_GUILD_ID", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

ENDPOINTS = {
    "announcement": "/ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail",
    "competition": "/ApplyhomeInfoCmpetRtSvc/v1/getAPTLttotPblancCmpet",
    "statistics": "/ApplyhomeStatSvc/v1/getAPTPrzwnerAreaStat",
}

EMBED_COLOR = 0x2B6CB0
ERROR_COLOR = 0xE53E3E
SUCCESS_COLOR = 0x38A169
