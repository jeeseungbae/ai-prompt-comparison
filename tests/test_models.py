"""Pydantic 모델 단위 테스트."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from bot.models import APIResponse, AptAnnouncement, AptCompetition, WinnerStatistics


def test_api_response_defaults() -> None:
    """빈 APIResponse()는 합리적인 기본값을 가져야 한다."""
    response = APIResponse()
    assert response.currentCount == 0
    assert response.data == []
    assert response.matchCount == 0
    assert response.page == 1
    assert response.perPage == 10
    assert response.totalCount == 0


def test_api_response_from_dict() -> None:
    """전체 필드가 담긴 딕셔너리로 APIResponse를 파싱한다."""
    data = {
        "currentCount": 10,
        "data": [{"key": "value"}],
        "matchCount": 100,
        "page": 2,
        "perPage": 10,
        "totalCount": 100,
    }
    response = APIResponse.model_validate(data)
    assert response.currentCount == 10
    assert response.data == [{"key": "value"}]
    assert response.matchCount == 100
    assert response.page == 2
    assert response.perPage == 10
    assert response.totalCount == 100


def test_apt_announcement_required_fields() -> None:
    """HOUSE_MANAGE_NO, PBLANC_NO, HOUSE_NM은 필수 필드여야 한다."""
    ann = AptAnnouncement.model_validate(
        {
            "HOUSE_MANAGE_NO": "2024000001",
            "PBLANC_NO": "2024000001",
            "HOUSE_NM": "테스트 아파트",
        }
    )
    assert ann.HOUSE_MANAGE_NO == "2024000001"
    assert ann.PBLANC_NO == "2024000001"
    assert ann.HOUSE_NM == "테스트 아파트"


def test_apt_announcement_optional_defaults() -> None:
    """선택적 필드는 기본값으로 None이어야 한다."""
    ann = AptAnnouncement.model_validate(
        {
            "HOUSE_MANAGE_NO": "2024000001",
            "PBLANC_NO": "2024000001",
            "HOUSE_NM": "테스트 아파트",
        }
    )
    assert ann.HSSPLY_ADRES is None
    assert ann.RCRIT_PBLANC_DE is None
    assert ann.PRZWNER_PRESNATN_DE is None
    assert ann.CNSTRCT_ENTRPS_NM is None
    assert ann.SUBSCRPT_AREA_CODE_NM is None
    assert ann.TOT_SUPLY_HSHLDCO is None
    assert ann.RCEPT_BGNDE is None
    assert ann.RCEPT_ENDDE is None
    assert ann.HOUSE_SECD_NM is None
    assert ann.HMPG_ADRES is None


def test_apt_announcement_extra_fields_ignored() -> None:
    """여분 필드가 있어도 ValidationError가 발생하지 않아야 한다 (ConfigDict extra='ignore')."""
    ann = AptAnnouncement.model_validate(
        {
            "HOUSE_MANAGE_NO": "2024000001",
            "PBLANC_NO": "2024000001",
            "HOUSE_NM": "테스트 아파트",
            "UNKNOWN_FIELD": "무시되어야 함",
            "ANOTHER_EXTRA": 999,
        }
    )
    assert ann.HOUSE_NM == "테스트 아파트"
    assert not hasattr(ann, "UNKNOWN_FIELD")


def test_apt_announcement_from_fixture(sample_announcement_dict: dict) -> None:
    """fixture 딕셔너리로 AptAnnouncement를 올바르게 파싱한다."""
    ann = AptAnnouncement.model_validate(sample_announcement_dict)
    assert ann.HOUSE_MANAGE_NO == "2024000001"
    assert ann.HOUSE_NM == "테스트 아파트"
    assert ann.HSSPLY_ADRES == "서울특별시 강남구"
    assert ann.RCRIT_PBLANC_DE == "2024-03-01"
    assert ann.PRZWNER_PRESNATN_DE == "2024-04-01"
    assert ann.CNSTRCT_ENTRPS_NM == "테스트건설"
    assert ann.TOT_SUPLY_HSHLDCO == 500
    assert ann.RCEPT_BGNDE == "2024-03-10"
    assert ann.RCEPT_ENDDE == "2024-03-15"
    assert ann.HOUSE_SECD_NM == "민영주택"
    assert ann.HMPG_ADRES == "https://example.com"


def test_apt_competition_all_optional() -> None:
    """AptCompetition은 최소한의 딕셔너리로도 생성될 수 있다."""
    comp = AptCompetition.model_validate({})
    assert comp.HOUSE_MANAGE_NO is None
    assert comp.PBLANC_NO is None
    assert comp.HOUSE_TY is None
    assert comp.SUPLY_HSHLDCO is None
    assert comp.SUPLY_REQ_CNT is None
    assert comp.SUPLY_CMPET_RATE is None


def test_apt_competition_full(sample_competition_dict: dict) -> None:
    """경쟁률 fixture 딕셔너리로 AptCompetition을 올바르게 파싱한다."""
    comp = AptCompetition.model_validate(sample_competition_dict)
    assert comp.HOUSE_MANAGE_NO == "2024000001"
    assert comp.PBLANC_NO == "2024000001"
    assert comp.HOUSE_TY == "084.9900A"
    assert comp.SUPLY_HSHLDCO == 100
    assert comp.SUPLY_REQ_CNT == 500
    assert comp.SUPLY_CMPET_RATE == "5.0"


def test_winner_statistics_all_optional() -> None:
    """WinnerStatistics는 빈 딕셔너리로도 생성될 수 있다 (모든 필드 optional)."""
    stat = WinnerStatistics()
    assert stat.SUBSCRPT_AREA_CODE_NM is None
    assert stat.AGE_30 is None
    assert stat.AGE_40 is None
    assert stat.AGE_50 is None
    assert stat.AGE_60 is None
    assert stat.STAT_DE is None


def test_winner_statistics_full(sample_statistics_dict: dict) -> None:
    """당첨통계 fixture 딕셔너리로 WinnerStatistics를 올바르게 파싱한다."""
    stat = WinnerStatistics.model_validate(sample_statistics_dict)
    assert stat.SUBSCRPT_AREA_CODE_NM == "서울"
    assert stat.AGE_30 == 100
    assert stat.AGE_40 == 200
    assert stat.AGE_50 == 150
    assert stat.AGE_60 == 50
    assert stat.STAT_DE == "202403"


def test_apt_announcement_missing_required_raises() -> None:
    """필수 필드 없이 AptAnnouncement.model_validate({})는 ValidationError를 발생시킨다."""
    with pytest.raises(ValidationError):
        AptAnnouncement.model_validate({})
