from discord.ext import commands
from discord import app_commands
import discord
from loguru import logger


class NotificationCog(commands.Cog):
    """알림 설정 명령어"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    notification = app_commands.Group(name="알림설정", description="새 공고 알림 채널 설정")

    @notification.command(name="등록", description="현재 채널을 새 공고 알림 채널로 등록합니다")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def register(self, interaction: discord.Interaction):
        """현재 채널을 알림 채널로 등록"""
        await interaction.response.defer(ephemeral=True)
        try:
            channel_id = interaction.channel_id
            guild_id = interaction.guild_id
            logger.info(f"알림 채널 등록 - 채널: {channel_id}, 서버: {guild_id}")
            await self.bot.db.add_notification_channel(
                channel_id=channel_id, guild_id=guild_id
            )
            embed = discord.Embed(
                title="알림 채널 등록 완료",
                description=(
                    f"<#{channel_id}> 채널이 새 공고 알림 채널로 등록되었습니다.\n"
                    "새로운 분양 공고가 올라오면 이 채널에 알림을 보내드립니다."
                ),
                color=discord.Color.green(),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"알림 채널 등록 실패: {e}")
            embed = discord.Embed(
                title="등록 실패",
                description=f"알림 채널 등록 중 오류가 발생했습니다: {e}",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @notification.command(name="해제", description="현재 채널의 알림 설정을 해제합니다")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unregister(self, interaction: discord.Interaction):
        """현재 채널의 알림 설정 해제"""
        await interaction.response.defer(ephemeral=True)
        try:
            channel_id = interaction.channel_id
            logger.info(f"알림 채널 해제 - 채널: {channel_id}")
            removed = await self.bot.db.remove_notification_channel(
                channel_id=channel_id
            )
            if removed:
                embed = discord.Embed(
                    title="알림 채널 해제 완료",
                    description=f"<#{channel_id}> 채널의 알림 설정이 해제되었습니다.",
                    color=discord.Color.green(),
                )
            else:
                embed = discord.Embed(
                    title="등록된 채널 없음",
                    description="현재 채널은 알림 채널로 등록되어 있지 않습니다.",
                    color=discord.Color.yellow(),
                )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"알림 채널 해제 실패: {e}")
            embed = discord.Embed(
                title="해제 실패",
                description=f"알림 채널 해제 중 오류가 발생했습니다: {e}",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @notification.command(name="확인", description="현재 채널의 알림 등록 여부를 확인합니다")
    async def check(self, interaction: discord.Interaction):
        """현재 채널의 알림 등록 여부 확인"""
        await interaction.response.defer(ephemeral=True)
        try:
            channel_id = interaction.channel_id
            channels = await self.bot.db.get_notification_channels()
            registered_ids = {ch["channel_id"] for ch in channels}
            if channel_id in registered_ids:
                embed = discord.Embed(
                    title="알림 채널 등록됨",
                    description=(
                        f"<#{channel_id}> 채널은 현재 알림 채널로 등록되어 있습니다.\n"
                        "새로운 분양 공고 알림을 수신합니다."
                    ),
                    color=discord.Color.blue(),
                )
            else:
                embed = discord.Embed(
                    title="알림 채널 미등록",
                    description=(
                        f"<#{channel_id}> 채널은 알림 채널로 등록되어 있지 않습니다.\n"
                        "`/알림설정 등록` 명령어로 등록할 수 있습니다."
                    ),
                    color=discord.Color.light_grey(),
                )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"알림 채널 확인 실패: {e}")
            embed = discord.Embed(
                title="확인 실패",
                description=f"알림 설정 확인 중 오류가 발생했습니다: {e}",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @register.error
    @unregister.error
    async def permission_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                title="권한 부족",
                description="이 명령어는 **채널 관리** 권한이 필요합니다.",
                color=discord.Color.red(),
            )
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(NotificationCog(bot))
