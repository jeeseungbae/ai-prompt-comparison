from __future__ import annotations

from datetime import datetime, timezone

import discord

from bot.services.api_client import (
    AptAnnouncement,
    AptCompetition,
    WinnerAgeStat,
    WinnerAreaStat,
)


def _format_date(date_str: str | None) -> str:
    """YYYYMMDD 형식을 YYYY.MM.DD로 변환합니다."""
    if not date_str or len(date_str) < 8:
        return "-"
    return f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:8]}"


def _format_month(month_str: str | None) -> str:
    """YYYYMM 형식을 YYYY년 MM월로 변환합니다."""
    if not month_str or len(month_str) < 6:
        return "-"
    return f"{month_str[:4]}년 {month_str[4:6]}월"


def format_announcement_embed(ann: AptAnnouncement) -> discord.Embed:
    """단일 분양공고를 Embed로 포맷합니다."""
    embed = discord.Embed(
        title=f"\U0001f3e0 {ann.HOUSE_NM}",
        description=ann.HSSPLY_ADRES or "주소 정보 없음",
        color=discord.Color.blue(),
        timestamp=datetime.now(timezone.utc),
    )
    if ann.HMPG_ADRES:
        embed.url = ann.HMPG_ADRES

    embed.add_field(name="공급지역", value=ann.SUBSCRPT_AREA_CODE_NM or "-", inline=True)
    embed.add_field(
        name="총 공급세대",
        value=f"{ann.TOT_SUPLY_HSHLDCO:,}세대" if ann.TOT_SUPLY_HSHLDCO else "-",
        inline=True,
    )
    embed.add_field(name="주택구분", value=ann.HOUSE_SECD_NM or "-", inline=True)
    embed.add_field(name="모집공고일", value=_format_date(ann.RCRIT_PBLANC_DE), inline=True)
    embed.add_field(
        name="청약접수",
        value=f"{_format_date(ann.RCEPT_BGNDE)} ~ {_format_date(ann.RCEPT_ENDDE)}",
        inline=True,
    )
    embed.add_field(
        name="당첨자발표", value=_format_date(ann.PRZWNER_PRESNATN_DE), inline=True
    )

    if ann.CNTRCT_CNCLS_BGNDE:
        embed.add_field(
            name="계약기간",
            value=f"{_format_date(ann.CNTRCT_CNCLS_BGNDE)} ~ {_format_date(ann.CNTRCT_CNCLS_ENDDE)}",
            inline=False,
        )

    embed.set_footer(text="청약홈 | data.go.kr")
    return embed


def format_announcement_list_embed(
    announcements: list[AptAnnouncement], region: str | None = None
) -> discord.Embed:
    """분양정보 목록을 Embed로 포맷합니다."""
    title = "최근 APT 분양정보"
    if region:
        title += f" ({region})"

    if not announcements:
        embed = discord.Embed(
            title=title,
            description="조회된 분양정보가 없습니다.",
            color=discord.Color.greyple(),
        )
        embed.set_footer(text="청약홈 | data.go.kr")
        return embed

    embed = discord.Embed(
        title=title,
        color=discord.Color.blue(),
        timestamp=datetime.now(timezone.utc),
    )

    # 최대 10개까지 표시
    for ann in announcements[:10]:
        supply = f"{ann.TOT_SUPLY_HSHLDCO:,}세대" if ann.TOT_SUPLY_HSHLDCO else "미정"
        region_name = ann.SUBSCRPT_AREA_CODE_NM or ""
        date = _format_date(ann.RCRIT_PBLANC_DE)
        embed.add_field(
            name=ann.HOUSE_NM,
            value=f"{region_name} | {supply} | 공고일 {date}",
            inline=False,
        )

    if len(announcements) > 10:
        embed.set_footer(
            text=f"총 {len(announcements)}건 중 10건 표시 | 청약홈 | data.go.kr"
        )
    else:
        embed.set_footer(text=f"총 {len(announcements)}건 | 청약홈 | data.go.kr")

    return embed


