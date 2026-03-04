"""경쟁률 조회 명령어 Cog."""

from __future__ import annotations

from datetime import datetime, timezone

import discord
from discord.ext import commands
from loguru import logger

from bot.services.api_client import APIError
from bot.services.formatter import format_competition_rates


class CompetitionCog(commands.Cog):
    """경쟁률 조회 명령어 Cog.

    /경쟁률 명령어를 제공한다.
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

    @commands.hybrid_command(name="경쟁률", description="공고번호로 주택형별 경쟁률을 조회합니다")
    async def 경쟁률(self, ctx: commands.Context, id: str) -> None:
        """공고번호(HOUSE_MANAGE_NO)로 주택형별 경쟁률을 조회하여 Embed로 응답한다.

        Args:
            id: 조회할 공고의 주택관리번호(HOUSE_MANAGE_NO).
        """
        await ctx.defer()
        try:
            competitions = await self.bot.api_client.get_competition_rates(id)
            if not competitions:
                embed = discord.Embed(
                    title=f"📊 경쟁률 조회: {id}",
                    description="해당 공고의 경쟁률 정보가 없습니다.",
                    color=0x0066FF,
                    timestamp=datetime.now(tz=timezone.utc),
                )
                embed.set_footer(text="주택청약 봇 | data.go.kr")
                await ctx.send(embed=embed)
                return

            formatted_list = format_competition_rates(competitions)
            embed = discord.Embed(
                title=f"📊 경쟁률 조회: {id}",
                color=0x0066FF,
                timestamp=datetime.now(tz=timezone.utc),
            )
            for item in formatted_list:
                house_type = item.get("주택형", "-")
                value_parts = [f"**{key}**: {val}" for key, val in item.items() if key != "주택형"]
                value = "\n".join(value_parts) if value_parts else "-"
                embed.add_field(name=f"주택형 {house_type}", value=value, inline=True)
            embed.set_footer(text="주택청약 봇 | data.go.kr")
            logger.info("경쟁률 조회 완료 (id={}, {}개 주택형)", id, len(competitions))
            await ctx.send(embed=embed)
        except APIError:
            logger.exception("경쟁률 조회 중 API 오류 발생 (id={})", id)
            await ctx.send(embed=self._error_embed())


async def setup(bot: commands.Bot) -> None:
    """Cog를 봇에 등록한다."""
    await bot.add_cog(CompetitionCog(bot))
