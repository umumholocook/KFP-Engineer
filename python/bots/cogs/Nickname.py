from common.models.NicknameModel import NicknameModel
import random
from common.NicknameUtil import NicknameUtil
from discord import User, Member
from discord.ext import commands

class Nickname(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name = 'nickname', invoke_without_command=True)
    async def nickname(self, ctx:commands.Context, *attr):
        msg = "如何使用暱稱這個功能\n"
        msg+= "\n"
        msg+= "!nickname list <@用戶名> 顯示用戶的暱稱\n"
        msg+= "!nickname set <@用戶名> <暱稱> 設定用戶的暱稱\n"
        msg+= "!nickname remove <@用戶名> <暱稱> 移除用戶的暱稱\n"
        msg+= "!nickname clear <@用戶名> 清空用戶所有的暱稱\n"
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

    @nickname.command(name = "secret_set")
    async def secret_set_nickname(self, ctx:commands.Context, user_name: str, name:str):
        if str(self.bot.user.id) in name:
            await ctx.channel.send(f"{name}不能當成暱稱使用")
            return
        user = self.findUserByName(user_name)
        if not user:
            await ctx.channel.send(f"找不到{name}")
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
    
    @nickname.command(name = "list_details")
    async def get_all_nickname_details(self, ctx:commands.Context, user: User):
        nicknames = NicknameUtil.get_all_nicknames_detail(ctx.guild.id, user.id)
        if len(nicknames) < 1:
            await ctx.channel.send(f"{user.name}沒有任何暱稱.")
            return
        result = f"{user.name}有以下暱稱:\n"
        nickname: NicknameModel
        for nickname in nicknames:
            result += f"  {nickname.id}.{nickname.nick_name}"
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

    @nickname.command(name = "remove_id")
    async def remove_nickname(self, ctx:commands.Context, user: User, name_id: int):
        nicknames = NicknameUtil.get_all_nicknames(ctx.guild.id, user.id)
        if len(nicknames) < 1:
            await ctx.channel.send(f"{user.name}沒有任何暱稱.")
            return
        if not NicknameUtil.remove_nickname_id(ctx.guild.id, user.id, name_id):
            await ctx.channel.send(f"{name_id} 並不存在於 {user.name}的暱稱裡, 因此無法刪除.")
            return
        await ctx.channel.send(f"{user.name}的暱稱{name_id}刪除成功.")
    
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

    def findUserByName(self, user_name: str):
        members = self.bot.get_all_members()
        member: Member
        for member in members:
            if user_name in member.display_name:
                return self.bot.get_user(member.id)
        return None

def setup(bot):
    bot.add_cog(Nickname(bot))