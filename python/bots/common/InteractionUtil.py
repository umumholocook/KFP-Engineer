import discord
from common.ChannelUtil import ChannelUtil
from common.Util import Util


class InteractionUtil:
    @staticmethod
    async def require_channel(interaction: discord.Interaction, channel_type: Util.ChannelType) -> bool:
        if not interaction.guild or not interaction.channel:
            await interaction.response.send_message("此指令只能在伺服器頻道中使用。", ephemeral=True)
            return False
        if not ChannelUtil.hasChannel(interaction.guild.id, interaction.channel.id, channel_type):
            await interaction.response.send_message("此頻道無法使用此指令。", ephemeral=True)
            return False
        return True

    @staticmethod
    async def respond(interaction: discord.Interaction, content: str = None, **kwargs):
        if interaction.response.is_done():
            await interaction.followup.send(content, **kwargs)
        else:
            await interaction.response.send_message(content, **kwargs)