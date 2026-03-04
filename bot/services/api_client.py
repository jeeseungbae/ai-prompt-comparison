from __future__ import annotations

import aiohttp
from loguru import logger
from pydantic import BaseModel, ConfigDict


class AptAnnouncement(BaseModel):
    """APT 분양정보."""

    model_config = ConfigDict(extra="ignore")

    HOUSE_MANAGE_NO: str
    PBLANC_NO: str
    HOUSE_NM: str
    HOUSE_SECD_NM: str | None = None
    SUBSCRPT_AREA_CODE_NM: str | None = None
    HSSPLY_ADRES: str | None = None
    TOT_SUPLY_HSHLDCO: int | None = None
    RCRIT_PBLANC_DE: str | None = None
    RCEPT_BGNDE: str | None = None
    RCEPT_ENDDE: str | None = None
    PRZWNER_PRESNATN_DE: str | None = None
    CNTRCT_CNCLS_BGNDE: str | None = None
    CNTRCT_CNCLS_ENDDE: str | None = None
    HMPG_ADRES: str | None = None


class AptCompetition(BaseModel):
    """APT 경쟁률."""

    model_config = ConfigDict(extra="ignore")

    HOUSE_MANAGE_NO: str
    PBLANC_NO: str
    HOUSE_NM: str | None = None
    MODEL_NO: str | None = None
    HOUSE_TY: str | None = None
    SUPLY_HSHLDCO: int | None = None
    SUBSCRPT_RANK_CODE: str | None = None
    RESIDE_SENM: str | None = None
    REQ_CNT: int | None = None
    CMPET_RATE: str | None = None


class WinnerAreaStat(BaseModel):
    """지역별 당첨자 통계."""

    model_config = ConfigDict(extra="ignore")

    STAT_DE: str
    SUBSCRPT_AREA_CODE_NM: str | None = None
    SPSPLY_HSHLDCO: int | None = None
    SPSPLY_REQ_CNT: int | None = None
    SPSPLY_CMPET_RATE: str | None = None
    SUPLY_HSHLDCO: int | None = None
    SUPLY_REQ_CNT: int | None = None
    SUPLY_CMPET_RATE: str | None = None


class WinnerAgeStat(BaseModel):
    """연령별 당첨자 통계."""

    model_config = ConfigDict(extra="ignore")

    STAT_DE: str
    AGE_SE: str | None = None
    PRZWNER_CNT: int | None = None
    PRZWNER_RATE: str | None = None


class ApplyHomeClient:
    """data.go.kr 청약홈 API 클라이언트."""

    def __init__(self, api_key: str, base_url: str = "https://api.odcloud.kr/api") -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _request(self, endpoint: str, params: dict | None = None) -> dict:
        """공통 API 요청 메서드."""
        session = await self._get_session()
        base_params = {
            "page": 1,
            "perPage": 50,
            "returnType": "JSON",
            "serviceKey": self._api_key,
        }
        if params:
            base_params.update(params)

        url = f"{self._base_url}{endpoint}"
        try:
            async with session.get(url, params=base_params) as resp:
                if resp.status != 200:
                    logger.error(f"API 요청 실패: {url} status={resp.status}")
                    return {"data": []}
                result = await resp.json()
                return result
        except Exception as e:
            logger.error(f"API 요청 에러: {url} error={e}")
            return {"data": []}

    async def get_apt_announcements(
        self,
        region: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        per_page: int = 50,
    ) -> list[AptAnnouncement]:
        """APT 분양정보 목록을 조회합니다."""
        params: dict = {"perPage": per_page}
        if region:
            params["cond[SUBSCRPT_AREA_CODE_NM::EQ]"] = region
        if start_date:
            params["cond[RCRIT_PBLANC_DE::GTE]"] = start_date
        if end_date:
            params["cond[RCRIT_PBLANC_DE::LTE]"] = end_date

        data = await self._request(
            "/ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail", params
        )
        return [AptAnnouncement.model_validate(item) for item in data.get("data", [])]

    async def get_apt_competition(
        self,
        house_manage_no: str | None = None,
        pblanc_no: str | None = None,
    ) -> list[AptCompetition]:
        """APT 경쟁률을 조회합니다."""
        params: dict = {}
        if house_manage_no:
            params["cond[HOUSE_MANAGE_NO::EQ]"] = house_manage_no
        if pblanc_no:
            params["cond[PBLANC_NO::EQ]"] = pblanc_no

        data = await self._request(
            "/ApplyhomeInfoCmpetRtSvc/v1/getAPTLttotPblancCmpet", params
        )
        return [AptCompetition.model_validate(item) for item in data.get("data", [])]

    async def search_apt_by_name(self, house_name: str) -> list[AptAnnouncement]:
        """단지명으로 분양정보를 검색합니다 (LIKE 조건)."""
        params = {"cond[HOUSE_NM::LIKE]": house_name}
        data = await self._request(
            "/ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail", params
        )
        return [AptAnnouncement.model_validate(item) for item in data.get("data", [])]

    async def get_winner_stats_by_area(
        self, start_month: str, end_month: str
    ) -> list[WinnerAreaStat]:
        """지역별 당첨자 통계를 조회합니다."""
        params = {
            "cond[STAT_DE::GTE]": start_month,
            "cond[STAT_DE::LTE]": end_month,
        }
        data = await self._request(
            "/ApplyhomeStatSvc/v1/getAPTPrzwnerAreaStat", params
        )
        return [WinnerAreaStat.model_validate(item) for item in data.get("data", [])]

    async def get_winner_stats_by_age(
        self, start_month: str, end_month: str
    ) -> list[WinnerAgeStat]:
        """연령별 당첨자 통계를 조회합니다."""
        params = {
            "cond[STAT_DE::GTE]": start_month,
            "cond[STAT_DE::LTE]": end_month,
        }
        data = await self._request(
            "/ApplyhomeStatSvc/v1/getAPTPrzwnerAgeStat", params
        )
        return [WinnerAgeStat.model_validate(item) for item in data.get("data", [])]

    async def close(self) -> None:
        """세션을 종료합니다."""
        if self._session and not self._session.closed:
            await self._session.close()
