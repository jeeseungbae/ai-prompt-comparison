import pytest

from bot.services.database import Database


@pytest.fixture
async def db(tmp_path):
    db_path = str(tmp_path / "test.db")
    database = Database(db_path=db_path)
    await database.init()
    yield database
    await database.close()


class TestDatabase:
    @pytest.mark.asyncio
    async def test_last_checked_id_default_none(self, db):
        """초기 상태에서 last_checked_id는 None"""
        result = await db.get_last_checked_id()
        assert result is None

    @pytest.mark.asyncio
    async def test_set_and_get_last_checked_id(self, db):
        """last_checked_id 설정 및 조회"""
        await db.set_last_checked_id("2024000001")
        result = await db.get_last_checked_id()
        assert result == "2024000001"

    @pytest.mark.asyncio
    async def test_update_last_checked_id(self, db):
        """last_checked_id 업데이트"""
        await db.set_last_checked_id("2024000001")
        await db.set_last_checked_id("2024000002")
        result = await db.get_last_checked_id()
        assert result == "2024000002"

    @pytest.mark.asyncio
    async def test_add_notification_channel(self, db):
        """알림 채널 등록"""
        await db.add_notification_channel(123456, 789)
        channels = await db.get_notification_channels()
        assert len(channels) == 1
        assert channels[0]["channel_id"] == 123456
        assert channels[0]["guild_id"] == 789

    @pytest.mark.asyncio
    async def test_remove_notification_channel(self, db):
        """알림 채널 해제"""
        await db.add_notification_channel(123456, 789)
        result = await db.remove_notification_channel(123456)
        assert result is True
        channels = await db.get_notification_channels()
        assert len(channels) == 0

    @pytest.mark.asyncio
    async def test_remove_nonexistent_channel(self, db):
        """존재하지 않는 채널 해제"""
        result = await db.remove_notification_channel(999)
        assert result is False

    @pytest.mark.asyncio
    async def test_duplicate_channel_upsert(self, db):
        """중복 채널 등록 시 upsert"""
        await db.add_notification_channel(123456, 789)
        await db.add_notification_channel(123456, 789)
        channels = await db.get_notification_channels()
        assert len(channels) == 1

    @pytest.mark.asyncio
    async def test_multiple_channels(self, db):
        """여러 채널 등록"""
        await db.add_notification_channel(111, 1)
        await db.add_notification_channel(222, 2)
        await db.add_notification_channel(333, 3)
        channels = await db.get_notification_channels()
        assert len(channels) == 3
