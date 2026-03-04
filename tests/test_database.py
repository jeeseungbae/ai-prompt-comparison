"""데이터베이스 CRUD 단위 테스트."""

from __future__ import annotations

import pytest

from bot.services.database import Database


@pytest.mark.asyncio
async def test_init_creates_tables(db: Database) -> None:
    """init() 후 notification_channels와 bot_state 테이블이 존재해야 한다."""
    assert db._conn is not None
    async with db._conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ) as cursor:
        rows = await cursor.fetchall()
        table_names = [row[0] for row in rows]

    assert "notification_channels" in table_names
    assert "bot_state" in table_names


@pytest.mark.asyncio
async def test_get_state_nonexistent(db: Database) -> None:
    """존재하지 않는 키를 조회하면 None을 반환해야 한다."""
    result = await db.get_state("nonexistent_key")
    assert result is None


@pytest.mark.asyncio
async def test_set_and_get_state(db: Database) -> None:
    """set_state 후 get_state로 동일한 값이 반환되어야 한다."""
    await db.set_state("last_check_id", "2024000001")
    result = await db.get_state("last_check_id")
    assert result == "2024000001"


@pytest.mark.asyncio
async def test_set_state_overwrite(db: Database) -> None:
    """동일한 키로 set_state를 두 번 호출하면 최신 값으로 덮어쓰여야 한다."""
    await db.set_state("my_key", "first_value")
    await db.set_state("my_key", "second_value")
    result = await db.get_state("my_key")
    assert result == "second_value"


@pytest.mark.asyncio
async def test_set_notification_channel(db: Database) -> None:
    """set_notification_channel 후 get_notification_channel로 동일한 채널 ID가 반환되어야 한다."""
    await db.set_notification_channel(guild_id=123456, channel_id=789012)
    result = await db.get_notification_channel(guild_id=123456)
    assert result == 789012


@pytest.mark.asyncio
async def test_set_notification_channel_overwrite(db: Database) -> None:
    """동일한 guild_id로 두 번 설정하면 최신 channel_id로 덮어쓰여야 한다 (길드당 단일 채널)."""
    await db.set_notification_channel(guild_id=111, channel_id=100)
    await db.set_notification_channel(guild_id=111, channel_id=200)
    result = await db.get_notification_channel(guild_id=111)
    assert result == 200


@pytest.mark.asyncio
async def test_get_notification_channel_nonexistent(db: Database) -> None:
    """설정되지 않은 guild_id 조회 시 None을 반환해야 한다."""
    result = await db.get_notification_channel(guild_id=999999)
    assert result is None


@pytest.mark.asyncio
async def test_get_notification_channels_empty(db: Database) -> None:
    """채널이 하나도 설정되지 않은 경우 빈 리스트를 반환해야 한다."""
    result = await db.get_notification_channels()
    assert result == []


@pytest.mark.asyncio
async def test_get_notification_channels_multiple(db: Database) -> None:
    """3개의 길드를 설정하고 get_notification_channels로 전체 목록을 가져온다."""
    guilds = [
        (1001, 2001),
        (1002, 2002),
        (1003, 2003),
    ]
    for guild_id, channel_id in guilds:
        await db.set_notification_channel(guild_id=guild_id, channel_id=channel_id)

    result = await db.get_notification_channels()
    assert len(result) == 3

    result_set = set(result)
    for pair in guilds:
        assert pair in result_set
