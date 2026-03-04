from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

if TYPE_CHECKING:
    from bot.services.api_client import ApplyHomeClient

from bot.services.formatter import format_winner_stats_embed


class StatsCog(commands.Cog):
    """당첨자 통계 조회 명령어."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @property
    def api_client(self) -> ApplyHomeClient:
        return self.bot.api_client  # type: ignore[attr-defined]

    @app_commands.command(name="당첨통계", description="청약 당첨자 통계를 조회합니다")
    @app_commands.describe(
        기간="조회 기간 (예: 202401-202412). 미입력시 최근 6개월"
    )
    async def winner_stats(
        self, interaction: discord.Interaction, 기간: str | None = None
    ) -> None:
        await interaction.response.defer()
        try:
            if 기간 and "-" in 기간:
                parts = 기간.split("-")
                start_month = parts[0].strip()
                end_month = parts[1].strip()
            else:
                # 기본값: 최근 6개월
                now = datetime.now(timezone.utc)
                end_month = now.strftime("%Y%m")
                start_date = now.replace(month=now.month - 6) if now.month > 6 else now.replace(year=now.year - 1, month=now.month + 6)
                start_month = start_date.strftime("%Y%m")

            period_display = f"{start_month[:4]}.{start_month[4:]} ~ {end_month[:4]}.{end_month[4:]}"

            area_stats = await self.api_client.get_winner_stats_by_area(
                start_month, end_month
            )
            age_stats = await self.api_client.get_winner_stats_by_age(
                start_month, end_month
            )

            embed = format_winner_stats_embed(area_stats, age_stats, period=period_display)
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"당첨통계 조회 에러: {e}")
            await interaction.followup.send(
                "일시적으로 당첨통계를 조회할 수 없습니다. 잠시 후 다시 시도해주세요.",
                ephemeral=True,
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StatsCog(bot))
