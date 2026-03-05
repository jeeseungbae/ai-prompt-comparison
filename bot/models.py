from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class APIResponse(BaseModel):
    """data.go.kr API 공통 응답 모델."""

    model_config = ConfigDict(extra="ignore")

    currentCount: int = 0
    data: list[dict] = []
    matchCount: int = 0
    page: int = 1
    perPage: int = 10
    totalCount: int = 0


class AptAnnouncement(BaseModel):
    """APT 분양공고 상세 모델."""

    model_config = ConfigDict(extra="ignore")

    HOUSE_MANAGE_NO: str
    PBLANC_NO: str
    HOUSE_NM: str
    HSSPLY_ADRES: str | None = None
    RCRIT_PBLANC_DE: str | None = None
    PRZWNER_PRESNATN_DE: str | None = None
    CNSTRCT_ENTRPS_NM: str | None = None
    SUBSCRPT_AREA_CODE_NM: str | None = None
    TOT_SUPLY_HSHLDCO: int | None = None
    RCEPT_BGNDE: str | None = None
    RCEPT_ENDDE: str | None = None
    HOUSE_SECD_NM: str | None = None
    HMPG_ADRES: str | None = None


class AptCompetition(BaseModel):
    """APT 경쟁률 모델."""

    model_config = ConfigDict(extra="ignore")

    HOUSE_MANAGE_NO: str | None = None
    PBLANC_NO: str | None = None
    HOUSE_TY: str | None = None
    SUPLY_HSHLDCO: int | None = None
    SUPLY_REQ_CNT: int | None = None
    SUPLY_CMPET_RATE: str | None = None


class WinnerStatistics(BaseModel):
    """APT 당첨자 지역별 통계 모델."""

    model_config = ConfigDict(extra="ignore")

    SUBSCRPT_AREA_CODE_NM: str | None = None
    AGE_30: int | None = None
    AGE_40: int | None = None
    AGE_50: int | None = None
    AGE_60: int | None = None
    STAT_DE: str | None = None
