"""도움말 명령어 Cog."""

from __future__ import annotations

from datetime import datetime, timezone

import discord
from discord.ext import commands
from loguru import logger


class HelpCog(commands.Cog):
    """도움말 명령어 Cog.

    /도움말 명령어를 제공한다.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Cog 초기화."""
        self.bot = bot

    @commands.hybrid_command(name="도움말", description="봇 사용법을 안내합니다")
    async def 도움말(self, ctx: commands.Context) -> None:
        """봇의 전체 명령어 사용법을 안내하는 Embed를 전송한다."""
        embed = discord.Embed(
            title="📖 주택청약 봇 사용법",
            description="주택청약(아파트 분양) 정보를 실시간으로 조회하고 알림받는 봇입니다.",
            color=0x0066FF,
            timestamp=datetime.now(tz=timezone.utc),
        )
        embed.add_field(
            name="/청약 최신",
            value="최근 분양공고 5건을 조회합니다.",
            inline=False,
        )
        embed.add_field(
            name="/청약 검색 [키워드]",
            value="주택명 키워드로 분양공고를 검색합니다.\n예) `/청약 검색 래미안`",
            inline=False,
        )
        embed.add_field(
            name="/청약 상세 [공고번호]",
            value=(
                "주택관리번호(HOUSE_MANAGE_NO)로 공고 상세 정보를 조회합니다.\n"
                "예) `/청약 상세 2024000001`"
            ),
            inline=False,
        )
        embed.add_field(
            name="/경쟁률 [공고번호]",
            value="주택관리번호로 주택형별 경쟁률을 조회합니다.\n예) `/경쟁률 2024000001`",
            inline=False,
        )
        embed.add_field(
            name="/당첨통계 [지역]",
            value=(
                "지역별 당첨자 연령대 통계를 조회합니다. 지역을 생략하면 전체를 조회합니다.\n"
                "예) `/당첨통계 서울`"
            ),
            inline=False,
        )
        embed.add_field(
            name="/알림설정",
            value="현재 채널을 새 분양공고 알림 채널로 등록합니다.",
            inline=False,
        )
        embed.set_footer(text="주택청약 봇 | data.go.kr")
        logger.debug("도움말 명령어 호출 — user_id={}", ctx.author.id)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Cog를 봇에 등록한다."""
    await bot.add_cog(HelpCog(bot))
