"""분양공고, 경쟁률, 당첨통계 데이터를 사람이 읽기 좋은 형태로 변환하는 포매터 모듈.

discord 모듈에 의존하지 않으며 순수 Python 딕셔너리와 문자열만 반환한다.
Embed 생성은 cogs 레이어에서 이 함수들의 반환값을 사용하여 수행한다.
"""

from __future__ import annotations

from bot.models import AptAnnouncement, AptCompetition, WinnerStatistics

_NONE_PLACEHOLDER = "-"


def _v(value: object) -> str:
    """None이면 '-'를 반환하고, 그 외에는 문자열로 변환한다."""
    if value is None:
        return _NONE_PLACEHOLDER
    return str(value)


def format_announcement_summary(announcement: AptAnnouncement) -> dict[str, str]:
    """분양공고 요약 정보를 딕셔너리로 반환한다.

    Args:
        announcement: AptAnnouncement 모델 인스턴스

    Returns:
        주택명, 지역, 모집공고일, 당첨자발표일, 관리번호를 담은 딕셔너리
    """
    return {
        "주택명": _v(announcement.HOUSE_NM),
        "지역": _v(announcement.HSSPLY_ADRES),
        "모집공고일": _v(announcement.RCRIT_PBLANC_DE),
        "당첨자발표일": _v(announcement.PRZWNER_PRESNATN_DE),
        "관리번호": _v(announcement.HOUSE_MANAGE_NO),
    }


def format_announcement_detail(announcement: AptAnnouncement) -> dict[str, str]:
    """분양공고 상세 정보를 딕셔너리로 반환한다.

    요약 정보에 시공사, 총공급세대, 접수기간, 주택구분, 홈페이지 정보를 추가한다.

    Args:
        announcement: AptAnnouncement 모델 인스턴스

    Returns:
        상세 공고 정보를 담은 딕셔너리
    """
    rcept_bgnde = _v(announcement.RCEPT_BGNDE)
    rcept_endde = _v(announcement.RCEPT_ENDDE)
    if rcept_bgnde != _NONE_PLACEHOLDER and rcept_endde != _NONE_PLACEHOLDER:
        rcept_period = f"{rcept_bgnde} ~ {rcept_endde}"
    elif rcept_bgnde != _NONE_PLACEHOLDER:
        rcept_period = f"{rcept_bgnde} ~"
    else:
        rcept_period = _NONE_PLACEHOLDER

    return {
        "주택명": _v(announcement.HOUSE_NM),
        "지역": _v(announcement.HSSPLY_ADRES),
        "모집공고일": _v(announcement.RCRIT_PBLANC_DE),
        "당첨자발표일": _v(announcement.PRZWNER_PRESNATN_DE),
        "관리번호": _v(announcement.HOUSE_MANAGE_NO),
        "시공사": _v(announcement.CNSTRCT_ENTRPS_NM),
        "총공급세대": _v(announcement.TOT_SUPLY_HSHLDCO),
        "접수기간": rcept_period,
        "주택구분": _v(announcement.HOUSE_SECD_NM),
        "홈페이지": _v(announcement.HMPG_ADRES),
    }


def format_announcement_list(
    announcements: list[AptAnnouncement],
) -> list[dict[str, str]]:
    """분양공고 목록을 요약 딕셔너리 목록으로 반환한다.

    Args:
        announcements: AptAnnouncement 모델 목록

    Returns:
        각 공고의 요약 딕셔너리 목록
    """
    return [format_announcement_summary(ann) for ann in announcements]


def format_competition_rates(
    competitions: list[AptCompetition],
) -> list[dict[str, str]]:
    """주택형별 경쟁률 목록을 딕셔너리 목록으로 반환한다.

    Args:
        competitions: AptCompetition 모델 목록

    Returns:
        주택형, 공급세대, 신청건수, 경쟁률을 담은 딕셔너리 목록
    """
    result: list[dict[str, str]] = []
    for comp in competitions:
        result.append(
            {
                "주택형": _v(comp.HOUSE_TY),
                "공급세대": _v(comp.SUPLY_HSHLDCO),
                "신청건수": _v(comp.SUPLY_REQ_CNT),
                "경쟁률": _v(comp.SUPLY_CMPET_RATE),
            }
        )
    return result


def format_winner_statistics(
    statistics: list[WinnerStatistics],
) -> list[dict[str, str]]:
    """지역별 당첨자 통계 목록을 딕셔너리 목록으로 반환한다.

    Args:
        statistics: WinnerStatistics 모델 목록

    Returns:
        지역, 30대이하, 40대, 50대, 60대이상 당첨자 수를 담은 딕셔너리 목록
    """
    result: list[dict[str, str]] = []
    for stat in statistics:
        result.append(
            {
                "지역": _v(stat.SUBSCRPT_AREA_CODE_NM),
                "30대이하": _v(stat.AGE_30),
                "40대": _v(stat.AGE_40),
                "50대": _v(stat.AGE_50),
                "60대이상": _v(stat.AGE_60),
            }
        )
    return result
