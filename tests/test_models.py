from __future__ import annotations

import pytest
from pydantic import ValidationError

from bot.models import APIResponse, AptAnnouncement, AptCompetition, WinnerStatistics


class TestAPIResponse:
    """APIResponse 모델 테스트."""

    def test_defaults(self) -> None:
        """기본값으로 생성할 수 있다."""
        resp = APIResponse()
        assert resp.currentCount == 0
        assert resp.data == []
        assert resp.totalCount == 0

    def test_full_parse(self) -> None:
        """전체 필드를 파싱할 수 있다."""
        raw = {
            "currentCount": 5,
            "data": [{"a": 1}],
            "matchCount": 10,
            "page": 2,
            "perPage": 5,
            "totalCount": 10,
        }
        resp = APIResponse.model_validate(raw)
        assert resp.currentCount == 5
        assert len(resp.data) == 1

    def test_extra_fields_ignored(self) -> None:
        """알 수 없는 필드는 무시된다."""
        raw = {"currentCount": 1, "data": [], "unknown_field": "test"}
        resp = APIResponse.model_validate(raw)
        assert resp.currentCount == 1


class TestAptAnnouncement:
    """AptAnnouncement 모델 테스트."""

    def test_required_fields(self, sample_announcement_dict: dict) -> None:
        """필수 필드가 있으면 생성된다."""
        ann = AptAnnouncement.model_validate(sample_announcement_dict)
        assert ann.HOUSE_MANAGE_NO == "2024000123"
        assert ann.HOUSE_NM == "테스트 아파트"

    def test_missing_required_raises(self) -> None:
        """필수 필드가 없으면 ValidationError가 발생한다."""
        with pytest.raises(ValidationError):
            AptAnnouncement.model_validate({"HOUSE_NM": "테스트"})

    def test_optional_defaults(self) -> None:
        """선택 필드는 None이 기본값이다."""
        ann = AptAnnouncement.model_validate(
            {"HOUSE_MANAGE_NO": "1", "PBLANC_NO": "1", "HOUSE_NM": "테스트"}
        )
        assert ann.HSSPLY_ADRES is None
        assert ann.TOT_SUPLY_HSHLDCO is None

    def test_extra_fields_ignored(self, sample_announcement_dict: dict) -> None:
        """알 수 없는 필드는 무시된다."""
        sample_announcement_dict["UNKNOWN"] = "value"
        ann = AptAnnouncement.model_validate(sample_announcement_dict)
        assert ann.HOUSE_NM == "테스트 아파트"


class TestAptCompetition:
    """AptCompetition 모델 테스트."""

    def test_all_optional(self) -> None:
        """모든 필드가 선택이므로 빈 딕셔너리로 생성 가능하다."""
        comp = AptCompetition.model_validate({})
        assert comp.HOUSE_TY is None

    def test_full_parse(self, sample_competition_dict: dict) -> None:
        """전체 필드를 파싱할 수 있다."""
        comp = AptCompetition.model_validate(sample_competition_dict)
        assert comp.HOUSE_TY == "084.9900A"
        assert comp.SUPLY_HSHLDCO == 100


class TestWinnerStatistics:
    """WinnerStatistics 모델 테스트."""

    def test_all_optional(self) -> None:
        """모든 필드가 선택이므로 빈 딕셔너리로 생성 가능하다."""
        stat = WinnerStatistics.model_validate({})
        assert stat.SUBSCRPT_AREA_CODE_NM is None

    def test_full_parse(self, sample_statistics_dict: dict) -> None:
        """전체 필드를 파싱할 수 있다."""
        stat = WinnerStatistics.model_validate(sample_statistics_dict)
        assert stat.SUBSCRPT_AREA_CODE_NM == "서울"
        assert stat.AGE_30 == 150
