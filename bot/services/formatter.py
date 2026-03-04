import discord

from bot.config import EMBED_COLOR, ERROR_COLOR, SUCCESS_COLOR


def _safe(value, default: str = "-") -> str:
    """None이나 빈 값을 안전하게 문자열로 변환"""
    if value is None or value == "":
        return default
    return str(value)


def format_announcement_list(data: dict) -> discord.Embed:
    """분양 공고 목록 임베드 생성"""
    items = data.get("data", [])
    total = data.get("totalCount", 0)

    if not items:
        embed = discord.Embed(
            title="🏠 분양 공고 목록",
            description="조회 결과가 없습니다.",
            color=EMBED_COLOR,
        )
        return embed

    embed = discord.Embed(
        title="🏠 분양 공고 목록",
        description=f"총 **{total}**건의 공고가 있습니다.",
        color=EMBED_COLOR,
    )

    for item in items[:10]:
        name = _safe(item.get("HOUSE_NM"))
        area = _safe(item.get("SUBSCRPT_AREA_CODE_NM"))
        count = _safe(item.get("SUPPLY_LTTOT_CNT"))
        start = _safe(item.get("RCEPT_BGNDE"))
        end = _safe(item.get("RCEPT_ENDDE"))
        pblanc_no = _safe(item.get("PBLANC_NO"))

        embed.add_field(
            name=f"📌 {name}",
            value=(
                f"📍 지역: {area}\n"
                f"🏗️ 공급세대: {count}세대\n"
                f"📅 접수기간: {start} ~ {end}\n"
                f"🔢 공고번호: `{pblanc_no}`"
            ),
            inline=False,
        )

    page = data.get("page", 1)
    per_page = data.get("perPage", 10)
    embed.set_footer(text=f"페이지 {page} | 페이지당 {per_page}건 | 총 {total}건")

    return embed


def format_announcement_detail(data: dict) -> discord.Embed:
    """분양 공고 상세 임베드 생성"""
    items = data.get("data", [])

    if not items:
        return discord.Embed(
            title="🏠 공고 상세 정보",
            description="조회 결과가 없습니다.",
            color=EMBED_COLOR,
        )

    item = items[0]

    embed = discord.Embed(
        title=f"🏠 {_safe(item.get('HOUSE_NM'))}",
        description="분양 공고 상세 정보",
        color=EMBED_COLOR,
    )

    fields = [
        ("공고번호", _safe(item.get("PBLANC_NO"))),
        ("주택명", _safe(item.get("HOUSE_NM"))),
        ("주택구분", _safe(item.get("HOUSE_SECD_NM"))),
        ("공급위치", _safe(item.get("HSSPLY_ADRES"))),
        ("공급세대수", f"{_safe(item.get('SUPPLY_LTTOT_CNT'))}세대"),
        ("모집공고일", _safe(item.get("RCRIT_PBLANC_DE"))),
        ("청약접수 시작일", _safe(item.get("RCEPT_BGNDE"))),
        ("청약접수 종료일", _safe(item.get("RCEPT_ENDDE"))),
        ("당첨자 발표일", _safe(item.get("PRZWNER_PRESNATN_DE"))),
        ("사업주체", _safe(item.get("BSNS_MBY_NM"))),
        ("시공사", _safe(item.get("CNSTRCT_ENTRPS_NM"))),
    ]

    for name, value in fields:
        embed.add_field(name=name, value=value, inline=True)

    return embed


def format_competition_rate(data: dict) -> discord.Embed:
    """경쟁률 임베드 생성"""
    items = data.get("data", [])

    if not items:
        return discord.Embed(
            title="📊 청약 경쟁률",
            description="조회 결과가 없습니다.",
            color=EMBED_COLOR,
        )

    embed = discord.Embed(
        title="📊 청약 경쟁률",
        description=f"공고번호: `{_safe(items[0].get('PBLANC_NO'))}`",
        color=EMBED_COLOR,
    )

    for item in items:
        house_ty = _safe(item.get("HOUSE_TY"))
        supply = _safe(item.get("SUPLY_HSHLDCO"))
        rcept = _safe(item.get("RCEPT_CNT"))
        rate = _safe(item.get("CMPET_RATE"))

        embed.add_field(
            name=f"🏠 {house_ty}",
            value=(
                f"공급세대: {supply}세대\n"
                f"접수건수: {rcept}건\n"
                f"경쟁률: **{rate}:1**"
            ),
            inline=True,
        )

    return embed


def format_winner_statistics(data: dict) -> discord.Embed:
    """당첨통계 임베드 생성"""
    items = data.get("data", [])

    if not items:
        return discord.Embed(
            title="🏆 당첨자 통계",
            description="조회 결과가 없습니다.",
            color=EMBED_COLOR,
        )

    embed = discord.Embed(
        title="🏆 당첨자 통계",
        description=f"공고번호: `{_safe(items[0].get('PBLANC_NO'))}`",
        color=EMBED_COLOR,
    )

    for item in items:
        region = _safe(item.get("SUBSCRPT_AREA_CODE_NM"))
        house_ty = _safe(item.get("HOUSE_TY"))
        supply = _safe(item.get("SUPLY_HSHLDCO"))

        embed.add_field(
            name=f"📍 {region} - {house_ty}",
            value=f"공급세대: {supply}세대",
            inline=True,
        )

    return embed


def format_error(message: str) -> discord.Embed:
    """에러 메시지 임베드 생성"""
    return discord.Embed(
        title="❌ 오류 발생",
        description=message,
        color=ERROR_COLOR,
    )


def format_notification_new(item: dict) -> discord.Embed:
    """새 공고 알림 임베드 생성"""
    name = _safe(item.get("HOUSE_NM"))
    area = _safe(item.get("SUBSCRPT_AREA_CODE_NM"))
    start = _safe(item.get("RCEPT_BGNDE"))
    end = _safe(item.get("RCEPT_ENDDE"))
    count = _safe(item.get("SUPPLY_LTTOT_CNT"))
    pblanc_no = _safe(item.get("PBLANC_NO"))

    embed = discord.Embed(
        title=f"🔔 새 분양 공고: {name}",
        description="새로운 분양 공고가 등록되었습니다!",
        color=SUCCESS_COLOR,
    )
    embed.add_field(name="📍 지역", value=area, inline=True)
    embed.add_field(name="🏗️ 공급세대", value=f"{count}세대", inline=True)
    embed.add_field(name="📅 접수기간", value=f"{start} ~ {end}", inline=False)
    embed.add_field(name="🔢 공고번호", value=f"`{pblanc_no}`", inline=False)
    embed.set_footer(text="'/청약 상세 공고번호'로 상세 정보를 확인하세요")

    return embed
