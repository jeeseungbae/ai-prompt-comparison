from __future__ import annotations

import pytest

from bot.services.api_client import (
    AptAnnouncement,
    AptCompetition,
    WinnerAgeStat,
    WinnerAreaStat,
)


@pytest.fixture
def sample_announcement_data() -> dict:
    """분양정보 API 응답 샘플 데이터."""
    return {
        "HOUSE_MANAGE_NO": "2024000001",
        "PBLANC_NO": "2024000001",
        "HOUSE_NM": "테스트 아파트",
        "HOUSE_SECD_NM": "APT",
        "SUBSCRPT_AREA_CODE_NM": "서울",
        "HSSPLY_ADRES": "서울특별시 강남구 테스트로 123",
        "TOT_SUPLY_HSHLDCO": 500,
        "RCRIT_PBLANC_DE": "20240315",
        "RCEPT_BGNDE": "20240325",
        "RCEPT_ENDDE": "20240327",
        "PRZWNER_PRESNATN_DE": "20240405",
        "CNTRCT_CNCLS_BGNDE": "20240501",
        "CNTRCT_CNCLS_ENDDE": "20240510",
        "HMPG_ADRES": "https://example.com",
    }


@pytest.fixture
def sample_announcement(sample_announcement_data: dict) -> AptAnnouncement:
    return AptAnnouncement.model_validate(sample_announcement_data)


@pytest.fixture
def sample_competition_data() -> dict:
    """경쟁률 API 응답 샘플 데이터."""
    return {
        "HOUSE_MANAGE_NO": "2024000001",
        "PBLANC_NO": "2024000001",
        "HOUSE_NM": "테스트 아파트",
        "MODEL_NO": "01",
        "HOUSE_TY": "084.9900A",
        "SUPLY_HSHLDCO": 100,
        "SUBSCRPT_RANK_CODE": "1순위",
        "RESIDE_SENM": "해당지역",
        "REQ_CNT": 5000,
        "CMPET_RATE": "50.00",
    }


@pytest.fixture
def sample_competition(sample_competition_data: dict) -> AptCompetition:
    return AptCompetition.model_validate(sample_competition_data)


@pytest.fixture
def sample_area_stat_data() -> dict:
    """지역별 당첨자 통계 샘플 데이터."""
    return {
        "STAT_DE": "202401",
        "SUBSCRPT_AREA_CODE_NM": "서울",
        "SPSPLY_HSHLDCO": 200,
        "SPSPLY_REQ_CNT": 3000,
        "SPSPLY_CMPET_RATE": "15.00",
        "SUPLY_HSHLDCO": 300,
        "SUPLY_REQ_CNT": 15000,
        "SUPLY_CMPET_RATE": "50.00",
    }


@pytest.fixture
def sample_area_stat(sample_area_stat_data: dict) -> WinnerAreaStat:
    return WinnerAreaStat.model_validate(sample_area_stat_data)


@pytest.fixture
def sample_age_stat_data() -> dict:
    """연령별 당첨자 통계 샘플 데이터."""
    return {
        "STAT_DE": "202401",
        "AGE_SE": "30대",
        "PRZWNER_CNT": 1500,
        "PRZWNER_RATE": "35.50",
    }


@pytest.fixture
def sample_age_stat(sample_age_stat_data: dict) -> WinnerAgeStat:
    return WinnerAgeStat.model_validate(sample_age_stat_data)


@pytest.fixture
def sample_api_response(sample_announcement_data: dict) -> dict:
    """API 공통 응답 구조."""
    return {
        "page": 1,
        "perPage": 10,
        "totalCount": 1,
        "currentCount": 1,
        "matchCount": 1,
        "data": [sample_announcement_data],
    }
