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
        if str(self.bot.user.id) in name:
            await ctx.channel.send(f"{name}不能當成暱稱使用")
            return
        result = NicknameUtil.set_nickname(ctx.guild.id, user.id, name)
        if result:
            await ctx.channel.send(f"新增用戶'{user.name}'新暱稱: {name} 成功!", )
        else:
            await ctx.channel.send(f"用戶暱稱'{name}'已經存在.")
    
    @nickname.command(name = "list")
    async def get_all_nickname(self, ctx:commands.Context, user: User):
        nicknames = NicknameUtil.get_all_nicknames(ctx.guild.id, user.id)
        if len(nicknames) < 1:
            await ctx.channel.send(f"{user.name}沒有任何暱稱.")
            return
        result = f"{user.name}有以下暱稱:\n"
        for index, nickname in enumerate(nicknames):
            result += f"  {index + 1}.{nickname}"
        await ctx.channel.send(result)

    @nickname.command(name = "remove")
    async def remove_nickname(self, ctx:commands.Context, user: User, name: str):
        nicknames = NicknameUtil.get_all_nicknames(ctx.guild.id, user.id)
        if len(nicknames) < 1:
            await ctx.channel.send(f"{user.name}沒有任何暱稱.")
            return
        if not NicknameUtil.remove_nickname(ctx.guild.id, user.id, name):
            await ctx.channel.send(f"{name} 並不是 {user.name}的暱稱, 因此無法刪除.")
            return
        await ctx.channel.send(f"{user.name}的暱稱{name}刪除成功.")
    
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