"""data.go.kr 청약홈 API 클라이언트 모듈."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

import aiohttp
from loguru import logger

from bot.models import APIResponse, AptAnnouncement, AptCompetition, WinnerStatistics


class APIError(Exception):
    """API 호출 실패 예외."""


class ApplyHomeClient:
    """data.go.kr 청약홈 API 클라이언트.

    aiohttp 세션을 관리하며 분양공고, 경쟁률, 당첨통계 API를 호출한다.
    사용 전 반드시 start()를 호출하고, 종료 시 close()를 호출해야 한다.
    """

    TIMEOUT = aiohttp.ClientTimeout(total=10)
    MAX_RETRIES = 3
    BACKOFF_DELAYS = [1, 2, 4]

    def __init__(self, api_key: str, base_url: str) -> None:
        """클라이언트를 초기화한다.

        Args:
            api_key: data.go.kr API 인증키 (URL-encoded 형태 그대로 보존)
            base_url: API 베이스 URL
        """
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        """aiohttp 세션을 생성한다. 봇 시작 시 호출한다."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.TIMEOUT)
            logger.info("ApplyHomeClient 세션 시작")

    async def close(self) -> None:
        """aiohttp 세션을 종료한다. 봇 종료 시 호출한다."""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("ApplyHomeClient 세션 종료")

    async def _request(
        self,
        endpoint: str,
        params: dict[str, str] | None = None,
    ) -> APIResponse:
        """API 요청을 수행한다. 최대 3회 재시도(지수 백오프)한다.

        serviceKey는 URL에 직접 삽입하여 이중 인코딩을 방지한다.
        cond[] 파라미터의 대괄호와 콜론은 보존된다.

        Args:
            endpoint: 베이스 URL 이후의 엔드포인트 경로
            params: 추가 쿼리 파라미터 (serviceKey 제외)

        Returns:
            파싱된 APIResponse 모델

        Raises:
            APIError: 모든 재시도 실패 시
        """
        if self._session is None or self._session.closed:
            raise APIError("세션이 시작되지 않았습니다. start()를 먼저 호출하세요.")

        # serviceKey를 raw로 삽입하고 나머지 파라미터를 추가한다.
        # params= kwarg로 전달하면 aiohttp가 serviceKey를 재인코딩하므로 URL 직접 구성.
        query_parts = [f"serviceKey={self._api_key}"]
        for k, v in (params or {}).items():
            query_parts.append(f"{k}={v}")
        url = f"{self._base_url}/{endpoint}?{'&'.join(query_parts)}"

        last_error: Exception | None = None
        for attempt, delay in enumerate(self.BACKOFF_DELAYS, start=1):
            try:
                logger.debug(
                    "API 요청 시도 {}/{} — endpoint={}",
                    attempt,
                    self.MAX_RETRIES,
                    endpoint,
                )
                async with self._session.get(url) as resp:
                    if resp.status != 200:
                        raise APIError(f"HTTP {resp.status} 응답 — endpoint={endpoint}")
                    raw = await resp.json(content_type=None)
                    return APIResponse.model_validate(raw)
            except APIError:
                raise
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                last_error = exc
                logger.warning(
                    "API 요청 실패 ({}회차): {} — {}초 후 재시도",
                    attempt,
                    type(exc).__name__,
                    delay,
                )
                if attempt < self.MAX_RETRIES:
                    await asyncio.sleep(delay)

        raise APIError(f"API 요청 최종 실패 (3회 재시도) — endpoint={endpoint}: {last_error}")

    async def get_recent_announcements(self, count: int = 5) -> list[AptAnnouncement]:
        """최근 APT 분양공고를 조회한다.

        Args:
            count: 가져올 공고 수 (기본 5건)

        Returns:
            AptAnnouncement 목록 (최신순)
        """
        params = {
            "page": "1",
            "perPage": str(count),
        }
        response = await self._request(
            "ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail",
            params,
        )
        announcements: list[AptAnnouncement] = []
        for item in response.data:
            try:
                announcements.append(AptAnnouncement.model_validate(item))
            except Exception as exc:
                logger.warning("분양공고 모델 변환 실패: {}", exc)
        return announcements

    async def search_announcements(self, keyword: str) -> list[AptAnnouncement]:
        """주택명 키워드로 분양공고를 검색한다.

        API가 텍스트 검색을 지원하지 않으므로 더 많은 건수를 가져와 클라이언트에서 필터링한다.

        Args:
            keyword: 검색 키워드 (주택명에 포함 여부로 필터링)

        Returns:
            키워드가 포함된 AptAnnouncement 목록
        """
        params = {
            "page": "1",
            "perPage": "100",
        }
        response = await self._request(
            "ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail",
            params,
        )
        results: list[AptAnnouncement] = []
        for item in response.data:
            try:
                ann = AptAnnouncement.model_validate(item)
                if keyword.lower() in ann.HOUSE_NM.lower():
                    results.append(ann)
            except Exception as exc:
                logger.warning("분양공고 모델 변환 실패: {}", exc)
        return results

    async def get_announcement_detail(self, house_manage_no: str) -> AptAnnouncement | None:
        """주택관리번호로 분양공고 상세 정보를 조회한다.

        Args:
            house_manage_no: 주택관리번호 (HOUSE_MANAGE_NO)

        Returns:
            AptAnnouncement 또는 없으면 None
        """
        params = {
            "page": "1",
            "perPage": "1",
            "cond[HOUSE_MANAGE_NO::EQ]": house_manage_no,
        }
        response = await self._request(
            "ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail",
            params,
        )
        if not response.data:
            return None
        try:
            return AptAnnouncement.model_validate(response.data[0])
        except Exception as exc:
            logger.warning("분양공고 상세 모델 변환 실패: {}", exc)
            return None

    async def get_competition_rates(self, house_manage_no: str) -> list[AptCompetition]:
        """주택관리번호로 주택형별 경쟁률을 조회한다.

        Args:
            house_manage_no: 주택관리번호 (HOUSE_MANAGE_NO)

        Returns:
            AptCompetition 목록
        """
        params = {
            "page": "1",
            "perPage": "100",
            "cond[HOUSE_MANAGE_NO::EQ]": house_manage_no,
        }
        response = await self._request(
            "ApplyhomeInfoCmpetRtSvc/v1/getAPTLttotPblancCmpet",
            params,
        )
        competitions: list[AptCompetition] = []
        for item in response.data:
            try:
                competitions.append(AptCompetition.model_validate(item))
            except Exception as exc:
                logger.warning("경쟁률 모델 변환 실패: {}", exc)
        return competitions

    async def get_winner_statistics(self, region: str | None = None) -> list[WinnerStatistics]:
        """지역별 당첨자 통계를 조회한다.

        최근 6개월 데이터를 가져오며, region이 지정된 경우 클라이언트에서 필터링한다.

        Args:
            region: 청약지역명 필터 (None이면 전체)

        Returns:
            WinnerStatistics 목록
        """
        now = datetime.now(tz=timezone.utc)
        # 6개월 전 연월 계산
        month_offset = now.month - 6
        year = now.year
        if month_offset <= 0:
            month_offset += 12
            year -= 1
        stat_de = f"{year}{month_offset:02d}"

        params = {
            "page": "1",
            "perPage": "100",
            "cond[STAT_DE::GTE]": stat_de,
        }
        response = await self._request(
            "ApplyhomeStatSvc/v1/getAPTPrzwnerAreaStat",
            params,
        )
        statistics: list[WinnerStatistics] = []
        for item in response.data:
            try:
                stat = WinnerStatistics.model_validate(item)
                if region is None or (
                    stat.SUBSCRPT_AREA_CODE_NM and region in stat.SUBSCRPT_AREA_CODE_NM
                ):
                    statistics.append(stat)
            except Exception as exc:
                logger.warning("당첨통계 모델 변환 실패: {}", exc)
        return statistics
