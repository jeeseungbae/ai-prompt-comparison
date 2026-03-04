import discord

from bot.services.formatter import (
    format_announcement_list,
    format_announcement_detail,
    format_competition_rate,
    format_winner_statistics,
    format_error,
    format_notification_new,
)


class TestFormatter:
    def test_format_announcement_list_with_data(self):
        """공고 목록 포맷"""
        data = {
            "data": [
                {
                    "PBLANC_NO": "2024000001",
                    "HOUSE_NM": "테스트 아파트",
                    "SUBSCRPT_AREA_CODE_NM": "서울",
                    "SUPPLY_LTTOT_CNT": 100,
                    "RCEPT_BGNDE": "2024-01-01",
                    "RCEPT_ENDDE": "2024-01-10",
                }
            ],
            "totalCount": 1,
        }
        embed = format_announcement_list(data)
        assert isinstance(embed, discord.Embed)
        embed_dict = embed.to_dict()
        assert "테스트 아파트" in str(embed_dict)

    def test_format_announcement_list_empty(self):
        """빈 목록 포맷"""
        data = {"data": [], "totalCount": 0}
        embed = format_announcement_list(data)
        assert isinstance(embed, discord.Embed)
        assert "조회 결과가 없습니다" in embed.description

    def test_format_announcement_detail(self):
        """상세 정보 포맷"""
        data = {
            "data": [
                {
                    "PBLANC_NO": "2024000001",
                    "HOUSE_NM": "테스트 아파트",
                    "HOUSE_SECD_NM": "APT",
                    "HSSPLY_ADRES": "서울특별시 강남구",
                    "SUPPLY_LTTOT_CNT": 100,
                    "RCRIT_PBLANC_DE": "2024-01-01",
                    "RCEPT_BGNDE": "2024-01-05",
                    "RCEPT_ENDDE": "2024-01-10",
                    "PRZWNER_PRESNATN_DE": "2024-01-20",
                    "BSNS_MBY_NM": "테스트 건설",
                    "CNSTRCT_ENTRPS_NM": "테스트 시공",
                }
            ]
        }
        embed = format_announcement_detail(data)
        assert isinstance(embed, discord.Embed)
        assert "테스트 아파트" in embed.title

    def test_format_announcement_detail_empty(self):
        """빈 상세 정보 포맷"""
        data = {"data": []}
        embed = format_announcement_detail(data)
        assert "조회 결과가 없습니다" in embed.description

    def test_format_competition_rate(self):
        """경쟁률 포맷"""
        data = {
            "data": [
                {
                    "PBLANC_NO": "2024000001",
                    "HOUSE_TY": "84A",
                    "SUPLY_HSHLDCO": 50,
                    "RCEPT_CNT": 250,
                    "CMPET_RATE": "5.00",
                }
            ]
        }
        embed = format_competition_rate(data)
        assert isinstance(embed, discord.Embed)
        assert "경쟁률" in embed.title

    def test_format_winner_statistics(self):
        """당첨통계 포맷"""
        data = {
            "data": [
                {
                    "PBLANC_NO": "2024000001",
                    "SUBSCRPT_AREA_CODE_NM": "서울",
                    "HOUSE_TY": "84A",
                    "SUPLY_HSHLDCO": 50,
                }
            ]
        }
        embed = format_winner_statistics(data)
        assert isinstance(embed, discord.Embed)
        assert "당첨자 통계" in embed.title

    def test_format_error(self):
        """에러 메시지 포맷"""
        embed = format_error("테스트 에러 메시지")
        assert isinstance(embed, discord.Embed)
        assert "테스트 에러 메시지" in embed.description

    def test_format_notification_new(self):
        """새 공고 알림 포맷"""
        item = {
            "PBLANC_NO": "2024000001",
            "HOUSE_NM": "테스트 아파트",
            "SUBSCRPT_AREA_CODE_NM": "서울",
            "SUPPLY_LTTOT_CNT": 100,
            "RCEPT_BGNDE": "2024-01-05",
            "RCEPT_ENDDE": "2024-01-10",
        }
        embed = format_notification_new(item)
        assert isinstance(embed, discord.Embed)
        assert "테스트 아파트" in embed.title
