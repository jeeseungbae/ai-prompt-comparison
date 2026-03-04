from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(request: Request) -> dict:
    """봇 상태를 확인하는 헬스체크 엔드포인트."""
    bot = request.app.state.bot
    return {
        "status": "ok",
        "bot_ready": bot.is_ready(),
        "guild_count": len(bot.guilds),
        "latency_ms": round(bot.latency * 1000, 2),
    }
