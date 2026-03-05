from __future__ import annotations

import time

from fastapi import APIRouter, Request

router = APIRouter()
_start_time = time.monotonic()


@router.get("/health")
async def health_check(request: Request) -> dict:
    """봇 상태를 반환하는 헬스체크 엔드포인트."""
    bot = getattr(request.app.state, "bot", None)
    return {
        "status": "ok",
        "bot_ready": bot.is_ready() if bot else False,
        "uptime_seconds": round(time.monotonic() - _start_time, 2),
        "guild_count": len(bot.guilds) if bot and bot.is_ready() else 0,
    }
