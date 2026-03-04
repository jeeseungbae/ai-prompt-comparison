"""포매터 함수 단위 테스트."""

from __future__ import annotations

import inspect

from bot.models import AptAnnouncement, AptCompetition, WinnerStatistics
from bot.services.formatter import (
    format_announcement_detail,
    format_announcement_list,
    format_announcement_summary,
    format_competition_rates,
    format_winner_statistics,
)


def test_format_announcement_summary(sample_announcement: AptAnnouncement) -> None:
    """공고 요약에 주택명, 지역, 모집공고일, 당첨자발표일, 관리번호 키가 포함되어야 한다."""
    result = format_announcement_summary(sample_announcement)
    assert "주택명" in result
    assert "지역" in result
    assert "모집공고일" in result
    assert "당첨자발표일" in result
    assert "관리번호" in result
    assert result["주택명"] == "테스트 아파트"
    assert result["지역"] == "서울특별시 강남구"
    assert result["모집공고일"] == "2024-03-01"
    assert result["당첨자발표일"] == "2024-04-01"
    assert result["관리번호"] == "2024000001"


def test_format_announcement_summary_none_values() -> None:
    """선택적 필드가 None인 경우 '-'로 표시되어야 한다."""
    ann = AptAnnouncement.model_validate(
        {
            "HOUSE_MANAGE_NO": "2024000001",
            "PBLANC_NO": "2024000001",
            "HOUSE_NM": "최소 아파트",
        }
    )
    result = format_announcement_summary(ann)
    assert result["지역"] == "-"
    assert result["모집공고일"] == "-"
    assert result["당첨자발표일"] == "-"


def test_format_announcement_detail_keys(sample_announcement: AptAnnouncement) -> None:
    """공고 상세에 요약 키 + 시공사, 총공급세대, 접수기간, 주택구분, 홈페이지 키가 있어야 한다."""
    result = format_announcement_detail(sample_announcement)
    required_keys = [
        "주택명",
        "지역",
        "모집공고일",
        "당첨자발표일",
        "관리번호",
        "시공사",
        "총공급세대",
        "접수기간",
        "주택구분",
        "홈페이지",
    ]
    for key in required_keys:
        assert key in result, f"'{key}' 키가 format_announcement_detail 결과에 없습니다."


def test_format_announcement_detail_period(sample_announcement: AptAnnouncement) -> None:
    """접수기간은 'YYYY-MM-DD ~ YYYY-MM-DD' 형식이어야 한다."""
    result = format_announcement_detail(sample_announcement)
    assert result["접수기간"] == "2024-03-10 ~ 2024-03-15"


def test_format_announcement_detail_period_only_start() -> None:
    """접수 종료일이 없으면 '시작일 ~' 형식이어야 한다."""
    ann = AptAnnouncement.model_validate(
        {
            "HOUSE_MANAGE_NO": "2024000001",
            "PBLANC_NO": "2024000001",
            "HOUSE_NM": "테스트",
            "RCEPT_BGNDE": "2024-03-10",
        }
    )
    result = format_announcement_detail(ann)
    assert result["접수기간"] == "2024-03-10 ~"


def test_format_announcement_detail_period_both_none() -> None:
    """접수 시작일과 종료일 모두 None이면 '-'이어야 한다."""
    ann = AptAnnouncement.model_validate(
        {
            "HOUSE_MANAGE_NO": "2024000001",
            "PBLANC_NO": "2024000001",
            "HOUSE_NM": "테스트",
        }
    )
    result = format_announcement_detail(ann)
    assert result["접수기간"] == "-"


def test_format_announcement_list(sample_announcement: AptAnnouncement) -> None:
    """format_announcement_list는 딕셔너리 리스트를 반환하며 길이가 입력과 일치해야 한다."""
    announcements = [sample_announcement, sample_announcement]
    result = format_announcement_list(announcements)
    assert isinstance(result, list)
    assert len(result) == 2
    for item in result:
        assert isinstance(item, dict)
        assert "주택명" in item


def test_format_announcement_list_empty() -> None:
    """빈 리스트 입력 시 빈 리스트를 반환해야 한다."""
    result = format_announcement_list([])
    assert result == []


def test_format_competition_rates(sample_competition: AptCompetition) -> None:
    """경쟁률 포맷에 주택형, 공급세대, 신청건수, 경쟁률 키가 있어야 한다."""
    result = format_competition_rates([sample_competition])
    assert len(result) == 1
    item = result[0]
    assert "주택형" in item
    assert "공급세대" in item
    assert "신청건수" in item
    assert "경쟁률" in item
    assert item["주택형"] == "084.9900A"
    assert item["공급세대"] == "100"
    assert item["신청건수"] == "500"
    assert item["경쟁률"] == "5.0"


def test_format_competition_rates_empty() -> None:
    """빈 리스트 입력 시 빈 리스트를 반환해야 한다."""
    result = format_competition_rates([])
    assert result == []


def test_format_winner_statistics(sample_statistics: WinnerStatistics) -> None:
    """당첨통계 포맷에 지역, 30대이하, 40대, 50대, 60대이상 키가 있어야 한다."""
    result = format_winner_statistics([sample_statistics])
    assert len(result) == 1
    item = result[0]
    assert "지역" in item
    assert "30대이하" in item
    assert "40대" in item
    assert "50대" in item
    assert "60대이상" in item
    assert item["지역"] == "서울"
    assert item["30대이하"] == "100"
    assert item["40대"] == "200"
    assert item["50대"] == "150"
    assert item["60대이상"] == "50"


def test_format_winner_statistics_empty() -> None:
    """빈 리스트 입력 시 빈 리스트를 반환해야 한다."""
    result = format_winner_statistics([])
    assert result == []


def test_no_discord_import() -> None:
    """formatter 모듈은 discord를 임포트해서는 안 된다."""
    import bot.services.formatter as formatter_module

    source = inspect.getsource(formatter_module)
    assert "import discord" not in source
    assert "from discord" not in source
