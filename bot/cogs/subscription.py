from __future__ import annotations

from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from bot.services import (
    APIError,
    format_announcement_detail,
    format_announcement_list,
)

EMBED_COLOR_INFO = 0x0066FF
EMBED_COLOR_ERROR = 0xFF3333
EMBED_COLOR_SUCCESS = 0x00CC66
FOOTER_TEXT = "주택청약 봇 | data.go.kr"


def _error_embed(message: str) -> discord.Embed:
    """에러 Embed를 생성한다."""
    embed = discord.Embed(
        title="오류",
        description=message,
        color=EMBED_COLOR_ERROR,
        timestamp=datetime.now(tz=timezone.utc),
    )
    embed.set_footer(text=FOOTER_TEXT)
    return embed


class SubscriptionCog(commands.Cog):
    """주택청약 분양공고 조회 명령어."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    청약 = app_commands.Group(name="청약", description="주택청약 분양공고 조회")

    @청약.command(name="최신", description="최근 분양공고 5건을 조회합니다")
    async def latest(self, interaction: discord.Interaction) -> None:
        """최근 분양공고 5건을 조회한다."""
        await interaction.response.defer()
        try:
            announcements = await self.bot.api_client.get_recent_announcements(5)  # type: ignore[attr-defined]
        except APIError as e:
            logger.error("최신 공고 조회 실패")
            await interaction.followup.send(embed=_error_embed(str(e)))
            return

        if not announcements:
            embed = discord.Embed(
                title="최근 분양공고",
                description="조회된 공고가 없습니다.",
                color=EMBED_COLOR_INFO,
                timestamp=datetime.now(tz=timezone.utc),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.followup.send(embed=embed)
            return

        formatted = format_announcement_list(announcements)
        embed = discord.Embed(
            title="최근 분양공고",
            description=f"총 {len(formatted)}건",
            color=EMBED_COLOR_INFO,
            timestamp=datetime.now(tz=timezone.utc),
        )
        for item in formatted:
            embed.add_field(
                name=item["주택명"],
                value=(
                    f"📍 {item['지역']}\n"
                    f"📅 모집공고일: {item['모집공고일']}\n"
                    f"🔢 관리번호: {item['관리번호']}"
                ),
                inline=False,
            )
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.followup.send(embed=embed)

    @청약.command(name="검색", description="주택명으로 분양공고를 검색합니다")
    @app_commands.describe(keyword="검색할 주택명 키워드")
    async def search(self, interaction: discord.Interaction, keyword: str) -> None:
        """주택명으로 분양공고를 검색한다."""
        await interaction.response.defer()
        try:
            announcements = await self.bot.api_client.search_announcements(keyword)  # type: ignore[attr-defined]
        except APIError as e:
            logger.error("공고 검색 실패: keyword={}", keyword)
            await interaction.followup.send(embed=_error_embed(str(e)))
            return

        if not announcements:
            embed = discord.Embed(
                title=f"'{keyword}' 검색 결과",
                description="일치하는 공고가 없습니다.",
                color=EMBED_COLOR_INFO,
                timestamp=datetime.now(tz=timezone.utc),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.followup.send(embed=embed)
            return

        formatted = format_announcement_list(announcements)
        embed = discord.Embed(
            title=f"'{keyword}' 검색 결과",
            description=f"총 {len(formatted)}건",
            color=EMBED_COLOR_INFO,
            timestamp=datetime.now(tz=timezone.utc),
        )
        for item in formatted[:10]:
            embed.add_field(
                name=item["주택명"],
                value=(
                    f"📍 {item['지역']}\n"
                    f"📅 모집공고일: {item['모집공고일']}\n"
                    f"🔢 관리번호: {item['관리번호']}"
                ),
                inline=False,
            )
        if len(formatted) > 10:
            embed.add_field(
                name="...",
                value=f"외 {len(formatted) - 10}건 (관리번호로 상세 조회하세요)",
                inline=False,
            )
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.followup.send(embed=embed)

    @청약.command(name="상세", description="관리번호로 분양공고 상세 정보를 조회합니다")
    @app_commands.describe(id="주택관리번호")
    async def detail(self, interaction: discord.Interaction, id: str) -> None:
        """관리번호로 분양공고 상세를 조회한다."""
        await interaction.response.defer()
        try:
            announcement = await self.bot.api_client.get_announcement_detail(id)  # type: ignore[attr-defined]
        except APIError as e:
            logger.error("공고 상세 조회 실패: id={}", id)
            await interaction.followup.send(embed=_error_embed(str(e)))
            return

        if not announcement:
            embed = discord.Embed(
                title="공고 상세",
                description=f"관리번호 '{id}'에 해당하는 공고를 찾을 수 없습니다.",
                color=EMBED_COLOR_INFO,
                timestamp=datetime.now(tz=timezone.utc),
            )
            embed.set_footer(text=FOOTER_TEXT)
            await interaction.followup.send(embed=embed)
            return

        detail_data = format_announcement_detail(announcement)
        embed = discord.Embed(
            title=detail_data["주택명"],
            color=EMBED_COLOR_INFO,
            timestamp=datetime.now(tz=timezone.utc),
        )
        for key, value in detail_data.items():
            if key == "주택명":
                continue
            embed.add_field(name=key, value=value, inline=True)
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Cog를 봇에 등록한다."""
    await bot.add_cog(SubscriptionCog(bot))
