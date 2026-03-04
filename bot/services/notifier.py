from __future__ import annotations

from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands, tasks
from loguru import logger

from bot.services.api_client import ApplyHomeClient
from bot.services.database import NotificationDB
from bot.services.formatter import format_announcement_embed


class NotifierCog(commands.Cog):
    """신규 분양공고를 자동으로 감지하여 알림을 보내는 Cog."""

    def __init__(
        self,
        bot: commands.Bot,
        api_client: ApplyHomeClient,
        db: NotificationDB,
        channel_id: int,
        polling_minutes: int = 30,
    ) -> None:
        self.bot = bot
        self.api_client = api_client
        self.db = db
        self.channel_id = channel_id
        # 폴링 주기를 동적으로 설정
        self.poll_new_announcements.change_interval(minutes=polling_minutes)
        self.poll_new_announcements.start()

    def cog_unload(self) -> None:
        self.poll_new_announcements.cancel()

    @tasks.loop(minutes=30)
    async def poll_new_announcements(self) -> None:
        """신규 분양공고를 확인하고 알림을 보냅니다."""
        logger.debug("분양공고 폴링 시작")
        try:
            # 최근 7일간의 공고를 조회
            now = datetime.now(timezone.utc)
            start_date = (now - timedelta(days=7)).strftime("%Y%m%d")
            end_date = now.strftime("%Y%m%d")

            announcements = await self.api_client.get_apt_announcements(
                start_date=start_date, end_date=end_date
            )

            if not announcements:
                logger.debug("새로운 분양공고 없음")
                return

            channel = self.bot.get_channel(self.channel_id)
            if channel is None:
                logger.error(f"알림 채널을 찾을 수 없음: {self.channel_id}")
                return

            new_count = 0
            for ann in announcements:
                if await self.db.is_notified(ann.PBLANC_NO):
                    continue

                embed = format_announcement_embed(ann)
                await channel.send(
                    content="새로운 APT 분양공고가 등록되었습니다!",
                    embed=embed,
                )
                await self.db.mark_notified(ann.PBLANC_NO, ann.HOUSE_NM)
                new_count += 1
                logger.info(f"신규 분양 알림 전송: {ann.HOUSE_NM} ({ann.PBLANC_NO})")

            if new_count > 0:
                logger.info(f"총 {new_count}건의 신규 분양 알림 전송 완료")

        except Exception as e:
            logger.error(f"분양공고 폴링 중 에러: {e}")

    @poll_new_announcements.before_loop
    async def before_poll(self) -> None:
        """봇이 준비될 때까지 대기합니다."""
        await self.bot.wait_until_ready()
        logger.info("분양공고 폴링 시작 대기 완료")

    @poll_new_announcements.error
    async def poll_error(self, error: Exception) -> None:
        """폴링 에러를 로깅합니다."""
        logger.error(f"분양공고 폴링 태스크 에러: {error}")
