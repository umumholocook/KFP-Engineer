from common.RPGUtil.StatusType import StatusType
from discord.ext import commands

# 簡單的Status Update, 目的是讓用戶知道Status的效果已經執行完畢了
class StatusUpdate():
    __member_id: int
    __guild_id: int
    __type: StatusType

    def __init__(self, member_id: int, guild_id: int, type: StatusType):
        self.__member_id = member_id
        self.__guild_id = guild_id
        self.__type = type
    
    async def sendMessage(self, bot: commands.Bot):
        guild = bot.get_guild(self.__guild_id)
        member = guild.get_member(self.__member_id)

        if member:
            await member.send(self.__getMessage())

    def __getMessage(self):
        if self.__type == StatusType.REST:
            return "休息結束, 你的體力已經完全恢復."