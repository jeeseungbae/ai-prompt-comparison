from __future__ import annotations

import pytest

from bot.services.database import Database


@pytest.mark.asyncio
class TestDatabase:
    """Database 서비스 테스트."""

    async def test_init_creates_tables(self, db: Database) -> None:
        """init()이 테이블을 생성한다."""
        assert db._conn is not None
        async with db._conn.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
            tables = {row[0] for row in await cursor.fetchall()}
        assert "notification_channels" in tables
        assert "bot_state" in tables

    async def test_get_state_nonexistent(self, db: Database) -> None:
        """존재하지 않는 키를 조회하면 None을 반환한다."""
        result = await db.get_state("nonexistent")
        assert result is None

    async def test_set_and_get_state(self, db: Database) -> None:
        """상태값을 저장하고 조회할 수 있다."""
        await db.set_state("test_key", "test_value")
        result = await db.get_state("test_key")
        assert result == "test_value"

    async def test_set_state_overwrite(self, db: Database) -> None:
        """같은 키로 상태값을 갱신할 수 있다."""
        await db.set_state("key", "value1")
        await db.set_state("key", "value2")
        result = await db.get_state("key")
        assert result == "value2"

    async def test_set_and_get_notification_channel(self, db: Database) -> None:
        """알림 채널을 등록하고 조회할 수 있다."""
        await db.set_notification_channel(guild_id=123, channel_id=456)
        result = await db.get_notification_channel(123)
        assert result == 456

    async def test_notification_channel_overwrite(self, db: Database) -> None:
        """같은 서버에 알림 채널을 갱신할 수 있다."""
        await db.set_notification_channel(guild_id=123, channel_id=456)
        await db.set_notification_channel(guild_id=123, channel_id=789)
        result = await db.get_notification_channel(123)
        assert result == 789

    async def test_get_notification_channel_nonexistent(self, db: Database) -> None:
        """등록되지 않은 서버를 조회하면 None을 반환한다."""
        result = await db.get_notification_channel(999)
        assert result is None

    async def test_get_notification_channels_empty(self, db: Database) -> None:
        """등록된 채널이 없으면 빈 리스트를 반환한다."""
        result = await db.get_notification_channels()
        assert result == []

    async def test_get_notification_channels_multiple(self, db: Database) -> None:
        """여러 서버의 알림 채널 목록을 조회할 수 있다."""
        await db.set_notification_channel(guild_id=1, channel_id=100)
        await db.set_notification_channel(guild_id=2, channel_id=200)
        result = await db.get_notification_channels()
        assert len(result) == 2
        guild_ids = {r[0] for r in result}
        assert guild_ids == {1, 2}
