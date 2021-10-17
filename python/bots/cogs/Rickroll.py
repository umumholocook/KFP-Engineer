from discord.ext import commands
from discord import Embed, File, User
from common.Util import Util
from common.RickrollGenerator import RickrollGenerator

class Rickroll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name = 'rick', invoke_without_command=True)
    @commands.cooldown(1, 30, type=commands.BucketType.user)
    async def rick_group(self, ctx:commands.Context, user:User):
        if user.bot:
            avatar = Util.downloadUserAvatar(user=ctx.message.author)
        else: 
            avatar = Util.downloadUserAvatar(user=user)
        imagePath = RickrollGenerator.createGif(avatar)

        embedMsg = Embed()
        embedMsg.set_image(url='attachment://rickrolled.gif')

        img = File(imagePath, filename="rickrolled.gif")
        await ctx.send(file=img, embed=embedMsg)
        

    @rick_group.error
    async def rick_error(self, ctx:commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = "請勿過於頻繁使用本指令"
            await ctx.reply(msg)
        else:
            raise error

def setup(client):
    client.add_cog(Rickroll(client))