from __future__ import annotations

import inspect

from bot.models import AptAnnouncement, AptCompetition, WinnerStatistics
from bot.services import formatter
from bot.services.formatter import (
    format_announcement_detail,
    format_announcement_list,
    format_announcement_summary,
    format_competition_rates,
    format_winner_statistics,
)


class TestFormatAnnouncementSummary:
    """format_announcement_summary 테스트."""

    def test_keys(self, sample_announcement: AptAnnouncement) -> None:
        """필요한 키가 모두 포함된다."""
        result = format_announcement_summary(sample_announcement)
        assert "주택명" in result
        assert "지역" in result
        assert "모집공고일" in result
        assert "관리번호" in result

    def test_values(self, sample_announcement: AptAnnouncement) -> None:
        """값이 올바르게 변환된다."""
        result = format_announcement_summary(sample_announcement)
        assert result["주택명"] == "테스트 아파트"
        assert result["지역"] == "서울"

    def test_none_values(self) -> None:
        """None 값은 '-'로 변환된다."""
        ann = AptAnnouncement.model_validate(
            {"HOUSE_MANAGE_NO": "1", "PBLANC_NO": "1", "HOUSE_NM": "테스트"}
        )
        result = format_announcement_summary(ann)
        assert result["지역"] == "-"
        assert result["모집공고일"] == "-"


class TestFormatAnnouncementDetail:
    """format_announcement_detail 테스트."""

    def test_all_keys(self, sample_announcement: AptAnnouncement) -> None:
        """상세 정보에 추가 키가 포함된다."""
        result = format_announcement_detail(sample_announcement)
        assert "시공사" in result
        assert "총공급세대" in result
        assert "접수기간" in result
        assert "주택구분" in result
        assert "홈페이지" in result

    def test_period_both_dates(self, sample_announcement: AptAnnouncement) -> None:
        """접수시작일과 종료일이 모두 있으면 범위로 표시된다."""
        result = format_announcement_detail(sample_announcement)
        assert "~" in result["접수기간"]
        assert "2024-06-10" in result["접수기간"]
        assert "2024-06-14" in result["접수기간"]

    def test_period_start_only(self) -> None:
        """접수시작일만 있으면 시작일 ~ 로 표시된다."""
        ann = AptAnnouncement.model_validate(
            {
                "HOUSE_MANAGE_NO": "1",
                "PBLANC_NO": "1",
                "HOUSE_NM": "테스트",
                "RCEPT_BGNDE": "2024-06-10",
            }
        )
        result = format_announcement_detail(ann)
        assert result["접수기간"] == "2024-06-10 ~"

    def test_period_none(self) -> None:
        """접수일이 모두 None이면 '-'로 표시된다."""
        ann = AptAnnouncement.model_validate(
            {"HOUSE_MANAGE_NO": "1", "PBLANC_NO": "1", "HOUSE_NM": "테스트"}
        )
        result = format_announcement_detail(ann)
        assert result["접수기간"] == "-"


class TestFormatAnnouncementList:
    """format_announcement_list 테스트."""

    def test_length(self, sample_announcement: AptAnnouncement) -> None:
        """입력 수만큼 결과를 반환한다."""
        result = format_announcement_list([sample_announcement, sample_announcement])
        assert len(result) == 2

    def test_empty(self) -> None:
        """빈 입력이면 빈 리스트를 반환한다."""
        assert format_announcement_list([]) == []


class TestFormatCompetitionRates:
    """format_competition_rates 테스트."""

    def test_keys(self, sample_competition: AptCompetition) -> None:
        """필요한 키가 모두 포함된다."""
        result = format_competition_rates([sample_competition])
        assert len(result) == 1
        assert "주택형" in result[0]
        assert "경쟁률" in result[0]

    def test_values(self, sample_competition: AptCompetition) -> None:
        """값이 올바르게 변환된다."""
        result = format_competition_rates([sample_competition])
        assert result[0]["주택형"] == "084.9900A"
        assert result[0]["경쟁률"] == "5.00"

    def test_empty(self) -> None:
        """빈 입력이면 빈 리스트를 반환한다."""
        assert format_competition_rates([]) == []


class TestFormatWinnerStatistics:
    """format_winner_statistics 테스트."""

    def test_keys(self, sample_statistics: WinnerStatistics) -> None:
        """필요한 키가 모두 포함된다."""
        result = format_winner_statistics([sample_statistics])
        assert len(result) == 1
        assert "지역" in result[0]
        assert "30대이하" in result[0]
        assert "60대이상" in result[0]

    def test_values(self, sample_statistics: WinnerStatistics) -> None:
        """값이 올바르게 변환된다."""
        result = format_winner_statistics([sample_statistics])
        assert result[0]["지역"] == "서울"
        assert result[0]["30대이하"] == "150"

    def test_empty(self) -> None:
        """빈 입력이면 빈 리스트를 반환한다."""
        assert format_winner_statistics([]) == []


class TestNoDiscordImport:
    """formatter 모듈에 discord import가 없는지 확인한다."""

    def test_no_discord_import(self) -> None:
        """formatter 소스코드에 discord import가 없다."""
        source = inspect.getsource(formatter)
        assert "import discord" not in source
        assert "from discord" not in source
