"""data.go.kr API 응답을 위한 Pydantic v2 모델 정의."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class APIResponse(BaseModel):
    """data.go.kr API 공통 응답 구조."""

    model_config = ConfigDict(extra="ignore")

    currentCount: int = 0
    """현재 페이지 반환 건수"""

    data: list[dict] = []
    """실제 데이터 목록"""

    matchCount: int = 0
    """조건에 매칭된 총 건수"""

    page: int = 1
    """현재 페이지 번호"""

    perPage: int = 10
    """페이지당 최대 건수"""

    totalCount: int = 0
    """전체 데이터 건수"""


class AptAnnouncement(BaseModel):
    """APT 분양공고 상세 (서비스 ID: 15098547)."""

    model_config = ConfigDict(extra="ignore")

    HOUSE_MANAGE_NO: str
    """주택관리번호 (고유 식별자)"""

    PBLANC_NO: str
    """공고번호"""

    HOUSE_NM: str
    """주택명"""

    HSSPLY_ADRES: str | None = None
    """공급위치 (주소)"""

    RCRIT_PBLANC_DE: str | None = None
    """모집공고일 (YYYY-MM-DD)"""

    PRZWNER_PRESNATN_DE: str | None = None
    """당첨자 발표일 (YYYY-MM-DD)"""

    CNSTRCT_ENTRPS_NM: str | None = None
    """시공사명"""

    SUBSCRPT_AREA_CODE_NM: str | None = None
    """청약지역명"""

    TOT_SUPLY_HSHLDCO: int | None = None
    """총 공급세대수"""

    RCEPT_BGNDE: str | None = None
    """청약접수 시작일 (YYYY-MM-DD)"""

    RCEPT_ENDDE: str | None = None
    """청약접수 종료일 (YYYY-MM-DD)"""

    HOUSE_SECD_NM: str | None = None
    """주택구분명 (예: 민영주택)"""

    HMPG_ADRES: str | None = None
    """분양정보 홈페이지 주소"""


class AptCompetition(BaseModel):
    """APT 청약 경쟁률 (서비스 ID: 15098905)."""

    model_config = ConfigDict(extra="ignore")

    HOUSE_MANAGE_NO: str | None = None
    """주택관리번호"""

    PBLANC_NO: str | None = None
    """공고번호"""

    HOUSE_TY: str | None = None
    """주택형 (예: 84A)"""

    SUPLY_HSHLDCO: int | None = None
    """공급세대수"""

    SUPLY_REQ_CNT: int | None = None
    """청약 신청건수"""

    SUPLY_CMPET_RATE: str | None = None
    """경쟁률 (예: 10.5)"""


class WinnerStatistics(BaseModel):
    """지역별 당첨자 통계 (서비스 ID: 15110812)."""

    model_config = ConfigDict(extra="ignore")

    SUBSCRPT_AREA_CODE_NM: str | None = None
    """청약지역명"""

    AGE_30: int | None = None
    """30대 이하 당첨자 수"""

    AGE_40: int | None = None
    """40대 당첨자 수"""

    AGE_50: int | None = None
    """50대 당첨자 수"""

    AGE_60: int | None = None
    """60대 이상 당첨자 수"""

    STAT_DE: str | None = None
    """통계 기준월 (YYYYMM)"""
