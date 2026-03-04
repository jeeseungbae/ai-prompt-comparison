from discord.ext import tasks
from discord.ext.commands import Bot
from loguru import logger

from bot.config import NOTIFICATION_CHECK_INTERVAL
from bot.services import formatter


def start_notification_checker(bot: Bot):
    """알림 체크 백그라운드 태스크 시작"""

    @tasks.loop(seconds=NOTIFICATION_CHECK_INTERVAL)
    async def check_new_announcements():
        """새 공고를 체크하고 등록된 채널에 알림 발송"""
        try:
            data = await bot.api.get_announcements(page=1, per_page=5)
            items = data.get("data", [])
            if not items:
                return

            last_checked_id = await bot.db.get_last_checked_id()

            new_items = []
            for item in items:
                pblanc_no = str(item.get("PBLANC_NO", ""))
                if pblanc_no == last_checked_id:
                    break
                new_items.append(item)

            if not new_items:
                return

            newest_id = str(items[0].get("PBLANC_NO", ""))
            await bot.db.set_last_checked_id(newest_id)

            channels = await bot.db.get_notification_channels()
            if not channels:
                return

            logger.info(
                f"새 공고 {len(new_items)}건 발견, {len(channels)}개 채널에 알림 발송"
            )

            for item in new_items:
                embed = formatter.format_notification_new(item)
                for ch_info in channels:
                    channel = bot.get_channel(ch_info["channel_id"])
                    if channel:
                        try:
                            await channel.send(embed=embed)
                        except Exception as e:
                            logger.warning(
                                f"채널 {ch_info['channel_id']} 알림 발송 실패: {e}"
                            )

        except Exception as e:
            logger.error(f"알림 체크 중 오류 발생: {e}")

    @check_new_announcements.before_loop
    async def before_check():
        await bot.wait_until_ready()

    check_new_announcements.start()
