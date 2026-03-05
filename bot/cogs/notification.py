from __future__ import annotations

from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands, tasks
from loguru import logger

from bot.services import APIError, format_announcement_summary

EMBED_COLOR_INFO = 0x0066FF
EMBED_COLOR_ERROR = 0xFF3333
EMBED_COLOR_SUCCESS = 0x00CC66
FOOTER_TEXT = "주택청약 봇 | data.go.kr"

LAST_HOUSE_MANAGE_NO_KEY = "last_house_manage_no"


class NotificationCog(commands.Cog):
    """새 분양공고 알림 관리."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        """Cog 로드 시 스케줄러를 시작한다."""
        interval = self.bot.settings.check_interval_minutes  # type: ignore[attr-defined]
        self.check_new_announcements.change_interval(minutes=interval)
        self.check_new_announcements.start()
        logger.info("알림 스케줄러 시작 (주기: {}분)", interval)

    async def cog_unload(self) -> None:
        """Cog 언로드 시 스케줄러를 중지한다."""
        self.check_new_announcements.cancel()
        logger.info("알림 스케줄러 중지")

    @app_commands.command(name="알림설정", description="현재 채널을 새 공고 알림 채널로 설정합니다")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def set_notification(self, interaction: discord.Interaction) -> None:
        """현재 채널을 알림 채널로 등록한다."""
        await interaction.response.defer()

        if not interaction.guild:
            embed = discord.Embed(
                title="오류",
                description="이 명령어는 서버 채널에서만 사용할 수 있습니다.",
                color=EMBED_COLOR_ERROR,
                timestamp=datetime.now(tz=timezone.utc),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.followup.send(embed=embed)
            return

        await self.bot.db.set_notification_channel(  # type: ignore[attr-defined]
            interaction.guild.id, interaction.channel_id
        )

        embed = discord.Embed(
            title="알림 설정 완료",
            description=(
                f"이 채널(<#{interaction.channel_id}>)이 "
                f"새 분양공고 알림 채널로 설정되었습니다.\n\n"
                f"새로운 분양공고가 등록되면 자동으로 알림을 보내드립니다."
            ),
            color=EMBED_COLOR_SUCCESS,
            timestamp=datetime.now(tz=timezone.utc),
        )
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.followup.send(embed=embed)

    @tasks.loop(minutes=30)
    async def check_new_announcements(self) -> None:
        """주기적으로 새 분양공고를 확인하고 알림을 발송한다."""
        try:
            announcements = await self.bot.api_client.get_recent_announcements(20)  # type: ignore[attr-defined]
        except APIError:
            logger.warning("새 공고 체크 실패, 다음 주기에 재시도합니다")
            return

        if not announcements:
            return

        last_id = await self.bot.db.get_state(LAST_HOUSE_MANAGE_NO_KEY)  # type: ignore[attr-defined]
        newest_id = announcements[0].HOUSE_MANAGE_NO

        # 첫 실행: 기준점만 저장하고 알림 안 보냄 (flooding 방지)
        if last_id is None:
            await self.bot.db.set_state(LAST_HOUSE_MANAGE_NO_KEY, newest_id)  # type: ignore[attr-defined]
            logger.info("첫 실행 — 기준점 저장: {}", newest_id)
            return

        # 신규 공고 필터링
        new_announcements = [a for a in announcements if a.HOUSE_MANAGE_NO > last_id]
        if not new_announcements:
            return

        logger.info("새 공고 {}건 감지", len(new_announcements))

        # 모든 알림 채널에 전송
        channels = await self.bot.db.get_notification_channels()  # type: ignore[attr-defined]
        for guild_id, channel_id in channels:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.warning("채널을 찾을 수 없음: guild={}, channel={}", guild_id, channel_id)
                continue

            for announcement in new_announcements:
                summary = format_announcement_summary(announcement)
                embed = discord.Embed(
                    title="🏠 새 분양공고",
                    color=EMBED_COLOR_SUCCESS,
                    timestamp=datetime.now(tz=timezone.utc),
                )
                embed.add_field(name="주택명", value=summary["주택명"], inline=False)
                embed.add_field(name="지역", value=summary["지역"], inline=True)
                embed.add_field(name="모집공고일", value=summary["모집공고일"], inline=True)
                embed.add_field(
                    name="상세 조회",
                    value=f"`/청약 상세 {summary['관리번호']}`",
                    inline=False,
                )
                embed.set_footer(text=FOOTER_TEXT)
                try:
                    await channel.send(embed=embed)  # type: ignore[union-attr]
                except discord.HTTPException:
                    logger.warning("알림 전송 실패: guild={}, channel={}", guild_id, channel_id)

        # 기준점 갱신
        await self.bot.db.set_state(LAST_HOUSE_MANAGE_NO_KEY, newest_id)  # type: ignore[attr-defined]

    @check_new_announcements.before_loop
    async def before_check(self) -> None:
        """봇이 준비될 때까지 대기한다."""
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    """Cog를 봇에 등록한다."""
    await bot.add_cog(NotificationCog(bot))
