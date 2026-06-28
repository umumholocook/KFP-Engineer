import discord
from common.DiscordUtil import DiscordUtil
from common.RPGUtil.StatusType import StatusType
from discord.ext import commands


class StatusUpdate:
    member_id: int
    guild_id: int
    type: StatusType

    def __init__(self, member_id: int, guild_id: int, type: StatusType):
        self.member_id = member_id
        self.guild_id = guild_id
        self.type = type

    async def sendMessage(self, bot: commands.Bot):
        guild = bot.get_guild(self.guild_id)
        if guild is None:
            try:
                guild = await bot.fetch_guild(self.guild_id)
            except (discord.NotFound, discord.HTTPException):
                return

        member = await DiscordUtil.fetch_guild_member(guild, self.member_id)
        if member is None or member.id == bot.user.id:
            return

        await DiscordUtil.send_user_dm(member, self.__getMessage())

    def __getMessage(self):
        if self.type == StatusType.REST:
            return "休息結束, 你的體力已經完全恢復."
        if self.type == StatusType.COMA:
            return "Kiara看到Cali喜極而泣，順便把倒地的你給治好了"
        return ""