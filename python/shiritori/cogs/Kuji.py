import random
from discord import Embed
import discord
from discord.ext import commands
from data.omikuji import OMIKUJI
from cogs.KujiUtil import KujiUtil
from datetime import date, datetime
from database.KujiDb import KujiDb

class Kuji(commands.Cog):

    def __init__(self, client):
        self.bot = client
        self.db = KujiDb()

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
    async def shake(self, ctx:commands.Command, *argv):
        channel = self.bot.get_channel(ctx.channel.id)
        random.seed(datetime.now())
        msg = await channel.send("搖...")
        random.seed(datetime.now())
        await msg.edit(content = str(msg.content)+" 搖...")
        random.seed(datetime.now())
        await msg.edit(content = str(msg.content)+" 搖...")

    @kuji_group.command(name = "clearRecord")
    async def clear_db(self, ctx:commands.Command, *argv):
        self.db.clearDb()

    @kuji_group.command(name = "jp")
    async def draw_jp(self, ctx:commands.Command, *argv):
        if not self.db.canDrawJp(ctx.author.id):
            await ctx.channel.send("同學, 你今天已經抽過了哦! 每人一天只限一次.")        
            return
        index = random.randint(0, 98)
        kuji = OMIKUJI[index]
        status = kuji["status"]
        img = discord.File(KujiUtil.getImageUrl(status), filename=KujiUtil.getImageName(status))
        await ctx.channel.send(file=img, embed=self.createEmbededJp(kuji))
        self.db.updateMemberJp(ctx.author.id)

    @kuji_group.command(name = "cn")
    async def draw_cn(self, ctx:commands.Command, *argv):
        if not self.db.canDrawCn(ctx.author.id):
            await ctx.channel.send("同學, 你今天已經抽過了哦! 每人一天只限一次.")        
            return
        yi = KujiUtil.getYi()
        await ctx.channel.send(embed=self.createEmbededCn(yi))
        self.db.updateMemberCn(ctx.author.id)

    def createEmbededCn(self, yi):
        today = date.today()
        title = today.strftime("%Y年%m月%d日")
        title+= "\n易經 · {} · {} {}".format(yi["name"], yi["shape"], yi["symbol"])
        embedMsg = Embed(title=title, description=yi["description"], color=KujiUtil.getYiColor(yi["name"]))
        embedMsg.set_author(name="KFP抽籤bot")
        payload = yi["payload"]
        for key in payload:
            embedMsg.add_field(name=key, value=payload[key], inline=True)
        return embedMsg


    def createEmbededJp(self, kuji):
        today = date.today()
        status = kuji["status"]
        title = today.strftime("%Y年%m月%d日")
        imageUri = 'attachment://{}'.format(KujiUtil.getImageName(status))
        title+= "\n東京淺草觀音寺御神籤· {}籤 · {}".format(kuji["title"], status)
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