from common.RoleUtil import RoleUtil
from cogs.RoleManager import RoleManager
from common.PoliceResponseUtil import PoliceResponseUtil
from common.NicknameUtil import NicknameUtil
from common.PoliceUtil import PoliceUtil
from common.Util import Util
from discord.ext import commands 
from discord import User, Message

class PoliceControl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name = 'police', invoke_without_command=True)
    async def police(self, ctx:commands.Context, *attr):
        msg = "如何使用警察?\n"
        msg+= "\n"
        msg+= "!police set <警察類型> <@用戶名> 在接下來一個小時內如果用戶發言, 警察就會警告\n"
        msg+= "    警察類型:\n"
        msg+= "        SLEEP: 睡覺\n"
        msg+= "          EAT: 吃飯\n"
        msg+= "       SHOWER: 洗澡\n"
        msg+= "        STUDY: 讀書\n"
        msg+= "     HOMEWORK: 寫作業\n"
        msg+= "\n"
        msg+= "!police lookup <@用戶名> 查看目前用戶是否被警察監視\n"
        msg+= "!police clear <@用戶名> 取消用戶目前的警察\n"
        await ctx.send(msg)
    
    @commands.Cog.listener('on_message')
    async def police_watch_message(self, message:Message):
        if message.author.bot:
            return # 無視機器人的消息
        currentType = PoliceUtil.getCurrentPoliceType(guild_id=message.guild.id, user_id=message.author.id)
        if len(currentType) > 0:
            user_name = await NicknameUtil.get_user_nickname_or_default(guild=message.guild, user=message.author)
            msg = PoliceResponseUtil.getResponse().format_map({'name': user_name,'action': PoliceUtil.getPoliceTypeChineseName(currentType)})
            await message.reply(msg)
    
    @police.command(name = "set")
    async def set_police(self, ctx:commands.Context, type: str, user: User):
        if not await self.canRunCommand(ctx, ctx.author):
            await ctx.channel.send(f"你不是警察, 無法執行這個指令")
            return
        if not PoliceUtil.isProperType(type):
            await ctx.channel.send(f"'{type}' 不是正確的警察類型, 請重新輸入")
            return
        guild_id = ctx.guild.id
        currentType = PoliceUtil.getCurrentPoliceType(guild_id=guild_id, user_id=user.id)
        user_name = await NicknameUtil.get_user_nickname_or_default(ctx.guild, user)
        if len(currentType) > 0:
            await ctx.channel.send(f"{user_name}已經被{PoliceUtil.getPoliceTypeChineseName(currentType)}警察監視了, 無法增加更多警力!!")
            return    
        PoliceUtil.createNewPolice(guild_id=guild_id, user_id=user.id, type=type)
        await ctx.channel.send(f"{user_name}現在已經被{PoliceUtil.getPoliceTypeChineseName(type)}警察監視啦!")

    @police.command(name = "lookup")
    async def lookup_police(self, ctx:commands.Context, user: User):
        if not await self.canRunCommand(ctx, ctx.author):
            await ctx.channel.send(f"你不是警察, 無法執行這個指令")
            return
        guild_id = ctx.guild.id
        currentType = PoliceUtil.getCurrentPoliceType(guild_id=guild_id, user_id=user.id)
        user_name = await NicknameUtil.get_user_nickname_or_default(guild=ctx.guild, user=user)
        if len(currentType) > 0:
            await ctx.channel.send(f"{user_name}現在被{PoliceUtil.getPoliceTypeChineseName(currentType)}警察監視中!!")
        else:
            await ctx.channel.send(f"{user_name}沒有被監視")
    
    @police.command(name = "clear")
    async def clear_police(self, ctx:commands.Context, user: User):
        if not await self.canRunCommand(ctx, ctx.author):
            await ctx.channel.send(f"你不是警察, 無法執行這個指令")
            return
        guild_id = ctx.guild.id
        user_name = await NicknameUtil.get_user_nickname_or_default(ctx.guild, user)
        if PoliceUtil.stopPolice(guild_id=guild_id, user_id=user.id):
            await ctx.channel.send(f"已經停止對{user_name}的監視")
        else:
            await ctx.channel.send(f"我們沒有在監視{user_name}啊... 還是說你想...?")

    async def canRunCommand(self, ctx: commands.Context, user: User):
        roleId = RoleUtil.getCategoryRole(guild_id=ctx.guild.id, category=Util.RoleCategory.KFP_UTIL)
        for role in ctx.guild.roles:
            if role.id == roleId:
                for member in role.members:
                    if user.id == member.id:
                        return True
        return False

def setup(bot):
    bot.add_cog(PoliceControl(bot))