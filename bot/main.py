"""봇 엔트리 포인트. Discord 봇과 FastAPI 서버를 동시에 실행한다."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import discord
import uvicorn
from discord.ext import commands
from fastapi import FastAPI
from loguru import logger

from bot.config import Settings, get_settings
from bot.services.api_client import ApplyHomeClient
from bot.services.database import Database

# --- 모듈 레벨 인스턴스 (main() 호출 시 초기화) ---
settings: Settings | None = None
api_client: ApplyHomeClient | None = None
db: Database | None = None

# --- Discord 봇 설정 ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


def _init_services() -> tuple[Settings, ApplyHomeClient, Database]:
    """설정 및 서비스 인스턴스를 초기화한다.

    Returns:
        (Settings, ApplyHomeClient, Database) 튜플
    """
    s = get_settings()
    a = ApplyHomeClient(s.data_go_kr_api_key, s.api_base_url)
    d = Database(s.database_path)
    return s, a, d


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI 앱 생명주기 관리."""
    yield


app = FastAPI(title="주택청약 봇 API", lifespan=lifespan)

from bot.api.health import router as health_router  # noqa: E402

app.include_router(health_router)
app.state.bot = bot


@bot.event
async def setup_hook() -> None:
    """봇 시작 시 서비스 초기화 및 cog 로드."""
    global settings, api_client, db

    settings, api_client, db = _init_services()

    await api_client.start()
    await db.init()

    bot.api_client = api_client  # type: ignore[attr-defined]
    bot.db = db  # type: ignore[attr-defined]
    bot.settings = settings  # type: ignore[attr-defined]

    extensions = [
        "bot.cogs.subscription",
        "bot.cogs.competition",
        "bot.cogs.statistics",
        "bot.cogs.notification",
        "bot.cogs.help",
    ]
    for ext in extensions:
        await bot.load_extension(ext)
        logger.info("확장 로드 완료: {}", ext)

    if settings.dev_guild_id:
        guild = discord.Object(id=settings.dev_guild_id)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        logger.info("개발 길드({}) 명령어 동기화 완료", settings.dev_guild_id)

    synced = await bot.tree.sync()
    logger.info("글로벌 슬래시 명령어 {}개 동기화 완료", len(synced))


@bot.event
async def on_ready() -> None:
    """봇이 준비되었을 때 호출된다."""
    logger.info(
        "봇 준비 완료 — 이름: {}, 길드 수: {}",
        bot.user,
        len(bot.guilds),
    )


async def run_bot() -> None:
    """Discord 봇을 실행한다. 종료 시 리소스를 정리한다."""
    try:
        s = settings
        if s is None:
            s, _, _ = _init_services()
        await bot.start(s.discord_token)
    finally:
        if api_client is not None:
            await api_client.close()
        if db is not None:
            await db.close()
        if not bot.is_closed():
            await bot.close()


async def run_api() -> None:
    """FastAPI 서버를 uvicorn으로 실행한다."""
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    """Discord 봇과 FastAPI 서버를 동시에 실행한다."""
    await asyncio.gather(run_bot(), run_api())


if __name__ == "__main__":
    asyncio.run(main())
