import discord
from discord.ext import commands
from loguru import logger

from bot.services.api_client import ApplyHomeAPI
from bot.services.database import Database


COGS = [
    "bot.cogs.subscription",
    "bot.cogs.competition",
    "bot.cogs.statistics",
    "bot.cogs.notification",
    "bot.cogs.help",
]


def create_bot() -> commands.Bot:
    intents = discord.Intents.default()

    bot = commands.Bot(
        command_prefix="!",
        intents=intents,
        help_command=None,
    )

    @bot.event
    async def on_ready():
        logger.info(f"봇 로그인 완료: {bot.user} (ID: {bot.user.id})")
        try:
            synced = await bot.tree.sync()
            logger.info(f"슬래시 명령어 {len(synced)}개 동기화 완료")
        except Exception as e:
            logger.error(f"명령어 동기화 실패: {e}")

    @bot.event
    async def setup_hook():
        bot.api = ApplyHomeAPI()
        await bot.api.start()

        bot.db = Database()
        await bot.db.init()

        for cog in COGS:
            try:
                await bot.load_extension(cog)
                logger.info(f"Cog 로드 완료: {cog}")
            except Exception as e:
                logger.error(f"Cog 로드 실패: {cog} - {e}")

        from bot.tasks.notification_checker import start_notification_checker

        start_notification_checker(bot)
        logger.info("알림 체크 백그라운드 태스크 시작")

    return bot


async def shutdown(bot: commands.Bot):
    """봇 서비스 정리"""
    logger.info("봇 종료 중...")
    if hasattr(bot, "api"):
        await bot.api.close()
    if hasattr(bot, "db"):
        await bot.db.close()
    logger.info("봇 종료 완료")
