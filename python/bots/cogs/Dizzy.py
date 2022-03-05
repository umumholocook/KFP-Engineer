from discord.embeds import Embed
from discord.file import File
from common.YagooUtil import YagooUtil
from discord.ext import commands

class DizzyMeme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name = 'dizzy', invoke_without_command=True)
    @commands.cooldown(1, 3, type=commands.BucketType.user)
    async def yagoo_group(self, ctx:commands.Context, text: str = "阿暈你好"):
        imagePath = YagooUtil.renderDizzyText(text)

        embedMsg = Embed()
        embedMsg.set_image(url='attachment://' + YagooUtil.getTempFileName())
        image = File(imagePath, filename=YagooUtil.getTempFileName())
        await ctx.message.delete()
        await ctx.send(file=image)

    @yagoo_group.error
    async def rps_error(self, ctx:commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = "指令太快, 請等{:.2f}秒".format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

def setup(client):
    client.add_cog(DizzyMeme(client))