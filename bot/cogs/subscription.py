"""분양공고 조회 명령어 Cog."""

from __future__ import annotations

from datetime import datetime, timezone

import discord
from discord.ext import commands
from loguru import logger

from bot.services.api_client import APIError
from bot.services.formatter import (
    format_announcement_detail,
    format_announcement_list,
)


class SubscriptionCog(commands.Cog):
    """분양공고 조회 명령어 Cog.

    /청약 최신, /청약 검색, /청약 상세 명령어를 제공한다.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Cog 초기화."""
        self.bot = bot

    def _error_embed(
        self,
        description: str = "API 호출에 실패했습니다. 잠시 후 다시 시도해주세요.",
    ) -> discord.Embed:
        """에러 Embed를 생성한다.

        Args:
            description: 에러 설명 메시지.

        Returns:
            에러 스타일 Embed 객체.
        """
        embed = discord.Embed(
            title="❌ 오류",
            description=description,
            color=0xFF3333,
            timestamp=datetime.now(tz=timezone.utc),
        )
        embed.set_footer(text="주택청약 봇 | data.go.kr")
        return embed

    청약 = commands.HybridGroup(name="청약", description="주택청약 분양공고 조회")

    @청약.command(name="최신", description="최근 분양공고 5건을 조회합니다")
    async def 최신(self, ctx: commands.Context) -> None:
        """최근 분양공고 5건을 조회하여 Embed로 응답한다."""
        await ctx.defer()
        try:
            announcements = await self.bot.api_client.get_recent_announcements(count=5)
            if not announcements:
                embed = discord.Embed(
                    title="📋 최근 분양공고",
                    description="조회된 분양공고가 없습니다.",
                    color=0x0066FF,
                    timestamp=datetime.now(tz=timezone.utc),
                )
                embed.set_footer(text="주택청약 봇 | data.go.kr")
                await ctx.send(embed=embed)
                return

            formatted_list = format_announcement_list(announcements)
            embed = discord.Embed(
                title="📋 최근 분양공고",
                color=0x0066FF,
                timestamp=datetime.now(tz=timezone.utc),
            )
            for item in formatted_list:
                name = item.get("주택명", "-")
                value_parts = [f"**{key}**: {val}" for key, val in item.items() if key != "주택명"]
                value = "\n".join(value_parts) if value_parts else "-"
                embed.add_field(name=name, value=value, inline=False)
            embed.set_footer(text="주택청약 봇 | data.go.kr")
            logger.info("최근 분양공고 {}건 조회 완료", len(announcements))
            await ctx.send(embed=embed)
        except APIError:
            logger.exception("최신 분양공고 조회 중 API 오류 발생")
            await ctx.send(embed=self._error_embed())

    @청약.command(name="검색", description="주택명으로 분양공고를 검색합니다")
    async def 검색(self, ctx: commands.Context, *, keyword: str) -> None:
        """주택명 키워드로 분양공고를 검색하여 Embed로 응답한다.

        Args:
            keyword: 검색할 주택명 키워드.
        """
        await ctx.defer()
        try:
            announcements = await self.bot.api_client.search_announcements(keyword)
            if not announcements:
                embed = discord.Embed(
                    title="🔍 분양공고 검색",
                    description=f"'{keyword}'에 해당하는 공고가 없습니다.",
                    color=0x0066FF,
                    timestamp=datetime.now(tz=timezone.utc),
                )
                embed.set_footer(text="주택청약 봇 | data.go.kr")
                await ctx.send(embed=embed)
                return

            formatted_list = format_announcement_list(announcements)
            embed = discord.Embed(
                title=f"🔍 분양공고 검색: {keyword}",
                color=0x0066FF,
                timestamp=datetime.now(tz=timezone.utc),
            )
            for item in formatted_list:
                name = item.get("주택명", "-")
                value_parts = [f"**{key}**: {val}" for key, val in item.items() if key != "주택명"]
                value = "\n".join(value_parts) if value_parts else "-"
                embed.add_field(name=name, value=value, inline=False)
            embed.set_footer(text="주택청약 봇 | data.go.kr")
            logger.info("분양공고 검색 '{}' — {}건 조회 완료", keyword, len(announcements))
            await ctx.send(embed=embed)
        except APIError:
            logger.exception("분양공고 검색 중 API 오류 발생 (keyword={})", keyword)
            await ctx.send(embed=self._error_embed())

    @청약.command(name="상세", description="공고번호로 상세 정보를 조회합니다")
    async def 상세(self, ctx: commands.Context, id: str) -> None:
        """공고번호(HOUSE_MANAGE_NO)로 분양공고 상세 정보를 조회하여 Embed로 응답한다.

        Args:
            id: 조회할 공고의 주택관리번호(HOUSE_MANAGE_NO).
        """
        await ctx.defer()
        try:
            announcement = await self.bot.api_client.get_announcement_detail(id)
            if announcement is None:
                embed = discord.Embed(
                    title="📄 분양공고 상세",
                    description="해당 공고를 찾을 수 없습니다.",
                    color=0x0066FF,
                    timestamp=datetime.now(tz=timezone.utc),
                )
                embed.set_footer(text="주택청약 봇 | data.go.kr")
                await ctx.send(embed=embed)
                return

            detail = format_announcement_detail(announcement)
            title = detail.get("주택명", announcement.HOUSE_NM)
            embed = discord.Embed(
                title=f"📄 {title}",
                color=0x0066FF,
                timestamp=datetime.now(tz=timezone.utc),
            )
            for key, val in detail.items():
                embed.add_field(name=key, value=val, inline=True)
            embed.set_footer(text="주택청약 봇 | data.go.kr")
            logger.info("분양공고 상세 조회 완료 (id={})", id)
            await ctx.send(embed=embed)
        except APIError:
            logger.exception("분양공고 상세 조회 중 API 오류 발생 (id={})", id)
            await ctx.send(embed=self._error_embed())


async def setup(bot: commands.Bot) -> None:
    """Cog를 봇에 등록한다."""
    await bot.add_cog(SubscriptionCog(bot))
