"""봇 상태 및 알림 채널 관리를 위한 SQLite 데이터베이스 모듈."""

from __future__ import annotations

import os

import aiosqlite
from loguru import logger


class Database:
    """봇 상태 및 알림 채널 관리 SQLite 데이터베이스.

    WAL 모드로 단일 커넥션을 재사용한다.
    사용 전 반드시 init()을 호출하고, 종료 시 close()를 호출해야 한다.
    """

    def __init__(self, db_path: str) -> None:
        """데이터베이스를 초기화한다.

        Args:
            db_path: SQLite 파일 경로. ':memory:' 지정 시 인메모리 DB 사용.
        """
        self._db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    async def init(self) -> None:
        """데이터베이스를 초기화하고 테이블을 생성한다.

        ':memory:' 경로가 아닌 경우 부모 디렉터리를 생성한다.
        WAL 모드를 활성화하여 동시 읽기 성능을 개선한다.
        """
        if self._db_path != ":memory:":
            parent_dir = os.path.dirname(self._db_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
                logger.debug("데이터베이스 디렉터리 생성/확인: {}", parent_dir)

        self._conn = await aiosqlite.connect(self._db_path)
        self._conn.row_factory = aiosqlite.Row

        # WAL 모드 활성화
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.commit()

        # 테이블 생성
        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_channels (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bot_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        await self._conn.commit()
        logger.info("데이터베이스 초기화 완료: {}", self._db_path)

    async def close(self) -> None:
        """데이터베이스 커넥션을 종료한다."""
        if self._conn is not None:
            await self._conn.close()
            self._conn = None
            logger.info("데이터베이스 커넥션 종료")

    async def get_state(self, key: str) -> str | None:
        """bot_state 테이블에서 값을 조회한다.

        Args:
            key: 상태 키

        Returns:
            저장된 값 또는 없으면 None
        """
        if self._conn is None:
            logger.error("데이터베이스가 초기화되지 않았습니다.")
            return None
        async with self._conn.execute(
            "SELECT value FROM bot_state WHERE key = ?", (key,)
        ) as cursor:
            row = await cursor.fetchone()
            return row["value"] if row else None

    async def set_state(self, key: str, value: str) -> None:
        """bot_state 테이블에 값을 저장한다. 이미 존재하면 덮어쓴다.

        Args:
            key: 상태 키
            value: 저장할 값
        """
        if self._conn is None:
            logger.error("데이터베이스가 초기화되지 않았습니다.")
            return
        await self._conn.execute(
            "INSERT OR REPLACE INTO bot_state (key, value) VALUES (?, ?)",
            (key, value),
        )
        await self._conn.commit()

    async def set_notification_channel(self, guild_id: int, channel_id: int) -> None:
        """길드의 알림 채널을 설정한다. 이미 존재하면 덮어쓴다.

        Args:
            guild_id: 디스코드 길드(서버) ID
            channel_id: 알림을 전송할 채널 ID
        """
        if self._conn is None:
            logger.error("데이터베이스가 초기화되지 않았습니다.")
            return
        await self._conn.execute(
            "INSERT OR REPLACE INTO notification_channels (guild_id, channel_id) VALUES (?, ?)",
            (guild_id, channel_id),
        )
        await self._conn.commit()
        logger.info("알림 채널 설정 — guild_id={}, channel_id={}", guild_id, channel_id)

    async def get_notification_channel(self, guild_id: int) -> int | None:
        """특정 길드의 알림 채널 ID를 조회한다.

        Args:
            guild_id: 디스코드 길드(서버) ID

        Returns:
            채널 ID 또는 설정되지 않은 경우 None
        """
        if self._conn is None:
            logger.error("데이터베이스가 초기화되지 않았습니다.")
            return None
        async with self._conn.execute(
            "SELECT channel_id FROM notification_channels WHERE guild_id = ?",
            (guild_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return int(row["channel_id"]) if row else None

    async def get_notification_channels(self) -> list[tuple[int, int]]:
        """알림이 설정된 모든 길드의 (guild_id, channel_id) 목록을 반환한다.

        Returns:
            (guild_id, channel_id) 튜플 목록
        """
        if self._conn is None:
            logger.error("데이터베이스가 초기화되지 않았습니다.")
            return []
        async with self._conn.execute(
            "SELECT guild_id, channel_id FROM notification_channels"
        ) as cursor:
            rows = await cursor.fetchall()
            return [(int(row["guild_id"]), int(row["channel_id"])) for row in rows]
