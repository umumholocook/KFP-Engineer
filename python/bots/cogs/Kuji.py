import random
from discord.ext import commands
from datetime import datetime

class Kuji(commands.Cog):

    def __init__(self, client):
        self.bot = client
        self.timeZone = "Asia/Taipei"
        # self.timeZone = "America/Los_Angeles"
        # self.db = KujiDb(timeZone = self.timeZone)

    @commands.group(name = 'kuji', invoke_without_command = True)
    async def kuji_group(self, ctx:commands.Context, *attr):
        helptext = "```"
        helptext+="KFP抽籤bot, 每人每種籤一天限抽一次\n"
        helptext+="!kuji jp - 抽日本淺草觀音寺籤\n"
        helptext+="!kuji cn - 抽易經64籤\n"
        helptext+="!kuji ls - 抽龍山寺觀音籤\n"
        helptext+="!kuji shake - 搖一下籤筒\n"
        helptext+="!kuji history - 查看之前抽到的籤\n"
        helptext+="```"
        await ctx.send(helptext)

    @kuji_group.command(name = "shake")
    async def shake(self, ctx:commands.Command, *argv):
        random.seed(datetime.now())
        channel = self.bot.get_channel(ctx.channel.id)
        random.seed(random.random())
        msg = await channel.send("搖...")
        random.seed(random.random())
        await msg.edit(content = str(msg.content)+" 搖...")
        random.seed(random.random())
        await msg.edit(content = str(msg.content)+" 搖...")

def setup(client):
    client.add_cog(Kuji(client))