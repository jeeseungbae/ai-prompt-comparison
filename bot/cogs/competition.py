from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

if TYPE_CHECKING:
    from bot.services.api_client import ApplyHomeClient

from bot.services.formatter import format_competition_embed


class CompetitionCog(commands.Cog):
    """경쟁률 조회 명령어."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @property
    def api_client(self) -> ApplyHomeClient:
        return self.bot.api_client  # type: ignore[attr-defined]

    @app_commands.command(name="경쟁률", description="APT 청약 경쟁률을 조회합니다")
    @app_commands.describe(단지명="조회할 단지명 (예: 힐스테이트, 래미안)")
    async def competition_rate(
        self, interaction: discord.Interaction, 단지명: str
    ) -> None:
        await interaction.response.defer()
        try:
            # 먼저 단지명으로 분양정보를 검색하여 HOUSE_MANAGE_NO를 획득
            announcements = await self.api_client.search_apt_by_name(단지명)

            if not announcements:
                await interaction.followup.send(
                    f"'{단지명}'에 해당하는 분양정보를 찾을 수 없습니다.",
                    ephemeral=True,
                )
                return

            # 첫 번째 매칭 결과의 경쟁률을 조회
            ann = announcements[0]
            competitions = await self.api_client.get_apt_competition(
                house_manage_no=ann.HOUSE_MANAGE_NO,
                pblanc_no=ann.PBLANC_NO,
            )

            embed = format_competition_embed(ann.HOUSE_NM, competitions)
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"경쟁률 조회 에러: {e}")
            await interaction.followup.send(
                "일시적으로 경쟁률을 조회할 수 없습니다. 잠시 후 다시 시도해주세요.",
                ephemeral=True,
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CompetitionCog(bot))
