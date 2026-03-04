import asyncio
from urllib.parse import urlencode

import aiohttp
from yarl import URL
from loguru import logger

from bot.config import BASE_URL, DATA_GO_KR_API_KEY, ENDPOINTS


class APIError(Exception):
    """API 호출 실패 시 발생하는 예외"""
    pass


class ApplyHomeAPI:
    """한국부동산원 청약홈 API 클라이언트"""

    MAX_RETRIES = 3
    BACKOFF_SECONDS = [1, 2, 4]

    def __init__(self):
        self._session: aiohttp.ClientSession | None = None

    async def start(self):
        self._session = aiohttp.ClientSession()
        logger.info("API 클라이언트 세션 생성 완료")

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("API 클라이언트 세션 종료")

    async def _request(self, endpoint: str, params: dict | None = None) -> dict:
        if not self._session:
            raise APIError("API 클라이언트가 초기화되지 않았습니다. start()를 먼저 호출하세요.")

        request_params = {"serviceKey": DATA_GO_KR_API_KEY}
        if params:
            request_params.update(params)
        query_string = urlencode(request_params, safe="[]:")
        full_url = URL(f"{BASE_URL}{endpoint}?{query_string}", encoded=True)

        last_error: Exception | None = None

        for attempt in range(self.MAX_RETRIES):
            try:
                async with self._session.get(full_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        last_error = APIError(
                            f"HTTP {response.status}: {await response.text()}"
                        )
                        logger.warning(
                            f"API 요청 실패 (시도 {attempt + 1}/{self.MAX_RETRIES}): "
                            f"HTTP {response.status}"
                        )
            except aiohttp.ClientError as e:
                last_error = APIError(f"네트워크 오류: {e}")
                logger.warning(
                    f"API 네트워크 오류 (시도 {attempt + 1}/{self.MAX_RETRIES}): {e}"
                )

            if attempt < self.MAX_RETRIES - 1:
                wait = self.BACKOFF_SECONDS[attempt]
                logger.debug(f"{wait}초 후 재시도...")
                await asyncio.sleep(wait)

        logger.error(f"API 호출 최종 실패: {last_error}")
        raise APIError(f"3회 재시도 후에도 실패: {last_error}")

    async def get_announcements(self, page: int = 1, per_page: int = 10) -> dict:
        """최신 분양 공고 목록 조회"""
        return await self._request(
            ENDPOINTS["announcement"],
            params={"page": str(page), "perPage": str(per_page)},
        )

    async def get_announcement_detail(self, announce_id: str) -> dict:
        """공고번호로 분양 공고 상세 조회"""
        return await self._request(
            ENDPOINTS["announcement"],
            params={
                "page": "1",
                "perPage": "1",
                "cond[PBLANC_NO::EQ]": announce_id,
            },
        )

    async def search_announcements(
        self, keyword: str, page: int = 1, per_page: int = 10
    ) -> dict:
        """키워드로 분양 공고 검색"""
        return await self._request(
            ENDPOINTS["announcement"],
            params={
                "page": str(page),
                "perPage": str(per_page),
                "cond[HOUSE_NM::LIKE]": keyword,
            },
        )

    async def get_competition_rate(self, announce_id: str) -> dict:
        """공고번호로 청약 경쟁률 조회"""
        return await self._request(
            ENDPOINTS["competition"],
            params={
                "page": "1",
                "perPage": "100",
                "cond[PBLANC_NO::EQ]": announce_id,
            },
        )

    async def get_winner_statistics(self, announce_id: str) -> dict:
        """공고번호로 당첨자 통계 조회"""
        return await self._request(
            ENDPOINTS["statistics"],
            params={
                "page": "1",
                "perPage": "100",
                "cond[PBLANC_NO::EQ]": announce_id,
            },
        )
