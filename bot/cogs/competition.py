from __future__ import annotations

from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from bot.services import APIError, format_competition_rates

EMBED_COLOR_INFO = 0x0066FF
EMBED_COLOR_ERROR = 0xFF3333
FOOTER_TEXT = "주택청약 봇 | data.go.kr"


class CompetitionCog(commands.Cog):
    """경쟁률 조회 명령어."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="경쟁률", description="관리번호로 주택형별 경쟁률을 조회합니다")
    @app_commands.describe(id="주택관리번호")
    async def competition(self, interaction: discord.Interaction, id: str) -> None:
        """주택형별 경쟁률을 조회한다."""
        await interaction.response.defer()
        try:
            rates = await self.bot.api_client.get_competition_rates(id)  # type: ignore[attr-defined]
        except APIError as e:
            logger.error("경쟁률 조회 실패: id={}", id)
            embed = discord.Embed(
                title="오류",
                description=str(e),
                color=EMBED_COLOR_ERROR,
                timestamp=datetime.now(tz=timezone.utc),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.followup.send(embed=embed)
            return

        if not rates:
            embed = discord.Embed(
                title="경쟁률 조회",
                description=f"관리번호 '{id}'에 대한 경쟁률 정보가 없습니다.",
                color=EMBED_COLOR_INFO,
                timestamp=datetime.now(tz=timezone.utc),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.followup.send(embed=embed)
            return

        formatted = format_competition_rates(rates)
        embed = discord.Embed(
            title=f"경쟁률 (관리번호: {id})",
            description=f"총 {len(formatted)}개 주택형",
            color=EMBED_COLOR_INFO,
            timestamp=datetime.now(tz=timezone.utc),
        )
        for item in formatted:
            embed.add_field(
                name=f"주택형 {item['주택형']}",
                value=(
                    f"**공급세대**: {item['공급세대']}\n"
                    f"**신청건수**: {item['신청건수']}\n"
                    f"**경쟁률**: {item['경쟁률']}"
                ),
                inline=True,
            )
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Cog를 봇에 등록한다."""
    await bot.add_cog(CompetitionCog(bot))
