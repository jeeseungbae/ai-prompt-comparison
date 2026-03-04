from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 설정. .env 파일에서 로드."""

    discord_token: str
    data_go_kr_api_key: str
    notification_channel_id: int
    database_path: str = "data/notifications.db"
    api_base_url: str = "https://api.odcloud.kr/api"
    polling_interval_minutes: int = 30
    dev_guild_id: int | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
