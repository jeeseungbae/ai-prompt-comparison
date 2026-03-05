from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
import pytest_asyncio

from bot.models import APIResponse
from bot.services.api_client import APIError, ApplyHomeClient


@pytest_asyncio.fixture
async def client() -> ApplyHomeClient:
    """테스트용 API 클라이언트."""
    c = ApplyHomeClient(api_key="test_key", base_url="https://api.test.kr/api")
    await c.start()
    yield c  # type: ignore[misc]
    await c.close()


def _mock_response(data: list[dict], status: int = 200) -> dict:
    """모의 API 응답 딕셔너리."""
    return {
        "currentCount": len(data),
        "data": data,
        "matchCount": len(data),
        "page": 1,
        "perPage": 10,
        "totalCount": len(data),
    }


class TestApplyHomeClient:
    """ApplyHomeClient 테스트."""

    @pytest.mark.asyncio
    async def test_start_creates_session(self) -> None:
        """start()가 세션을 생성한다."""
        client = ApplyHomeClient(api_key="key")
        await client.start()
        assert client._session is not None
        assert not client._session.closed
        await client.close()

    @pytest.mark.asyncio
    async def test_close_closes_session(self) -> None:
        """close()가 세션을 닫는다."""
        client = ApplyHomeClient(api_key="key")
        await client.start()
        await client.close()
        assert client._session is not None
        assert client._session.closed

    @pytest.mark.asyncio
    async def test_request_without_start_raises(self) -> None:
        """start() 없이 요청하면 APIError가 발생한다."""
        client = ApplyHomeClient(api_key="key")
        with pytest.raises(APIError, match="세션이 초기화되지 않았습니다"):
            await client._request("test/endpoint")

    @pytest.mark.asyncio
    async def test_get_recent_announcements(self, client: ApplyHomeClient) -> None:
        """최근 공고를 조회한다."""
        mock_data = [
            {"HOUSE_MANAGE_NO": "1", "PBLANC_NO": "1", "HOUSE_NM": "아파트A"},
            {"HOUSE_MANAGE_NO": "2", "PBLANC_NO": "2", "HOUSE_NM": "아파트B"},
        ]
        with patch.object(
            client,
            "_request",
            new=AsyncMock(return_value=APIResponse.model_validate(_mock_response(mock_data))),
        ):
            result = await client.get_recent_announcements(5)
            assert len(result) == 2
            assert result[0].HOUSE_NM == "아파트A"

    @pytest.mark.asyncio
    async def test_get_recent_announcements_empty(self, client: ApplyHomeClient) -> None:
        """공고가 없으면 빈 리스트를 반환한다."""
        with patch.object(
            client,
            "_request",
            new=AsyncMock(return_value=APIResponse.model_validate(_mock_response([]))),
        ):
            result = await client.get_recent_announcements()
            assert result == []

    @pytest.mark.asyncio
    async def test_search_announcements(self, client: ApplyHomeClient) -> None:
        """키워드로 검색한다."""
        mock_data = [
            {"HOUSE_MANAGE_NO": "1", "PBLANC_NO": "1", "HOUSE_NM": "힐스테이트 강남"},
            {"HOUSE_MANAGE_NO": "2", "PBLANC_NO": "2", "HOUSE_NM": "래미안 서초"},
        ]
        with patch.object(
            client,
            "_request",
            new=AsyncMock(return_value=APIResponse.model_validate(_mock_response(mock_data))),
        ):
            result = await client.search_announcements("힐스테이트")
            assert len(result) == 1
            assert result[0].HOUSE_NM == "힐스테이트 강남"

    @pytest.mark.asyncio
    async def test_search_no_match(self, client: ApplyHomeClient) -> None:
        """검색 결과가 없으면 빈 리스트를 반환한다."""
        mock_data = [
            {"HOUSE_MANAGE_NO": "1", "PBLANC_NO": "1", "HOUSE_NM": "래미안"},
        ]
        with patch.object(
            client,
            "_request",
            new=AsyncMock(return_value=APIResponse.model_validate(_mock_response(mock_data))),
        ):
            result = await client.search_announcements("힐스테이트")
            assert result == []

    @pytest.mark.asyncio
    async def test_get_announcement_detail(self, client: ApplyHomeClient) -> None:
        """상세 조회 성공."""
        mock_data = [
            {"HOUSE_MANAGE_NO": "123", "PBLANC_NO": "123", "HOUSE_NM": "테스트"},
        ]
        with patch.object(
            client,
            "_request",
            new=AsyncMock(return_value=APIResponse.model_validate(_mock_response(mock_data))),
        ):
            result = await client.get_announcement_detail("123")
            assert result is not None
            assert result.HOUSE_MANAGE_NO == "123"

    @pytest.mark.asyncio
    async def test_get_announcement_detail_not_found(self, client: ApplyHomeClient) -> None:
        """상세 조회 시 결과가 없으면 None을 반환한다."""
        with patch.object(
            client,
            "_request",
            new=AsyncMock(return_value=APIResponse.model_validate(_mock_response([]))),
        ):
            result = await client.get_announcement_detail("999")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_competition_rates(self, client: ApplyHomeClient) -> None:
        """경쟁률을 조회한다."""
        mock_data = [
            {"HOUSE_TY": "084A", "SUPLY_HSHLDCO": 10, "SUPLY_REQ_CNT": 50},
        ]
        with patch.object(
            client,
            "_request",
            new=AsyncMock(return_value=APIResponse.model_validate(_mock_response(mock_data))),
        ):
            result = await client.get_competition_rates("123")
            assert len(result) == 1
            assert result[0].HOUSE_TY == "084A"

    @pytest.mark.asyncio
    async def test_get_winner_statistics(self, client: ApplyHomeClient) -> None:
        """당첨통계를 조회한다."""
        mock_data = [
            {"SUBSCRPT_AREA_CODE_NM": "서울", "AGE_30": 100},
            {"SUBSCRPT_AREA_CODE_NM": "경기", "AGE_30": 200},
        ]
        with patch.object(
            client,
            "_request",
            new=AsyncMock(return_value=APIResponse.model_validate(_mock_response(mock_data))),
        ):
            result = await client.get_winner_statistics("서울")
            assert len(result) == 1
            assert result[0].SUBSCRPT_AREA_CODE_NM == "서울"

    @pytest.mark.asyncio
    async def test_retry_on_failure(self) -> None:
        """연결 실패 시 재시도한다."""
        client = ApplyHomeClient(api_key="key")
        await client.start()

        import json as json_mod

        response_bytes = json_mod.dumps(_mock_response([])).encode()
        mock_content = MagicMock()
        mock_content.read = AsyncMock(return_value=response_bytes)
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.content = mock_content

        call_count = 0

        def side_effect(*args, **kwargs):  # type: ignore[no-untyped-def]
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise aiohttp.ClientError("Connection failed")
            cm = MagicMock()
            cm.__aenter__ = AsyncMock(return_value=mock_resp)
            cm.__aexit__ = AsyncMock(return_value=False)
            return cm

        with (
            patch.object(client._session, "get", side_effect=side_effect),
            patch("asyncio.sleep", new=AsyncMock()),
        ):
            result = await client._request("test/endpoint")
            assert call_count == 3
            assert result.currentCount == 0

        await client.close()

    @pytest.mark.asyncio
    async def test_all_retries_fail(self) -> None:
        """모든 재시도가 실패하면 APIError가 발생한다."""
        client = ApplyHomeClient(api_key="key")
        await client.start()

        with (
            patch.object(
                client._session,
                "get",
                side_effect=aiohttp.ClientError("fail"),
            ),
            patch("asyncio.sleep", new=AsyncMock()),
            pytest.raises(APIError, match="3회 실패"),
        ):
            await client._request("test/endpoint")

        await client.close()
