from __future__ import annotations

from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

EMBED_COLOR_INFO = 0x0066FF
FOOTER_TEXT = "주택청약 봇 | data.go.kr"


class HelpCog(commands.Cog):
    """봇 도움말 명령어."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="도움말", description="봇 사용법을 안내합니다")
    async def help_command(self, interaction: discord.Interaction) -> None:
        """봇 사용법을 안내한다."""
        embed = discord.Embed(
            title="주택청약 봇 사용 안내",
            description="주택청약(아파트 분양) 정보를 실시간으로 조회하고 알림받을 수 있습니다.",
            color=EMBED_COLOR_INFO,
            timestamp=datetime.now(tz=timezone.utc),
        )
        embed.add_field(
            name="/청약 최신",
            value="최근 분양공고 5건을 조회합니다.",
            inline=False,
        )
        embed.add_field(
            name="/청약 검색 [키워드]",
            value="주택명으로 분양공고를 검색합니다.\n예: `/청약 검색 힐스테이트`",
            inline=False,
        )
        embed.add_field(
            name="/청약 상세 [관리번호]",
            value="관리번호로 분양공고 상세 정보를 조회합니다.\n예: `/청약 상세 2024000123`",
            inline=False,
        )
        embed.add_field(
            name="/경쟁률 [관리번호]",
            value="주택형별 경쟁률을 조회합니다.\n예: `/경쟁률 2024000123`",
            inline=False,
        )
        embed.add_field(
            name="/당첨통계 [지역]",
            value="지역별 당첨자 연령대 통계를 조회합니다.\n예: `/당첨통계 서울`",
            inline=False,
        )
        embed.add_field(
            name="/알림설정",
            value="현재 채널을 새 분양공고 알림 채널로 설정합니다.",
            inline=False,
        )
        embed.add_field(
            name="/도움말",
            value="이 도움말을 표시합니다.",
            inline=False,
        )
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Cog를 봇에 등록한다."""
    await bot.add_cog(HelpCog(bot))
