from discord.ext import commands
from discord import app_commands
import discord
from loguru import logger

from bot.services.api_client import APIError
from bot.services import formatter


class CompetitionCog(commands.Cog):
    """청약 경쟁률 조회 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="경쟁률", description="청약 경쟁률을 조회합니다")
    async def competition_rate(self, interaction: discord.Interaction, 공고번호: str):
        """공고번호로 청약 경쟁률 조회"""
        await interaction.response.defer()
        try:
            logger.info(f"경쟁률 조회 - 공고번호: {공고번호} (사용자: {interaction.user})")
            data = await self.bot.api.get_competition_rate(announce_id=공고번호)
            embed = formatter.format_competition_rate(data)
            await interaction.followup.send(embed=embed)
        except APIError as e:
            logger.error(f"경쟁률 조회 실패: {e}")
            embed = formatter.format_error(f"경쟁률 조회 실패: {e}")
            await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(CompetitionCog(bot))
