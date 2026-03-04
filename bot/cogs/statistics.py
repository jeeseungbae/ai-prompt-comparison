from discord.ext import commands
from discord import app_commands
import discord
from loguru import logger

from bot.services.api_client import APIError
from bot.services import formatter


class StatisticsCog(commands.Cog):
    """당첨자 통계 조회 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="당첨통계", description="당첨자 통계를 조회합니다")
    async def winner_statistics(self, interaction: discord.Interaction, 공고번호: str):
        """공고번호로 당첨자 통계 조회"""
        await interaction.response.defer()
        try:
            logger.info(f"당첨통계 조회 - 공고번호: {공고번호} (사용자: {interaction.user})")
            data = await self.bot.api.get_winner_statistics(announce_id=공고번호)
            embed = formatter.format_winner_statistics(data)
            await interaction.followup.send(embed=embed)
        except APIError as e:
            logger.error(f"당첨통계 조회 실패: {e}")
            embed = formatter.format_error(f"당첨통계 조회 실패: {e}")
            await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(StatisticsCog(bot))
