"""API 클라이언트 단위 테스트."""

from __future__ import annotations

from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from aiohttp import ClientError

from bot.models import APIResponse, AptAnnouncement, AptCompetition, WinnerStatistics
from bot.services.api_client import APIError, ApplyHomeClient


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[ApplyHomeClient, None]:
    """테스트용 ApplyHomeClient 인스턴스. start/close 자동 처리."""
    c = ApplyHomeClient("test_api_key", "https://api.example.com")
    await c.start()
    yield c
    await c.close()


@pytest.mark.asyncio
async def test_start_creates_session() -> None:
    """start() 호출 후 세션이 None이 아니어야 한다."""
    c = ApplyHomeClient("test_key", "https://api.example.com")
    assert c._session is None
    await c.start()
    assert c._session is not None
    await c.close()


@pytest.mark.asyncio
async def test_close_session() -> None:
    """close() 호출 후 세션이 closed 상태여야 한다."""
    c = ApplyHomeClient("test_key", "https://api.example.com")
    await c.start()
    session = c._session
    assert session is not None
    await c.close()
    assert session.closed


@pytest.mark.asyncio
async def test_request_without_start_raises() -> None:
    """start() 없이 _request()를 호출하면 APIError가 발생해야 한다."""
    c = ApplyHomeClient("test_key", "https://api.example.com")
    with pytest.raises(APIError, match="세션이 시작되지 않았습니다"):
        await c._request("some/endpoint")


@pytest.mark.asyncio
async def test_get_recent_announcements(
    client: ApplyHomeClient, sample_announcement_dict: dict
) -> None:
    """_request를 모킹하여 최근 공고 목록이 AptAnnouncement 리스트로 반환되는지 확인한다."""
    mock_response = APIResponse(
        currentCount=1,
        data=[sample_announcement_dict],
        matchCount=1,
        totalCount=1,
    )
    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)):
        result = await client.get_recent_announcements(count=1)

    assert len(result) == 1
    assert isinstance(result[0], AptAnnouncement)
    assert result[0].HOUSE_NM == "테스트 아파트"


@pytest.mark.asyncio
async def test_get_recent_announcements_empty(client: ApplyHomeClient) -> None:
    """빈 데이터 응답 시 빈 리스트를 반환해야 한다."""
    mock_response = APIResponse(currentCount=0, data=[], matchCount=0, totalCount=0)
    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)):
        result = await client.get_recent_announcements()

    assert result == []


@pytest.mark.asyncio
async def test_search_announcements_found(
    client: ApplyHomeClient, sample_announcement_dict: dict
) -> None:
    """키워드가 주택명에 포함된 경우 해당 공고를 반환한다."""
    mock_response = APIResponse(
        currentCount=1,
        data=[sample_announcement_dict],
        matchCount=1,
        totalCount=1,
    )
    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)):
        result = await client.search_announcements("테스트")

    assert len(result) == 1
    assert result[0].HOUSE_NM == "테스트 아파트"


@pytest.mark.asyncio
async def test_search_announcements_not_found(
    client: ApplyHomeClient, sample_announcement_dict: dict
) -> None:
    """키워드가 주택명에 없는 경우 빈 리스트를 반환한다."""
    mock_response = APIResponse(
        currentCount=1,
        data=[sample_announcement_dict],
        matchCount=1,
        totalCount=1,
    )
    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)):
        result = await client.search_announcements("존재하지않는키워드XYZ")

    assert result == []


@pytest.mark.asyncio
async def test_get_announcement_detail_found(
    client: ApplyHomeClient, sample_announcement_dict: dict
) -> None:
    """주택관리번호로 상세 조회 시 AptAnnouncement를 반환한다."""
    mock_response = APIResponse(
        currentCount=1,
        data=[sample_announcement_dict],
        matchCount=1,
        totalCount=1,
    )
    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)):
        result = await client.get_announcement_detail("2024000001")

    assert result is not None
    assert isinstance(result, AptAnnouncement)
    assert result.HOUSE_MANAGE_NO == "2024000001"


@pytest.mark.asyncio
async def test_get_announcement_detail_not_found(client: ApplyHomeClient) -> None:
    """데이터가 없을 때 상세 조회는 None을 반환해야 한다."""
    mock_response = APIResponse(currentCount=0, data=[], matchCount=0, totalCount=0)
    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)):
        result = await client.get_announcement_detail("9999999999")

    assert result is None


@pytest.mark.asyncio
async def test_get_competition_rates(
    client: ApplyHomeClient, sample_competition_dict: dict
) -> None:
    """경쟁률 조회 시 AptCompetition 리스트를 반환한다."""
    mock_response = APIResponse(
        currentCount=1,
        data=[sample_competition_dict],
        matchCount=1,
        totalCount=1,
    )
    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)):
        result = await client.get_competition_rates("2024000001")

    assert len(result) == 1
    assert isinstance(result[0], AptCompetition)
    assert result[0].HOUSE_TY == "084.9900A"


@pytest.mark.asyncio
async def test_get_winner_statistics(client: ApplyHomeClient, sample_statistics_dict: dict) -> None:
    """당첨통계 조회 시 WinnerStatistics 리스트를 반환한다."""
    mock_response = APIResponse(
        currentCount=1,
        data=[sample_statistics_dict],
        matchCount=1,
        totalCount=1,
    )
    with patch.object(client, "_request", new=AsyncMock(return_value=mock_response)):
        result = await client.get_winner_statistics()

    assert len(result) == 1
    assert isinstance(result[0], WinnerStatistics)
    assert result[0].SUBSCRPT_AREA_CODE_NM == "서울"


@pytest.mark.asyncio
async def test_retry_on_client_error(
    client: ApplyHomeClient, sample_announcement_dict: dict
) -> None:
    """ClientError가 두 번 발생하고 세 번째 시도에서 성공하면 총 3회 호출되어야 한다."""
    raw_response_data = {
        "currentCount": 1,
        "data": [sample_announcement_dict],
        "matchCount": 1,
        "page": 1,
        "perPage": 10,
        "totalCount": 1,
    }

    # 성공 응답을 모방하는 context manager 헬퍼
    def make_success_response() -> AsyncMock:
        resp = AsyncMock()
        resp.status = 200
        resp.json = AsyncMock(return_value=raw_response_data)
        cm = AsyncMock()
        cm.__aenter__ = AsyncMock(return_value=resp)
        cm.__aexit__ = AsyncMock(return_value=False)
        return cm

    call_count = 0

    def side_effect(url: str) -> AsyncMock:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ClientError("연결 오류")
        return make_success_response()

    with (
        patch.object(client._session, "get", side_effect=side_effect),
        patch("asyncio.sleep", new=AsyncMock()),
    ):
        result = await client._request("ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail")

    assert call_count == 3
    assert isinstance(result, APIResponse)


@pytest.mark.asyncio
async def test_all_retries_fail_raises_api_error(client: ApplyHomeClient) -> None:
    """모든 재시도가 실패하면 APIError가 발생해야 한다."""
    with (
        patch.object(
            client._session,
            "get",
            side_effect=ClientError("연결 오류"),
        ),
        patch("asyncio.sleep", new=AsyncMock()),
    ):
        with pytest.raises(APIError):
            await client._request("ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail")
