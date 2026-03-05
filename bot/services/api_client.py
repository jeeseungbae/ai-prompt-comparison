from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime, timezone
from urllib.parse import quote

import aiohttp
from loguru import logger

from bot.models import (
    APIResponse,
    AptAnnouncement,
    AptCompetition,
    WinnerStatistics,
)


class APIError(Exception):
    """외부 API 호출 실패 시 발생하는 예외."""


class ApplyHomeClient:
    """data.go.kr 청약홈 API 클라이언트.

    aiohttp 세션을 관리하고, 3회 재시도 + exponential backoff을 수행한다.
    """

    TIMEOUT = aiohttp.ClientTimeout(total=10)
    MAX_RETRIES = 3
    BACKOFF_DELAYS = [1, 2, 4]
    MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5MB

    ENDPOINTS = {
        "announcement": "ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail",
        "competition": "ApplyhomeInfoCmpetRtSvc/v1/getAPTLttotPblancCmpet",
        "statistics": "ApplyhomeStatSvc/v1/getAPTPrzwnerAreaStat",
    }

    def __init__(self, api_key: str, base_url: str = "https://api.odcloud.kr/api") -> None:
        """클라이언트를 초기화한다."""
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        """aiohttp 세션을 생성한다."""
        self._session = aiohttp.ClientSession(timeout=self.TIMEOUT)
        logger.info("API 클라이언트 세션 생성 완료")

    async def close(self) -> None:
        """aiohttp 세션을 종료한다."""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("API 클라이언트 세션 종료 완료")

    def _build_url(self, endpoint: str, params: dict[str, str] | None = None) -> str:
        """API URL을 직접 조립한다.

        serviceKey에 +/= 문자가 포함되어 있어 params= 사용 시
        이중 인코딩이 발생하므로 URL을 직접 조립한다.
        """
        url = f"{self._base_url}/{endpoint}?serviceKey={self._api_key}"
        if params:
            for key, value in params.items():
                url += f"&{quote(key, safe='[]:')}={quote(str(value), safe='')}"
        return url

    async def _request(self, endpoint: str, params: dict[str, str] | None = None) -> APIResponse:
        """API를 호출하고 응답을 파싱한다.

        3회까지 재시도하며 exponential backoff을 적용한다.
        """
        if not self._session or self._session.closed:
            raise APIError(
                "API 클라이언트 세션이 초기화되지 않았습니다. start()를 먼저 호출하세요."
            )

        url = self._build_url(endpoint, params)

        for attempt in range(self.MAX_RETRIES):
            try:
                async with self._session.get(url) as response:
                    if response.status != 200:
                        raise APIError(f"API 응답 오류 (HTTP {response.status})")
                    body = await response.content.read(self.MAX_RESPONSE_SIZE + 1)
                    if len(body) > self.MAX_RESPONSE_SIZE:
                        raise APIError("API 응답 크기가 제한을 초과했습니다.")
                    raw = json.loads(body)
                    return APIResponse.model_validate(raw)
            except APIError:
                raise
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                safe_msg = re.sub(r"serviceKey=[^&\s]+", "serviceKey=***", str(e))
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.BACKOFF_DELAYS[attempt]
                    logger.warning(
                        "API 호출 실패 (시도 {}/{}), {}초 후 재시도: {}",
                        attempt + 1,
                        self.MAX_RETRIES,
                        delay,
                        safe_msg,
                    )
                    await asyncio.sleep(delay)

        raise APIError(f"API 호출이 {self.MAX_RETRIES}회 실패했습니다. 잠시 후 다시 시도해 주세요.")

    async def get_recent_announcements(self, count: int = 5) -> list[AptAnnouncement]:
        """최근 분양공고를 조회한다."""
        params = {"page": "1", "perPage": str(count)}
        resp = await self._request(self.ENDPOINTS["announcement"], params)
        return [AptAnnouncement.model_validate(item) for item in resp.data]

    async def search_announcements(self, keyword: str) -> list[AptAnnouncement]:
        """주택명으로 분양공고를 검색한다.

        API가 텍스트 검색을 지원하지 않으므로 100건을 조회 후
        클라이언트사이드에서 HOUSE_NM 부분 일치 필터링한다.
        """
        params = {"page": "1", "perPage": "100"}
        resp = await self._request(self.ENDPOINTS["announcement"], params)
        announcements = [AptAnnouncement.model_validate(item) for item in resp.data]
        keyword_lower = keyword.lower()
        return [a for a in announcements if keyword_lower in a.HOUSE_NM.lower()]

    async def get_announcement_detail(self, house_manage_no: str) -> AptAnnouncement | None:
        """공고번호로 분양공고 상세를 조회한다."""
        params = {
            "page": "1",
            "perPage": "1",
            "cond[HOUSE_MANAGE_NO::EQ]": house_manage_no,
        }
        resp = await self._request(self.ENDPOINTS["announcement"], params)
        if not resp.data:
            return None
        return AptAnnouncement.model_validate(resp.data[0])

    async def get_competition_rates(
        self, house_manage_no: str, pblanc_no: str | None = None
    ) -> list[AptCompetition]:
        """주택형별 경쟁률을 조회한다."""
        params: dict[str, str] = {
            "page": "1",
            "perPage": "100",
            "cond[HOUSE_MANAGE_NO::EQ]": house_manage_no,
        }
        if pblanc_no:
            params["cond[PBLANC_NO::EQ]"] = pblanc_no
        resp = await self._request(self.ENDPOINTS["competition"], params)
        return [AptCompetition.model_validate(item) for item in resp.data]

    async def get_winner_statistics(self, region: str | None = None) -> list[WinnerStatistics]:
        """지역별 당첨자 통계를 조회한다.

        최근 6개월 데이터를 조회하며, region이 지정된 경우
        SUBSCRPT_AREA_CODE_NM 부분 일치 필터링을 수행한다.
        """
        now = datetime.now(tz=timezone.utc)
        month = now.month - 6
        year = now.year
        if month <= 0:
            month += 12
            year -= 1
        stat_de = f"{year}{month:02d}"

        params = {
            "page": "1",
            "perPage": "100",
            "cond[STAT_DE::GTE]": stat_de,
        }
        resp = await self._request(self.ENDPOINTS["statistics"], params)
        stats = [WinnerStatistics.model_validate(item) for item in resp.data]

        if region:
            region_lower = region.lower()
            stats = [
                s
                for s in stats
                if s.SUBSCRPT_AREA_CODE_NM and region_lower in s.SUBSCRPT_AREA_CODE_NM.lower()
            ]
        return stats
