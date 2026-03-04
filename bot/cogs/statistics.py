"""당첨통계 조회 명령어 Cog."""

from __future__ import annotations

from datetime import datetime, timezone

import discord
from discord.ext import commands
from loguru import logger

from bot.services.api_client import APIError
from bot.services.formatter import format_winner_statistics


class StatisticsCog(commands.Cog):
    """당첨통계 조회 명령어 Cog.

    /당첨통계 명령어를 제공한다.
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

    @commands.hybrid_command(name="당첨통계", description="지역별 당첨자 연령대 통계를 조회합니다")
    async def 당첨통계(
        self,
        ctx: commands.Context,
        region: str | None = None,
    ) -> None:
        """지역별 당첨자 연령대 통계를 조회하여 Embed로 응답한다.

        Args:
            region: 조회할 청약지역명. None이면 전체 지역 조회.
        """
        await ctx.defer()
        try:
            statistics = await self.bot.api_client.get_winner_statistics(region=region)
            if not statistics:
                if region:
                    description = f"'{region}' 지역의 당첨 통계가 없습니다."
                else:
                    description = "당첨 통계가 없습니다."
                embed = discord.Embed(
                    title="📈 당첨통계",
                    description=description,
                    color=0x0066FF,
                    timestamp=datetime.now(tz=timezone.utc),
                )
                embed.set_footer(text="주택청약 봇 | data.go.kr")
                await ctx.send(embed=embed)
                return

            formatted_list = format_winner_statistics(statistics)
            title = f"📈 당첨통계: {region}" if region else "📈 당첨통계 (전체)"
            embed = discord.Embed(
                title=title,
                color=0x0066FF,
                timestamp=datetime.now(tz=timezone.utc),
            )
            for item in formatted_list:
                area = item.get("지역", "-")
                value_parts = [f"**{key}**: {val}" for key, val in item.items() if key != "지역"]
                value = "\n".join(value_parts) if value_parts else "-"
                embed.add_field(name=area, value=value, inline=True)
            embed.set_footer(text="주택청약 봇 | data.go.kr")
            logger.info(
                "당첨통계 조회 완료 (region={}, {}건)",
                region if region else "전체",
                len(statistics),
            )
            await ctx.send(embed=embed)
        except APIError:
            logger.exception("당첨통계 조회 중 API 오류 발생 (region={})", region)
            await ctx.send(embed=self._error_embed())


async def setup(bot: commands.Bot) -> None:
    """Cog를 봇에 등록한다."""
    await bot.add_cog(StatisticsCog(bot))
