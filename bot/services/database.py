from __future__ import annotations

from pathlib import Path

import aiosqlite
from loguru import logger


class Database:
    """알림 채널 및 봇 상태를 관리하는 SQLite 데이터베이스.

    WAL 모드를 사용하며, 단일 커넥션을 재사용한다.
    """

    def __init__(self, db_path: str) -> None:
        """데이터베이스 경로를 설정한다."""
        self._db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    async def init(self) -> None:
        """데이터베이스를 초기화하고 테이블을 생성한다."""
        if self._db_path != ":memory:":
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)

        self._conn = await aiosqlite.connect(self._db_path)
        await self._conn.execute("PRAGMA journal_mode=WAL")

        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS notification_channels (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS bot_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        await self._conn.commit()
        logger.info("데이터베이스 초기화 완료: {}", self._db_path)

    async def close(self) -> None:
        """데이터베이스 커넥션을 닫는다."""
        if self._conn:
            await self._conn.close()
            logger.info("데이터베이스 커넥션 종료")

    async def get_state(self, key: str) -> str | None:
        """봇 상태값을 조회한다."""
        if self._conn is None:
            raise RuntimeError("데이터베이스가 초기화되지 않았습니다. init()을 먼저 호출하세요.")
        async with self._conn.execute(
            "SELECT value FROM bot_state WHERE key = ?", (key,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

    async def set_state(self, key: str, value: str) -> None:
        """봇 상태값을 저장하거나 갱신한다."""
        if self._conn is None:
            raise RuntimeError("데이터베이스가 초기화되지 않았습니다. init()을 먼저 호출하세요.")
        await self._conn.execute(
            "INSERT INTO bot_state (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        await self._conn.commit()

    async def set_notification_channel(self, guild_id: int, channel_id: int) -> None:
        """알림 채널을 등록하거나 갱신한다."""
        if self._conn is None:
            raise RuntimeError("데이터베이스가 초기화되지 않았습니다. init()을 먼저 호출하세요.")
        await self._conn.execute(
            "INSERT INTO notification_channels (guild_id, channel_id) VALUES (?, ?) "
            "ON CONFLICT(guild_id) DO UPDATE SET channel_id = excluded.channel_id",
            (guild_id, channel_id),
        )
        await self._conn.commit()
        logger.info("알림 채널 등록: guild={}, channel={}", guild_id, channel_id)

    async def get_notification_channel(self, guild_id: int) -> int | None:
        """특정 서버의 알림 채널 ID를 조회한다."""
        if self._conn is None:
            raise RuntimeError("데이터베이스가 초기화되지 않았습니다. init()을 먼저 호출하세요.")
        async with self._conn.execute(
            "SELECT channel_id FROM notification_channels WHERE guild_id = ?",
            (guild_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

    async def get_notification_channels(self) -> list[tuple[int, int]]:
        """모든 알림 채널 목록을 반환한다."""
        if self._conn is None:
            raise RuntimeError("데이터베이스가 초기화되지 않았습니다. init()을 먼저 호출하세요.")
        async with self._conn.execute(
            "SELECT guild_id, channel_id FROM notification_channels"
        ) as cursor:
            return await cursor.fetchall()
