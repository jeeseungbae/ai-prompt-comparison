"""알림 설정 및 새 공고 자동 체크 Cog."""

from __future__ import annotations

from datetime import datetime, timezone

import discord
from discord.ext import commands, tasks
from loguru import logger

from bot.services.api_client import APIError
from bot.services.formatter import format_announcement_summary


class NotificationCog(commands.Cog):
    """알림 설정 및 새 공고 자동 체크 Cog.

    /알림설정 명령어와 주기적 새 공고 체크 태스크를 제공한다.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Cog 초기화."""
        self.bot = bot

    def _error_embed(
        self,
        description: str = "API 호출에 실패했습니다. 잠시 후 다시 시도해주세요.",
    ) -> discord.Embed:
        """에러 Embed를 생성한다.

        Args:
            description: 에러 설명 메시지.

        Returns:
            에러 스타일 Embed 객체.
        """
        embed = discord.Embed(
            title="❌ 오류",
            description=description,
            color=0xFF3333,
            timestamp=datetime.now(tz=timezone.utc),
        )
        embed.set_footer(text="주택청약 봇 | data.go.kr")
        return embed

    @commands.hybrid_command(
        name="알림설정", description="현재 채널을 새 공고 알림 채널로 설정합니다"
    )
    async def 알림설정(self, ctx: commands.Context) -> None:
        """현재 채널을 새 분양공고 알림 채널로 등록한다."""
        await ctx.defer()
        if ctx.guild is None:
            await ctx.send(
                embed=self._error_embed("서버(길드) 채널에서만 알림을 설정할 수 있습니다.")
            )
            return
        try:
            await self.bot.db.set_notification_channel(ctx.guild.id, ctx.channel.id)
            embed = discord.Embed(
                title="✅ 알림 채널 설정 완료",
                description="이 채널이 새 공고 알림 채널로 설정되었습니다.",
                color=0x00CC66,
                timestamp=datetime.now(tz=timezone.utc),
            )
            embed.set_footer(text="주택청약 봇 | data.go.kr")
            logger.info(
                "알림 채널 설정 완료 — guild_id={}, channel_id={}",
                ctx.guild.id,
                ctx.channel.id,
            )
            await ctx.send(embed=embed)
        except Exception:
            logger.exception("알림 채널 설정 중 오류 발생 — guild_id={}", ctx.guild.id)
            await ctx.send(
                embed=self._error_embed("알림 채널 설정에 실패했습니다. 잠시 후 다시 시도해주세요.")
            )

    @tasks.loop(minutes=30)
    async def check_new_announcements(self) -> None:
        """새 분양공고를 주기적으로 체크하고 등록된 알림 채널에 전송한다.

        마지막으로 확인한 HOUSE_MANAGE_NO를 DB에 저장하여 신규 공고를 감지한다.
        최초 실행 시에는 기준값만 저장하고 알림을 전송하지 않는다.
        """
        try:
            last_id = await self.bot.db.get_state("last_house_manage_no")
            announcements = await self.bot.api_client.get_recent_announcements(count=20)

            if not announcements:
                logger.debug("새 공고 체크: 조회된 공고 없음")
                return

            newest_id = announcements[0].HOUSE_MANAGE_NO

            if last_id is None:
                # 최초 실행: 기준값만 저장하고 알림 전송 없이 종료
                await self.bot.db.set_state("last_house_manage_no", newest_id)
                logger.info("새 공고 체크 초기화 완료 — 기준 ID={}", newest_id)
                return

            new_announcements = [ann for ann in announcements if ann.HOUSE_MANAGE_NO > last_id]
            if not new_announcements:
                logger.debug("새 공고 없음 (last_id={})", last_id)
                return

            channels = await self.bot.db.get_notification_channels()
            if not channels:
                logger.debug("등록된 알림 채널 없음 — 알림 전송 생략")
                await self.bot.db.set_state("last_house_manage_no", newest_id)
                return

            for announcement in new_announcements:
                summary = format_announcement_summary(announcement)
                embed = discord.Embed(
                    title="🏠 새 분양공고",
                    color=0x0066FF,
                    timestamp=datetime.now(tz=timezone.utc),
                )
                for key, val in summary.items():
                    embed.add_field(name=key, value=val, inline=True)
                embed.set_footer(
                    text=(
                        f"주택청약 봇 | data.go.kr  |  "
                        f"상세 정보: /청약 상세 {announcement.HOUSE_MANAGE_NO}"
                    )
                )

                for guild_id, channel_id in channels:
                    channel = self.bot.get_channel(channel_id)
                    if channel is None:
                        logger.warning(
                            "알림 채널을 찾을 수 없음 — guild_id={}, channel_id={}",
                            guild_id,
                            channel_id,
                        )
                        continue
                    try:
                        await channel.send(embed=embed)  # type: ignore[union-attr]
                        logger.info(
                            "새 공고 알림 전송 완료 — channel_id={}, house={}",
                            channel_id,
                            announcement.HOUSE_NM,
                        )
                    except Exception:
                        logger.exception("알림 전송 실패 — channel_id={}", channel_id)

            await self.bot.db.set_state("last_house_manage_no", newest_id)
            logger.info("새 공고 {}건 처리 완료 — newest_id={}", len(new_announcements), newest_id)

        except APIError:
            logger.exception("새 공고 체크 중 API 오류 발생 — 다음 주기에 재시도")
        except Exception:
            logger.exception("새 공고 체크 중 예상치 못한 오류 발생 — 다음 주기에 재시도")

    @check_new_announcements.before_loop
    async def before_check_new_announcements(self) -> None:
        """봇이 준비될 때까지 루프 시작을 대기한다."""
        await self.bot.wait_until_ready()

    async def cog_load(self) -> None:
        """Cog 로드 시 인터벌을 설정에서 읽어 적용하고 태스크를 시작한다."""
        interval = self.bot.settings.check_interval_minutes
        if interval != 30:
            self.check_new_announcements.change_interval(minutes=interval)
            logger.info("새 공고 체크 인터벌 변경 — {}분", interval)
        self.check_new_announcements.start()
        logger.info("새 공고 체크 태스크 시작")

    async def cog_unload(self) -> None:
        """Cog 언로드 시 태스크를 취소한다."""
        self.check_new_announcements.cancel()
        logger.info("새 공고 체크 태스크 취소")


async def setup(bot: commands.Bot) -> None:
    """Cog를 봇에 등록한다."""
    await bot.add_cog(NotificationCog(bot))
