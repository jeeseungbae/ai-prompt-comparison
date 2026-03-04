from __future__ import annotations

import discord

from bot.services.api_client import (
    AptAnnouncement,
    AptCompetition,
    WinnerAgeStat,
    WinnerAreaStat,
)
from bot.services.formatter import (
    format_announcement_embed,
    format_announcement_list_embed,
    format_competition_embed,
    format_winner_stats_embed,
)


def test_format_announcement_embed(sample_announcement: AptAnnouncement) -> None:
    """단일 분양공고 Embed 생성 테스트."""
    embed = format_announcement_embed(sample_announcement)
    assert isinstance(embed, discord.Embed)
    assert "테스트 아파트" in embed.title
    assert embed.color == discord.Color.blue()
    assert len(embed.fields) >= 6


def test_format_announcement_embed_with_url(sample_announcement: AptAnnouncement) -> None:
    """홈페이지 URL이 있는 경우 Embed URL 설정 테스트."""
    embed = format_announcement_embed(sample_announcement)
    assert embed.url == "https://example.com"


def test_format_announcement_list_embed_with_data(
    sample_announcement: AptAnnouncement,
) -> None:
    """분양정보 목록 Embed 테스트."""
    embed = format_announcement_list_embed([sample_announcement])
    assert isinstance(embed, discord.Embed)
    assert "분양정보" in embed.title
    assert len(embed.fields) == 1


def test_format_announcement_list_embed_empty() -> None:
    """빈 분양정보 목록 Embed 테스트."""
    embed = format_announcement_list_embed([])
    assert "없습니다" in embed.description


def test_format_announcement_list_embed_with_region(
    sample_announcement: AptAnnouncement,
) -> None:
    """지역 필터가 적용된 목록 Embed 테스트."""
    embed = format_announcement_list_embed([sample_announcement], region="서울")
    assert "서울" in embed.title


def test_format_competition_embed(sample_competition: AptCompetition) -> None:
    """경쟁률 Embed 생성 테스트."""
    embed = format_competition_embed("테스트 아파트", [sample_competition])
    assert isinstance(embed, discord.Embed)
    assert "테스트 아파트" in embed.title
    assert embed.color == discord.Color.orange()
    assert len(embed.fields) >= 1


def test_format_competition_embed_empty() -> None:
    """빈 경쟁률 Embed 테스트."""
    embed = format_competition_embed("없는단지", [])
    assert "없습니다" in embed.description


def test_format_winner_stats_embed(
    sample_area_stat: WinnerAreaStat, sample_age_stat: WinnerAgeStat
) -> None:
    """당첨자 통계 Embed 생성 테스트."""
    embed = format_winner_stats_embed([sample_area_stat], [sample_age_stat])
    assert isinstance(embed, discord.Embed)
    assert embed.color == discord.Color.green()
    assert len(embed.fields) == 2  # 지역별 + 연령별


def test_format_winner_stats_embed_empty() -> None:
    """빈 통계 Embed 테스트."""
    embed = format_winner_stats_embed([], [])
    assert "없습니다" in embed.description
