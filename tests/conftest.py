from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio

from bot.models import AptAnnouncement, AptCompetition, WinnerStatistics
from bot.services.database import Database


@pytest.fixture
def sample_announcement_dict() -> dict:
    """분양공고 API 응답 샘플 딕셔너리."""
    return {
        "HOUSE_MANAGE_NO": "2024000123",
        "PBLANC_NO": "2024000123",
        "HOUSE_NM": "테스트 아파트",
        "HSSPLY_ADRES": "서울특별시 강남구",
        "RCRIT_PBLANC_DE": "2024-06-01",
        "PRZWNER_PRESNATN_DE": "2024-07-01",
        "CNSTRCT_ENTRPS_NM": "테스트건설",
        "SUBSCRPT_AREA_CODE_NM": "서울",
        "TOT_SUPLY_HSHLDCO": 500,
        "RCEPT_BGNDE": "2024-06-10",
        "RCEPT_ENDDE": "2024-06-14",
        "HOUSE_SECD_NM": "APT",
        "HMPG_ADRES": "https://example.com",
    }


@pytest.fixture
def sample_announcement(sample_announcement_dict: dict) -> AptAnnouncement:
    """분양공고 Pydantic 모델 샘플."""
    return AptAnnouncement.model_validate(sample_announcement_dict)


@pytest.fixture
def sample_competition_dict() -> dict:
    """경쟁률 API 응답 샘플 딕셔너리."""
    return {
        "HOUSE_MANAGE_NO": "2024000123",
        "PBLANC_NO": "2024000123",
        "HOUSE_TY": "084.9900A",
        "SUPLY_HSHLDCO": 100,
        "SUPLY_REQ_CNT": 500,
        "SUPLY_CMPET_RATE": "5.00",
    }


@pytest.fixture
def sample_competition(sample_competition_dict: dict) -> AptCompetition:
    """경쟁률 Pydantic 모델 샘플."""
    return AptCompetition.model_validate(sample_competition_dict)


@pytest.fixture
def sample_statistics_dict() -> dict:
    """당첨통계 API 응답 샘플 딕셔너리."""
    return {
        "SUBSCRPT_AREA_CODE_NM": "서울",
        "AGE_30": 150,
        "AGE_40": 200,
        "AGE_50": 100,
        "AGE_60": 50,
        "STAT_DE": "202406",
    }


@pytest.fixture
def sample_statistics(sample_statistics_dict: dict) -> WinnerStatistics:
    """당첨통계 Pydantic 모델 샘플."""
    return WinnerStatistics.model_validate(sample_statistics_dict)


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[Database, None]:
    """인메모리 SQLite 데이터베이스 fixture."""
    database = Database(":memory:")
    await database.init()
    yield database
    await database.close()
