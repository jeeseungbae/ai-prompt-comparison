from pathlib import Path

import aiosqlite
from loguru import logger

from bot.config import DATABASE_PATH


class Database:
    """SQLite 데이터베이스 관리"""

    def __init__(self, db_path: str | None = None):
        self._db_path = db_path or DATABASE_PATH
        self._db: aiosqlite.Connection | None = None

    async def init(self):
        """데이터베이스 초기화 및 테이블 생성"""
        db_dir = Path(self._db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        self._db = await aiosqlite.connect(self._db_path)
        self._db.row_factory = aiosqlite.Row

        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS bot_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_channels (
                channel_id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await self._db.commit()
        logger.info(f"데이터베이스 초기화 완료: {self._db_path}")

    async def close(self):
        if self._db:
            await self._db.close()
            logger.info("데이터베이스 연결 종료")

    async def get_last_checked_id(self) -> str | None:
        """마지막으로 체크한 공고 ID 조회"""
        async with self._db.execute(
            "SELECT value FROM bot_state WHERE key = ?", ("last_checked_id",)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

    async def set_last_checked_id(self, announce_id: str) -> None:
        """마지막으로 체크한 공고 ID 저장"""
        await self._db.execute(
            """
            INSERT INTO bot_state (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            ("last_checked_id", announce_id),
        )
        await self._db.commit()

    async def add_notification_channel(self, channel_id: int, guild_id: int) -> None:
        """알림 채널 등록 (upsert)"""
        await self._db.execute(
            """
            INSERT INTO notification_channels (channel_id, guild_id) VALUES (?, ?)
            ON CONFLICT(channel_id) DO UPDATE SET guild_id = excluded.guild_id
            """,
            (channel_id, guild_id),
        )
        await self._db.commit()
        logger.info(f"알림 채널 등록: {channel_id} (서버: {guild_id})")

    async def remove_notification_channel(self, channel_id: int) -> bool:
        """알림 채널 해제, 성공 여부 반환"""
        cursor = await self._db.execute(
            "DELETE FROM notification_channels WHERE channel_id = ?", (channel_id,)
        )
        await self._db.commit()
        removed = cursor.rowcount > 0
        if removed:
            logger.info(f"알림 채널 해제: {channel_id}")
        return removed

    async def get_notification_channels(self) -> list[dict]:
        """등록된 알림 채널 목록 조회"""
        async with self._db.execute(
            "SELECT channel_id, guild_id FROM notification_channels"
        ) as cursor:
            rows = await cursor.fetchall()
            return [{"channel_id": row[0], "guild_id": row[1]} for row in rows]
