from __future__ import annotations

from bot.models import AptAnnouncement, AptCompetition, WinnerStatistics


def _v(value: object) -> str:
    """None 값을 '-'로 변환한다."""
    return str(value) if value is not None else "-"


def format_announcement_summary(announcement: AptAnnouncement) -> dict[str, str]:
    """분양공고 요약 정보를 반환한다."""
    return {
        "주택명": announcement.HOUSE_NM,
        "지역": _v(announcement.SUBSCRPT_AREA_CODE_NM),
        "공급위치": _v(announcement.HSSPLY_ADRES),
        "모집공고일": _v(announcement.RCRIT_PBLANC_DE),
        "당첨자발표일": _v(announcement.PRZWNER_PRESNATN_DE),
        "관리번호": announcement.HOUSE_MANAGE_NO,
    }


def format_announcement_detail(announcement: AptAnnouncement) -> dict[str, str]:
    """분양공고 상세 정보를 반환한다."""
    summary = format_announcement_summary(announcement)

    if announcement.RCEPT_BGNDE and announcement.RCEPT_ENDDE:
        period = f"{announcement.RCEPT_BGNDE} ~ {announcement.RCEPT_ENDDE}"
    elif announcement.RCEPT_BGNDE:
        period = f"{announcement.RCEPT_BGNDE} ~"
    else:
        period = "-"

    summary.update(
        {
            "시공사": _v(announcement.CNSTRCT_ENTRPS_NM),
            "총공급세대": _v(announcement.TOT_SUPLY_HSHLDCO),
            "접수기간": period,
            "주택구분": _v(announcement.HOUSE_SECD_NM),
            "홈페이지": _v(announcement.HMPG_ADRES),
        }
    )
    return summary


def format_announcement_list(announcements: list[AptAnnouncement]) -> list[dict[str, str]]:
    """분양공고 목록의 요약 정보를 반환한다."""
    return [format_announcement_summary(a) for a in announcements]


def format_competition_rates(competitions: list[AptCompetition]) -> list[dict[str, str]]:
    """경쟁률 목록을 포맷팅한다."""
    return [
        {
            "주택형": _v(c.HOUSE_TY),
            "공급세대": _v(c.SUPLY_HSHLDCO),
            "신청건수": _v(c.SUPLY_REQ_CNT),
            "경쟁률": _v(c.SUPLY_CMPET_RATE),
        }
        for c in competitions
    ]


def format_winner_statistics(statistics: list[WinnerStatistics]) -> list[dict[str, str]]:
    """당첨통계 목록을 포맷팅한다."""
    return [
        {
            "지역": _v(s.SUBSCRPT_AREA_CODE_NM),
            "30대이하": _v(s.AGE_30),
            "40대": _v(s.AGE_40),
            "50대": _v(s.AGE_50),
            "60대이상": _v(s.AGE_60),
        }
        for s in statistics
    ]
