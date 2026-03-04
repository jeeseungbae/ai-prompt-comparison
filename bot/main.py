from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

import discord
import uvicorn
from discord.ext import commands
from fastapi import FastAPI
from loguru import logger

from bot.api.health import router as health_router
from bot.config import Settings
from bot.services.api_client import ApplyHomeClient
from bot.services.database import NotificationDB
from bot.services.notifier import NotifierCog


def get_settings() -> Settings:
    """Settings를 lazy 로딩합니다."""
    return Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 라이프사이클: 봇과 서비스를 시작/종료합니다."""
    # === Startup ===
    settings = get_settings()
    logger.info("청약알리미 봇 시작 중...")

    # 데이터베이스 초기화
    db = NotificationDB(settings.database_path)
    await db.init()

    # API 클라이언트 생성
    api_client = ApplyHomeClient(settings.data_go_kr_api_key, settings.api_base_url)

    # 봇 설정
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="!", intents=intents)

    # 서비스를 봇 인스턴스에 주입 (Cog에서 접근용)
    bot.api_client = api_client  # type: ignore[attr-defined]
    bot.db = db  # type: ignore[attr-defined]
    bot.notification_channel_id = settings.notification_channel_id  # type: ignore[attr-defined]

    # FastAPI state에도 저장 (API 라우트에서 접근용)
    app.state.bot = bot
    app.state.db = db
    app.state.api_client = api_client

    async def setup_hook() -> None:
        """봇 시작 시 Cog를 로드하고 슬래시 명령어를 동기화합니다."""
        # 슬래시 명령어 Cog 로드
        await bot.load_extension("bot.cogs.subscription")
        await bot.load_extension("bot.cogs.competition")
        await bot.load_extension("bot.cogs.stats")
        logger.info("슬래시 명령어 Cog 로드 완료")

        # 알림 Cog 등록
        await bot.add_cog(
            NotifierCog(
                bot,
                api_client,
                db,
                settings.notification_channel_id,
                polling_minutes=settings.polling_interval_minutes,
            )
        )
        logger.info("알림 Cog 등록 완료")

        # 슬래시 명령어 동기화
        if settings.dev_guild_id:
            guild = discord.Object(id=settings.dev_guild_id)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            logger.info(f"개발 서버({settings.dev_guild_id})에 {len(synced)}개 명령어 동기화")
        else:
            synced = await bot.tree.sync()
            logger.info(f"글로벌 {len(synced)}개 명령어 동기화")

    bot.setup_hook = setup_hook  # type: ignore[assignment]

    @bot.event
    async def on_ready() -> None:
        logger.info(f"봇 로그인 완료: {bot.user} (ID: {bot.user.id})")  # type: ignore[union-attr]
        logger.info(f"참여 서버 수: {len(bot.guilds)}")

    # 봇을 백그라운드 태스크로 시작
    bot_task = asyncio.create_task(bot.start(settings.discord_token))

    yield

    # === Shutdown ===
    logger.info("청약알리미 봇 종료 중...")
    await bot.close()
    await api_client.close()
    await db.close()
    bot_task.cancel()
    logger.info("청약알리미 봇 종료 완료")


app = FastAPI(title="청약알리미 Bot API", lifespan=lifespan)
app.include_router(health_router)


if __name__ == "__main__":
    uvicorn.run("bot.main:app", host="0.0.0.0", port=8000)
