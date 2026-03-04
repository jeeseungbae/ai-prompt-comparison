from __future__ import annotations

import importlib

import pytest


@pytest.mark.parametrize(
    "module_path",
    [
        "bot.cogs.subscription",
        "bot.cogs.competition",
        "bot.cogs.stats",
        "bot.services.notifier",
        "bot.services.api_client",
        "bot.services.formatter",
        "bot.services.database",
        "bot.api.health",
        "bot.config",
    ],
)
def test_module_import(module_path: str) -> None:
    """모든 모듈이 정상적으로 임포트되는지 테스트합니다."""
    module = importlib.import_module(module_path)
    assert module is not None


def test_api_client_models_exist() -> None:
    """Pydantic 모델이 존재하는지 테스트합니다."""
    from bot.services.api_client import (
        AptAnnouncement,
        AptCompetition,
        WinnerAgeStat,
        WinnerAreaStat,
    )

    assert AptAnnouncement is not None
    assert AptCompetition is not None
    assert WinnerAreaStat is not None
    assert WinnerAgeStat is not None


def test_cog_setup_functions_exist() -> None:
    """각 Cog의 setup 함수가 존재하는지 테스트합니다."""
    from bot.cogs import competition, stats, subscription

    assert hasattr(subscription, "setup")
    assert hasattr(competition, "setup")
    assert hasattr(stats, "setup")
    assert callable(subscription.setup)
    assert callable(competition.setup)
    assert callable(stats.setup)
