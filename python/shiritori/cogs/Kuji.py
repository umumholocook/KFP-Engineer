import random
from discord import Embed
import discord
from discord.ext import commands
from data.omikuji import OMIKUJI
from cogs.KujiUtil import KujiUtil
from datetime import date

class Kuji(commands.Cog):

    def __init__(self, client):
        self.bot = client

    @commands.group(name = 'kuji', invoke_without_command = True)
    async def kuji_group(self, ctx:commands.Command, *attr):
        helptext = "```"
        helptext+="KFP抽籤bot, 每人每種籤一天限抽一次\n"
        helptext+="!kuji jp - 抽日本淺草觀音寺籤\n"
        helptext+="!kuji cn - 抽易經64籤\n"
        helptext+="!kuji shake - 搖一下籤筒\n"
        helptext+="```"
        await ctx.send(helptext)
    
    @kuji_group.command(name = "shake")
    async def draw_jp(self, ctx:commands.Command, *argv):
        channel = self.bot.getChannel(ctx.channel.id)
        random.seed = random.randint(0, 100)
        msg = await channel.send("搖... ")
        random.seed = random.randint(0, 100)
        await msg.edit(contnet= str(msg.content)+ "搖... ")
        random.seed = random.randint(0, 100)
        await msg.edit(contnet= str(msg.content)+ "搖... ")

    @kuji_group.command(name = "jp")
    async def draw_jp(self, ctx:commands.Command, *argv):
        index = random.randint(0, 98)
        kuji = OMIKUJI[index]
        status = kuji["status"]
        img = discord.File(KujiUtil.getImageUrl(status), filename=KujiUtil.getImageName(status))
        await ctx.channel.send(file=img, embed=self.createEmbededJp(kuji))

    @kuji_group.command(name = "cn")
    async def draw_cn(self, ctx:commands.Command, *argv):
        pass

    def createEmbededJp(self, kuji):
        today = date.today()
        status = kuji["status"]
        title = today.strftime("%Y年%m月%d日")
        imageUri = 'attachment://{}'.format(KujiUtil.getImageName(status))
        title+= ", {}籤 · {}".format(kuji["title"], status)
        description = "{}\n".format(kuji["poem_line1"])
        description+= "`{}`\n".format(kuji["poem_line1_explain"])
        description+= "{}\n".format(kuji["poem_line2"])
        description+= "`{}`\n".format(kuji["poem_line2_explain"])
        description+= "{}\n".format(kuji["poem_line3"])
        description+= "`{}`\n".format(kuji["poem_line3_explain"])
        description+= "{}\n".format(kuji["poem_line4"])
        description+= "`{}`\n".format(kuji["poem_line4_explain"])
        embedMsg = Embed(title=title, description=description, color=KujiUtil.getColor(status))
        embedMsg.set_author(name="KFP抽籤bot")
        embedMsg.set_thumbnail(url=imageUri)
        payload = kuji["payload"]
        for key in payload:
            embedMsg.add_field(name=key, value=payload[key], inline=True)
        return embedMsg

def setup(client):
    client.add_cog(Kuji(client))