def format_competition_embed(
    house_name: str, competitions: list[AptCompetition]
) -> discord.Embed:
    """경쟁률 데이터를 Embed로 포맷합니다."""
    if not competitions:
        embed = discord.Embed(
            title=f"경쟁률: {house_name}",
            description="조회된 경쟁률 정보가 없습니다.",
            color=discord.Color.greyple(),
        )
        embed.set_footer(text="청약홈 | data.go.kr")
        return embed

    embed = discord.Embed(
        title=f"경쟁률: {house_name}",
        color=discord.Color.orange(),
        timestamp=datetime.now(timezone.utc),
    )

    # 주택형별로 그룹핑해서 표시
    seen_types: dict[str, list[str]] = {}
    for comp in competitions:
        house_ty = comp.HOUSE_TY or "미분류"
        if house_ty not in seen_types:
            seen_types[house_ty] = []

        rank = comp.SUBSCRPT_RANK_CODE or "-"
        region = comp.RESIDE_SENM or "-"
        supply = f"{comp.SUPLY_HSHLDCO}세대" if comp.SUPLY_HSHLDCO else "-"
        req_cnt = f"{comp.REQ_CNT:,}건" if comp.REQ_CNT is not None else "-"
        rate = comp.CMPET_RATE or "-"

        line = f"{rank} | {region} | 공급 {supply} | 접수 {req_cnt} | 경쟁률 {rate}"
        seen_types[house_ty].append(line)

    for house_ty, lines in list(seen_types.items())[:25]:  # Embed 필드 25개 제한
        value = "\n".join(lines[:5])  # 주택형당 최대 5줄
        if len(value) > 1024:
            value = value[:1021] + "..."
        embed.add_field(name=f"주택형 {house_ty}", value=value, inline=False)

    embed.set_footer(text="청약홈 | data.go.kr")
    return embed


def format_winner_stats_embed(
    area_stats: list[WinnerAreaStat],
    age_stats: list[WinnerAgeStat],
    period: str = "",
) -> discord.Embed:
    """당첨자 통계를 Embed로 포맷합니다."""
    title = "청약 당첨자 통계"
    if period:
        title += f" ({period})"

    if not area_stats and not age_stats:
        embed = discord.Embed(
            title=title,
            description="조회된 통계 데이터가 없습니다.",
            color=discord.Color.greyple(),
        )
        embed.set_footer(text="청약홈 | data.go.kr")
        return embed

    embed = discord.Embed(
        title=title,
        color=discord.Color.green(),
        timestamp=datetime.now(timezone.utc),
    )

    # 지역별 통계
    if area_stats:
        area_lines = []
        for stat in area_stats[:15]:
            region = stat.SUBSCRPT_AREA_CODE_NM or "-"
            general_supply = f"{stat.SUPLY_HSHLDCO:,}" if stat.SUPLY_HSHLDCO else "-"
            general_req = f"{stat.SUPLY_REQ_CNT:,}" if stat.SUPLY_REQ_CNT else "-"
            general_rate = stat.SUPLY_CMPET_RATE or "-"
            area_lines.append(
                f"**{region}**: 공급 {general_supply} / 접수 {general_req} / 경쟁률 {general_rate}"
            )
        area_value = "\n".join(area_lines)
        if len(area_value) > 1024:
            area_value = area_value[:1021] + "..."
        embed.add_field(name="지역별 일반공급 현황", value=area_value, inline=False)

    # 연령별 통계
    if age_stats:
        age_lines = []
        for stat in age_stats[:10]:
            age = stat.AGE_SE or "-"
            count = f"{stat.PRZWNER_CNT:,}명" if stat.PRZWNER_CNT is not None else "-"
            rate = stat.PRZWNER_RATE or "-"
            age_lines.append(f"**{age}**: {count} ({rate})")
        age_value = "\n".join(age_lines)
        if len(age_value) > 1024:
            age_value = age_value[:1021] + "..."
        embed.add_field(name="연령별 당첨자 현황", value=age_value, inline=False)

    embed.set_footer(text="청약홈 | data.go.kr")
    return embed
