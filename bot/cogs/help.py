from discord.ext import commands
from discord import app_commands
import discord
from loguru import logger

from bot.config import EMBED_COLOR


class HelpCog(commands.Cog):
    """도움말 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="도움말", description="사용 가능한 명령어 목록을 표시합니다")
    async def help_command(self, interaction: discord.Interaction):
        """전체 명령어 도움말 표시"""
        logger.info(f"도움말 요청 (사용자: {interaction.user})")

        embed = discord.Embed(
            title="주택청약 봇 명령어 안내",
            description="아래는 사용 가능한 모든 명령어 목록입니다.",
            color=EMBED_COLOR,
        )

        embed.add_field(
            name="청약 공고 조회",
            value=(
                "`/청약 최신 [페이지]` - 최신 분양 공고 조회\n"
                "`/청약 검색 <키워드> [페이지]` - 분양 공고 검색\n"
                "`/청약 상세 <공고번호>` - 분양 공고 상세 정보"
            ),
            inline=False,
        )

        embed.add_field(
            name="통계 및 경쟁률",
            value=(
                "`/경쟁률 <공고번호>` - 청약 경쟁률 조회\n"
                "`/당첨통계 <공고번호>` - 당첨자 통계 조회"
            ),
            inline=False,
        )

        embed.add_field(
            name="알림 설정",
            value=(
                "`/알림설정 등록` - 새 공고 알림 채널 등록 (채널 관리 권한 필요)\n"
                "`/알림설정 해제` - 알림 채널 해제 (채널 관리 권한 필요)\n"
                "`/알림설정 확인` - 알림 설정 확인"
            ),
            inline=False,
        )

        embed.add_field(
            name="기타",
            value="`/도움말` - 명령어 도움말",
            inline=False,
        )

        embed.add_field(
            name="사용 예시",
            value=(
                "`/청약 최신` - 1페이지 최신 공고 조회\n"
                "`/청약 검색 강남 2` - '강남' 키워드로 2페이지 검색\n"
                "`/경쟁률 2024001234` - 공고번호 2024001234의 경쟁률 조회"
            ),
            inline=False,
        )

        embed.set_footer(text="주택청약 정보 봇 v1.0")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
