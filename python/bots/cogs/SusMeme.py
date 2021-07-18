from typing import List
from common.NicknameUtil import NicknameUtil
from common.SusMemeGenerator import SusMemeGenerator
import requests
import io
from PIL import Image
from discord.ext import commands
from discord import User, File, Embed

class SusMeme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name = 'sus', invoke_without_command=True)
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def sus_group(self, ctx:commands.Context, user:User):
        avatar = self.downloadUserAvatar(user)

        user_name = await NicknameUtil.get_user_nickname_or_default(ctx.guild, user)
        imagePath = SusMemeGenerator.createGif(user_name, avatar)
        
        embedMsg = Embed()
        embedMsg.set_image(url='attachment://sus.gif')

        img = File(imagePath, filename="sus.gif")
        await ctx.reply(file=img, embed=embedMsg)
    
    @sus_group.error
    async def sus_error(self, ctx:commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = "等一下, 我還在忙..."
            await ctx.reply(msg)
        else:
            msg = "我才剛忙完... 讓我休息一下"
            await ctx.reply(msg)
    
    @sus_group.command(name = "no_icon")
    async def eject(self, ctx:commands.Command, user:User):
        user_name = await NicknameUtil.get_user_nickname_or_default(ctx.guild, user)
        imagePath = SusMemeGenerator.createGifWithoutAvatar(user_name)
        
        embedMsg = Embed()
        embedMsg.set_image(url='attachment://sus.gif')

        img = File(imagePath, filename="sus.gif")
        await ctx.reply(file=img, embed=embedMsg)
    
    @sus_group.command(name = "help")
    async def show_help_message(self, ctx:commands.Command):
        msg = "如何使用sus\n"
        msg+= "!sus <@用戶名> 生成一個用戶名或著用戶暱稱的被票圖"
        msg+= "!sus no_icon <@用戶名> 生成一個不使用頭像的被票圖"

        await ctx.send(msg)

    def downloadUserAvatar(self, user: User):
        avatar_url = user.avatar_url
        data = requests.get(avatar_url).content
        return Image.open(io.BytesIO(data))

def setup(client):
    client.add_cog(SusMeme(client))