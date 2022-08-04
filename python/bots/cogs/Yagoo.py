from pydoc import describe
import discord

from discord.embeds import Embed
from discord.file import File
from common.YagooUtil import YagooUtil
from discord.ext import commands
from discord import app_commands

class YagooMeme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name = 'yagoo', description="Best Girl 跟你打招呼, 最多四個字")
    @commands.cooldown(1, 3, type=commands.BucketType.user)
    async def yagoo_group(self, interaction: discord.Interaction, text: str = "早安你好"):
        imageInfo = YagooUtil.drawYagoo(text)

        tempFileName = imageInfo[0]
        tempFilePath = imageInfo[1]

        embedMsg = Embed()
        embedMsg.set_image(url='attachment://' + tempFileName)
        image = File(tempFilePath, filename=tempFileName)
        await interaction.response.defer()
        await interaction.followup.send(file=image)

    @yagoo_group.error
    async def rps_error(self, ctx:commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = "指令太快, 請等{:.2f}秒".format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

async def setup(client):
    await client.add_cog(YagooMeme(client))