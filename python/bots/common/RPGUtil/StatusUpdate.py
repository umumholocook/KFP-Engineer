from common.RPGUtil.StatusType import StatusType
from discord.ext import commands

# 簡單的Status Update, 目的是讓用戶知道Status的效果已經執行完畢了
class StatusUpdate():
    member_id: int
    guild_id: int
    type: StatusType

    def __init__(self, member_id: int, guild_id: int, type: StatusType):
        self.member_id = member_id
        self.guild_id = guild_id
        self.type = type
    
    async def sendMessage(self, bot: commands.Bot):
        guild = bot.get_guild(self.guild_id)
        member = guild.get_member(self.member_id)
        if member.id == bot.id:
            return
        if member:
            await member.send(self.__getMessage())

    def __getMessage(self):
        if self.type == StatusType.REST:
            return "休息結束, 你的體力已經完全恢復."
        if self.type == StatusType.COMA:
            return "Kiara看到Cali喜極而泣，順便把倒地的你給治好了"
