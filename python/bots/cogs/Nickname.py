import random
from common.NicknameUtil import NicknameUtil
from discord import User
from discord.ext import commands

class Nickname(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name = 'nickname', invoke_without_command=True)
    async def nickname(self, ctx:commands.Context, *attr):
        msg = "如何使用暱稱\n"
        msg+= "\n"
        msg+= "!nickname set <@用戶名> <暱稱> 設定用戶的暱稱\n"
        msg+= "!nickname clear <@用戶名> 清空用戶的暱稱\n"
        await ctx.send(msg)

    @nickname.command(name = "set")
    async def set_nickname(self, ctx:commands.Context, user: User, name:str):
        NicknameUtil.set_nickname(ctx.guild.id, user.id, name)
        await ctx.channel.send(f"新增用戶'{user.name}'新暱稱: {name} 成功!", )
    
    @nickname.command(name = "clear")
    async def clear_nickname(self, ctx:commands.Context, user: User):
        NicknameUtil.clear_nickname(ctx.guild.id, user.id)
        await ctx.channel.send(f"清除用戶'{user.name}'暱稱成功!", )

    @nickname.command(name = "get")
    async def get_nickname(self, ctx:commands.Context, user: User):
        nicknames = NicknameUtil.get_all_nicknames(ctx.guild.id, user.id)
        if len(nicknames) > 0:
            nickname_to_use = random.choice(nicknames)
            await ctx.channel.send(nickname_to_use)
        else:
            await ctx.channel.send(f"用戶'{user.name}'沒有任何暱稱.")

def setup(bot):
    bot.add_cog(Nickname(bot))