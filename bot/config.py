"""봇 설정 모듈. .env 파일에서 환경변수를 로드하여 Settings 인스턴스를 제공한다."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, ConfigDict, model_validator


def _load_env() -> None:
    """프로젝트 루트의 .env 파일을 로드한다."""
    loaded = load_dotenv(override=False)
    if loaded:
        logger.debug(".env 파일 로드 완료")
    else:
        logger.debug(".env 파일 없음 — 시스템 환경변수 사용")


class Settings(BaseModel):
    """애플리케이션 전체 설정.

    .env 또는 시스템 환경변수에서 값을 읽어온다.
    필수 항목(discord_token, data_go_kr_api_key)이 없으면 ValueError를 발생시킨다.
    """

    model_config = ConfigDict(extra="ignore")

    # --- 필수 항목 ---
    discord_token: str
    """디스코드 봇 토큰 (필수)"""

    data_go_kr_api_key: str
    """data.go.kr API 인증키 (필수, URL-encoded)"""

    # --- 선택 항목 (기본값 있음) ---
    notification_channel_id: int | None = None
    """새 공고 알림을 전송할 디스코드 채널 ID"""

    check_interval_minutes: int = 30
    """새 공고 체크 주기(분)"""

    database_path: str = "./data/bot.db"
    """SQLite 데이터베이스 파일 경로"""

    log_level: str = "INFO"
    """로그 레벨 (DEBUG / INFO / WARNING / ERROR)"""

    dev_guild_id: int | None = None
    """개발용 길드 ID — 슬래시 커맨드 즉시 동기화 목적"""

    api_base_url: str = "https://api.odcloud.kr/api"
    """data.go.kr API 베이스 URL"""

    @model_validator(mode="before")
    @classmethod
    def _load_from_env(cls, values: object) -> dict[str, object]:
        """환경변수에서 설정값을 읽어 딕셔너리로 반환한다."""
        if isinstance(values, dict) and values:
            # 명시적으로 값을 전달받은 경우 그대로 사용 (테스트 용도)
            return values  # type: ignore[return-value]

        raw: dict[str, object] = {}

        def _get(key: str) -> str | None:
            return os.environ.get(key) or None

        def _get_int(key: str) -> int | None:
            val = _get(key)
            if val is None:
                return None
            try:
                return int(val)
            except ValueError:
                logger.warning(
                    "환경변수 {}의 값 '{}'을 정수로 변환할 수 없습니다. 무시합니다.", key, val
                )
                return None

        discord_token = _get("DISCORD_TOKEN")
        if not discord_token:
            raise ValueError("환경변수 DISCORD_TOKEN이 설정되지 않았습니다.")
        raw["discord_token"] = discord_token

        api_key = _get("DATA_GO_KR_API_KEY")
        if not api_key:
            raise ValueError("환경변수 DATA_GO_KR_API_KEY가 설정되지 않았습니다.")
        raw["data_go_kr_api_key"] = api_key

        notification_channel_id = _get_int("NOTIFICATION_CHANNEL_ID")
        if notification_channel_id is not None:
            raw["notification_channel_id"] = notification_channel_id

        check_interval = _get_int("CHECK_INTERVAL_MINUTES")
        if check_interval is not None:
            raw["check_interval_minutes"] = check_interval

        database_path = _get("DATABASE_PATH")
        if database_path:
            raw["database_path"] = database_path

        log_level = _get("LOG_LEVEL")
        if log_level:
            raw["log_level"] = log_level

        dev_guild_id = _get_int("DEV_GUILD_ID")
        if dev_guild_id is not None:
            raw["dev_guild_id"] = dev_guild_id

        api_base_url = _get("API_BASE_URL")
        if api_base_url:
            raw["api_base_url"] = api_base_url

        return raw


def get_settings() -> Settings:
    """설정 인스턴스를 반환한다.

    .env 파일을 로드한 뒤 Settings를 생성한다.
    필수 환경변수가 없으면 ValueError가 발생한다.
    """
    _load_env()
    settings = Settings.model_validate({})
    logger.info(
        "설정 로드 완료 — log_level={}, check_interval={}분, database_path={}",
        settings.log_level,
        settings.check_interval_minutes,
        settings.database_path,
    )
    return settings
