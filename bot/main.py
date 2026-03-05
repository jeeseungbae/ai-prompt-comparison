from __future__ import annotations

import asyncio
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import discord
import uvicorn
from discord import app_commands
from discord.ext import commands
from fastapi import FastAPI
from loguru import logger

from bot.api.health import router as health_router
from bot.config import get_settings
from bot.services.api_client import ApplyHomeClient
from bot.services.database import Database

EXTENSIONS = [
    "bot.cogs.subscription",
    "bot.cogs.competition",
    "bot.cogs.statistics",
    "bot.cogs.notification",
    "bot.cogs.help",
]


def _create_bot() -> commands.Bot:
    """Discord 봇 인스턴스를 생성한다."""
    intents = discord.Intents.default()
    intents.message_content = True
    return commands.Bot(
        command_prefix="!",
        intents=intents,
        help_command=None,
    )


bot = _create_bot()


@bot.event
async def on_ready() -> None:
    """봇이 준비되면 로그를 출력한다."""
    logger.info("봇 로그인 완료: {} (서버 {}개)", bot.user, len(bot.guilds))


async def _init_services() -> None:
    """서비스를 초기화하고 봇에 연결한다."""
    settings = get_settings()

    # 로그 레벨 설정
    logger.remove()
    logger.add(sys.stderr, level=settings.log_level)

    # API 클라이언트
    api_client = ApplyHomeClient(
        api_key=settings.data_go_kr_api_key,
        base_url=settings.api_base_url,
    )
    await api_client.start()

    # 데이터베이스
    db = Database(settings.database_path)
    await db.init()

    # 봇에 서비스 연결
    bot.api_client = api_client  # type: ignore[attr-defined]
    bot.db = db  # type: ignore[attr-defined]
    bot.settings = settings  # type: ignore[attr-defined]

    logger.info("서비스 초기화 완료")


@bot.event
async def setup_hook() -> None:
    """봇 시작 시 서비스 초기화 및 Cog 로딩을 수행한다."""
    await _init_services()

    for ext in EXTENSIONS:
        await bot.load_extension(ext)
        logger.info("Extension 로드: {}", ext)

    settings = bot.settings  # type: ignore[attr-defined]
    if settings.dev_guild_id:
        guild = discord.Object(id=settings.dev_guild_id)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        logger.info("커맨드 트리 동기화 (dev guild: {})", settings.dev_guild_id)
    else:
        await bot.tree.sync()
        logger.info("커맨드 트리 글로벌 동기화")


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
) -> None:
    """슬래시 명령어의 예상 외 에러를 처리한다."""
    logger.error("명령어 실행 중 오류: {}", str(error))
    embed = discord.Embed(
        title="오류",
        description="예기치 않은 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        color=0xFF3333,
        timestamp=datetime.now(tz=timezone.utc),
    )
    embed.set_footer(text="주택청약 봇 | data.go.kr")
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """FastAPI 생명주기를 관리한다."""
    app.state.bot = bot
    yield


def _create_app() -> FastAPI:
    """FastAPI 앱을 생성한다."""
    app = FastAPI(
        title="주택청약 봇 API",
        lifespan=_lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.include_router(health_router)
    return app


async def _run_bot() -> None:
    """Discord 봇을 실행한다."""
    try:
        await bot.start(bot.settings.discord_token)  # type: ignore[attr-defined]
    finally:
        # 서비스 정리
        if hasattr(bot, "api_client"):
            await bot.api_client.close()  # type: ignore[attr-defined]
        if hasattr(bot, "db"):
            await bot.db.close()  # type: ignore[attr-defined]
        if not bot.is_closed():
            await bot.close()
        logger.info("봇 종료 완료")


async def _run_api() -> None:
    """FastAPI 서버를 실행한다."""
    app = _create_app()
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    """봇과 API 서버를 동시에 실행한다."""
    await asyncio.gather(_run_bot(), _run_api())


if __name__ == "__main__":
    asyncio.run(main())
