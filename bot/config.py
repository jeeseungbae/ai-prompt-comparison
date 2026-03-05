from __future__ import annotations

import os

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Settings(BaseModel):
    """봇 설정을 관리하는 Pydantic 모델."""

    model_config = ConfigDict(extra="ignore")

    discord_token: str = Field(default="", repr=False)
    data_go_kr_api_key: str = Field(default="", repr=False)
    notification_channel_id: int | None = None
    check_interval_minutes: int = 30
    database_path: str = "./data/bot.db"
    log_level: str = "INFO"
    dev_guild_id: int | None = None
    api_base_url: str = "https://api.odcloud.kr/api"

    @model_validator(mode="before")
    @classmethod
    def _load_from_env(cls, values: object) -> dict[str, object]:
        """환경변수에서 설정값을 로딩한다."""
        env_map: dict[str, str] = {
            "discord_token": "DISCORD_TOKEN",
            "data_go_kr_api_key": "DATA_GO_KR_API_KEY",
            "notification_channel_id": "NOTIFICATION_CHANNEL_ID",
            "check_interval_minutes": "CHECK_INTERVAL_MINUTES",
            "database_path": "DATABASE_PATH",
            "log_level": "LOG_LEVEL",
            "dev_guild_id": "DEV_GUILD_ID",
            "api_base_url": "API_BASE_URL",
        }
        int_fields = {"notification_channel_id", "check_interval_minutes", "dev_guild_id"}
        result: dict[str, object] = {}

        for field_name, env_key in env_map.items():
            env_val = os.environ.get(env_key, "")
            if not env_val:
                continue
            if field_name in int_fields:
                result[field_name] = int(env_val)
            else:
                result[field_name] = env_val

        # 필수 필드 검증
        if not result.get("discord_token"):
            raise ValueError("DISCORD_TOKEN 환경변수가 설정되지 않았습니다.")
        if not result.get("data_go_kr_api_key"):
            raise ValueError("DATA_GO_KR_API_KEY 환경변수가 설정되지 않았습니다.")

        return result


def get_settings() -> Settings:
    """환경변수를 로딩하고 Settings 인스턴스를 반환한다."""
    load_dotenv(override=False)
    settings = Settings.model_validate({})
    logger.info("설정 로딩 완료 (log_level={})", settings.log_level)
    return settings
