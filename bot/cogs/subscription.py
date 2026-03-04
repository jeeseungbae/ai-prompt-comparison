from discord.ext import commands
from discord import app_commands
import discord
from loguru import logger

from bot.services.api_client import APIError
from bot.services import formatter


class SubscriptionCog(commands.Cog):
    """청약 정보 조회 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    subscription = app_commands.Group(name="청약", description="청약 정보 조회")

    @subscription.command(name="최신", description="최신 분양 공고를 조회합니다")
    async def latest(self, interaction: discord.Interaction, 페이지: int = 1):
        """최신 분양 공고 목록 조회"""
        await interaction.response.defer()
        try:
            logger.info(f"청약 최신 조회 - 페이지: {페이지} (사용자: {interaction.user})")
            data = await self.bot.api.get_announcements(page=페이지)
            embed = formatter.format_announcement_list(data)
            await interaction.followup.send(embed=embed)
        except APIError as e:
            logger.error(f"청약 최신 조회 실패: {e}")
            embed = formatter.format_error(f"API 조회 실패: {e}")
            await interaction.followup.send(embed=embed)

    @subscription.command(name="검색", description="분양 공고를 검색합니다")
    async def search(self, interaction: discord.Interaction, 키워드: str, 페이지: int = 1):
        """키워드로 분양 공고 검색"""
        await interaction.response.defer()
        try:
            logger.info(f"청약 검색 - 키워드: {키워드}, 페이지: {페이지} (사용자: {interaction.user})")
            data = await self.bot.api.search_announcements(keyword=키워드, page=페이지)
            embed = formatter.format_announcement_list(data)
            embed.title = f"🔍 '{키워드}' 검색 결과"
            await interaction.followup.send(embed=embed)
        except APIError as e:
            logger.error(f"청약 검색 실패: {e}")
            embed = formatter.format_error(f"검색 실패: {e}")
            await interaction.followup.send(embed=embed)

    @subscription.command(name="상세", description="분양 공고 상세 정보를 조회합니다")
    async def detail(self, interaction: discord.Interaction, 공고번호: str):
        """공고번호로 상세 정보 조회"""
        await interaction.response.defer()
        try:
            logger.info(f"청약 상세 조회 - 공고번호: {공고번호} (사용자: {interaction.user})")
            data = await self.bot.api.get_announcement_detail(announce_id=공고번호)
            embed = formatter.format_announcement_detail(data)
            await interaction.followup.send(embed=embed)
        except APIError as e:
            logger.error(f"청약 상세 조회 실패: {e}")
            embed = formatter.format_error(f"상세 조회 실패: {e}")
            await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(SubscriptionCog(bot))
