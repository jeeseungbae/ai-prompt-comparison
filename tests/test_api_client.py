import re

import pytest
from aioresponses import aioresponses

from bot.services.api_client import ApplyHomeAPI, APIError

URL_ANNOUNCEMENT = re.compile(
    r"^https://api\.odcloud\.kr/api/ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail"
)
URL_COMPETITION = re.compile(
    r"^https://api\.odcloud\.kr/api/ApplyhomeInfoCmpetRtSvc/v1/getAPTLttotPblancCmpet"
)
URL_STATISTICS = re.compile(
    r"^https://api\.odcloud\.kr/api/ApplyhomeStatSvc/v1/getAPTPrzwnerAreaStat"
)


class TestApplyHomeAPI:
    @pytest.mark.asyncio
    async def test_get_announcements_success(self):
        """최신 공고 조회 성공"""
        mock_response = {
            "currentCount": 1,
            "data": [{"PBLANC_NO": "2024000001", "HOUSE_NM": "테스트 아파트"}],
            "totalCount": 1,
            "page": 1,
            "perPage": 10,
        }
        with aioresponses() as m:
            m.get(URL_ANNOUNCEMENT, payload=mock_response)
            client = ApplyHomeAPI()
            await client.start()
            try:
                result = await client.get_announcements()
                assert result["data"][0]["HOUSE_NM"] == "테스트 아파트"
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_get_announcements_retry_then_success(self):
        """API 실패 후 재시도 성공"""
        with aioresponses() as m:
            m.get(URL_ANNOUNCEMENT, status=500)
            m.get(URL_ANNOUNCEMENT, status=500)
            m.get(URL_ANNOUNCEMENT, payload={"data": [], "totalCount": 0})
            client = ApplyHomeAPI()
            await client.start()
            try:
                result = await client.get_announcements()
                assert result["data"] == []
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_get_announcements_all_retries_fail(self):
        """모든 재시도 실패 시 APIError 발생"""
        with aioresponses() as m:
            m.get(URL_ANNOUNCEMENT, status=500)
            m.get(URL_ANNOUNCEMENT, status=500)
            m.get(URL_ANNOUNCEMENT, status=500)
            client = ApplyHomeAPI()
            await client.start()
            try:
                with pytest.raises(APIError):
                    await client.get_announcements()
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_search_announcements(self):
        """키워드 검색"""
        mock_response = {
            "data": [{"PBLANC_NO": "2024000001", "HOUSE_NM": "강남 아파트"}],
            "totalCount": 1,
        }
        with aioresponses() as m:
            m.get(URL_ANNOUNCEMENT, payload=mock_response)
            client = ApplyHomeAPI()
            await client.start()
            try:
                result = await client.search_announcements("강남")
                assert len(result["data"]) == 1
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_get_competition_rate(self):
        """경쟁률 조회"""
        mock_response = {
            "data": [{"PBLANC_NO": "2024000001", "CMPET_RATE": "5.2"}],
        }
        with aioresponses() as m:
            m.get(URL_COMPETITION, payload=mock_response)
            client = ApplyHomeAPI()
            await client.start()
            try:
                result = await client.get_competition_rate("2024000001")
                assert result["data"][0]["CMPET_RATE"] == "5.2"
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_get_winner_statistics(self):
        """당첨통계 조회"""
        mock_response = {
            "data": [{"PBLANC_NO": "2024000001", "SUBSCRPT_AREA_CODE_NM": "서울"}],
        }
        with aioresponses() as m:
            m.get(URL_STATISTICS, payload=mock_response)
            client = ApplyHomeAPI()
            await client.start()
            try:
                result = await client.get_winner_statistics("2024000001")
                assert result["data"][0]["SUBSCRPT_AREA_CODE_NM"] == "서울"
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_request_without_start_raises(self):
        """start() 없이 요청 시 APIError 발생"""
        client = ApplyHomeAPI()
        with pytest.raises(APIError, match="초기화"):
            await client.get_announcements()
