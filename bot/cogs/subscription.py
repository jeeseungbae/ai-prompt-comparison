from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

if TYPE_CHECKING:
    from bot.services.api_client import ApplyHomeClient

from bot.services.formatter import format_announcement_list_embed


class SubscriptionCog(commands.Cog):
    """청약정보 조회 명령어."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @property
    def api_client(self) -> ApplyHomeClient:
        return self.bot.api_client  # type: ignore[attr-defined]

    @app_commands.command(name="청약정보", description="최근 APT 분양정보를 조회합니다")
    @app_commands.describe(지역="조회할 지역 (예: 서울, 경기, 부산). 미입력시 전체 조회")
    async def subscription_info(
        self, interaction: discord.Interaction, 지역: str | None = None
    ) -> None:
        await interaction.response.defer()
        try:
            announcements = await self.api_client.get_apt_announcements(region=지역)
            embed = format_announcement_list_embed(announcements, region=지역)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"청약정보 조회 에러: {e}")
            await interaction.followup.send(
                "일시적으로 청약정보를 조회할 수 없습니다. 잠시 후 다시 시도해주세요.",
                ephemeral=True,
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SubscriptionCog(bot))
