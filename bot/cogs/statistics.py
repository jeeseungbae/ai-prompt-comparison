from __future__ import annotations

from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from bot.services import APIError, format_winner_statistics

EMBED_COLOR_INFO = 0x0066FF
EMBED_COLOR_ERROR = 0xFF3333
FOOTER_TEXT = "주택청약 봇 | data.go.kr"


class StatisticsCog(commands.Cog):
    """당첨통계 조회 명령어."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="당첨통계", description="지역별 당첨자 연령대 통계를 조회합니다")
    @app_commands.describe(region="조회할 지역명 (예: 서울, 경기). 미입력 시 전체 조회")
    async def statistics(self, interaction: discord.Interaction, region: str | None = None) -> None:
        """지역별 당첨자 통계를 조회한다."""
        await interaction.response.defer()
        try:
            stats = await self.bot.api_client.get_winner_statistics(region)  # type: ignore[attr-defined]
        except APIError as e:
            logger.error("당첨통계 조회 실패: region={}", region)
            embed = discord.Embed(
                title="오류",
                description=str(e),
                color=EMBED_COLOR_ERROR,
                timestamp=datetime.now(tz=timezone.utc),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.followup.send(embed=embed)
            return

        if not stats:
            if region:
                desc = f"'{region}' 지역의 통계 데이터가 없습니다."
            else:
                desc = "통계 데이터가 없습니다."
            embed = discord.Embed(
                title="당첨통계",
                description=desc,
                color=EMBED_COLOR_INFO,
                timestamp=datetime.now(tz=timezone.utc),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.followup.send(embed=embed)
            return

        formatted = format_winner_statistics(stats)
        title = f"당첨통계 - {region}" if region else "당첨통계 - 전체"
        embed = discord.Embed(
            title=title,
            description=f"총 {len(formatted)}건",
            color=EMBED_COLOR_INFO,
            timestamp=datetime.now(tz=timezone.utc),
        )
        for item in formatted[:15]:
            embed.add_field(
                name=item["지역"],
                value=(
                    f"30대이하: {item['30대이하']}\n"
                    f"40대: {item['40대']}\n"
                    f"50대: {item['50대']}\n"
                    f"60대이상: {item['60대이상']}"
                ),
                inline=True,
            )
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Cog를 봇에 등록한다."""
    await bot.add_cog(StatisticsCog(bot))
