from __future__ import annotations

import os

import aiosqlite
from loguru import logger


class NotificationDB:
    """알림 중복 방지를 위한 SQLite 데이터베이스."""

    def __init__(self, db_path: str = "data/notifications.db") -> None:
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def init(self) -> None:
        """데이터베이스를 초기화하고 테이블을 생성합니다."""
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS notified_announcements (
                pblanc_no TEXT PRIMARY KEY,
                house_nm TEXT,
                notified_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        await self._db.commit()
        logger.info(f"데이터베이스 초기화 완료: {self._db_path}")

    async def is_notified(self, pblanc_no: str) -> bool:
        """해당 공고가 이미 알림되었는지 확인합니다."""
        if not self._db:
            return False
        cursor = await self._db.execute(
            "SELECT 1 FROM notified_announcements WHERE pblanc_no = ?",
            (pblanc_no,),
        )
        row = await cursor.fetchone()
        return row is not None

    async def mark_notified(self, pblanc_no: str, house_nm: str = "") -> None:
        """공고를 알림 완료로 기록합니다."""
        if not self._db:
            return
        await self._db.execute(
            "INSERT OR IGNORE INTO notified_announcements (pblanc_no, house_nm) VALUES (?, ?)",
            (pblanc_no, house_nm),
        )
        await self._db.commit()

    async def close(self) -> None:
        """데이터베이스 연결을 종료합니다."""
        if self._db:
            await self._db.close()
            self._db = None
            logger.info("데이터베이스 연결 종료")
