import asyncio
import sys

from loguru import logger

from bot.config import DISCORD_TOKEN, LOG_LEVEL
from bot.main import create_bot, shutdown


def setup_logging():
    logger.remove()
    logger.add(
        sys.stderr,
        level=LOG_LEVEL,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )
    logger.add(
        "logs/bot_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
    )


async def main():
    setup_logging()
    logger.info("주택청약 정보 봇 시작")

    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN이 설정되지 않았습니다. .env 파일을 확인하세요.")
        sys.exit(1)

    bot = create_bot()
    try:
        await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("사용자에 의한 종료")
    finally:
        await shutdown(bot)
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
