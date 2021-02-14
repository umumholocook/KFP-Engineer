import random
from discord import Embed
import discord
import pytz
from discord.ext import commands
from data.omikuji import OMIKUJI
from cogs.KujiUtil import KujiUtil
from datetime import date, datetime, timedelta
from database.KujiDb import KujiDb

class Kuji(commands.Cog):

    def __init__(self, client):
        self.bot = client
        self.timeZone = "Asia/Taipei"
        # self.timeZone = "America/Los_Angeles"
        self.db = KujiDb(timeZone = self.timeZone)

    @commands.group(name = 'kuji', invoke_without_command = True)
    async def kuji_group(self, ctx:commands.Command, *attr):
        helptext = "```"
        helptext+="KFP抽籤bot, 每人每種籤一天限抽一次\n"
        helptext+="!kuji jp - 抽日本淺草觀音寺籤\n"
        helptext+="!kuji cn - 抽易經64籤\n"
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

    @kuji_group.command(name = "clearRecord")
    async def clear_db(self, ctx:commands.Command, *argv):
        self.db.clearDb()

    @kuji_group.command(name = "jp")
    async def draw_jp(self, ctx:commands.Command, *argv):
        if not self.db.canDrawJp(ctx.author.id):
            await ctx.reply("同學, 你今天已經抽過了哦! 每人一天只限一次.")        
            return
        random.seed(random.random())
        index = random.randint(0, 98)
        kuji = OMIKUJI[index]
        status = kuji["status"]
        img = discord.File(KujiUtil.getImageUrl(status), filename=KujiUtil.getImageName(status))
        await ctx.reply(file=img, embed=self.createEmbededJp(kuji, datetime.now()))
        self.db.updateMemberJp(ctx.author.id, index)

    @kuji_group.command(name = "cn")
    async def draw_cn(self, ctx:commands.Command, *argv):
        if not self.db.canDrawCn(ctx.author.id):
            await ctx.reply("同學, 你今天已經抽過了哦! 每人一天只限一次.")
            return
        random.seed(random.random())
        yiIndex = KujiUtil.getYi()
        yi = KujiUtil.getTargetedYi(yiIndex[0], yiIndex[1])
        await ctx.reply(embed=self.createEmbededCn(yi, datetime.now()))
        self.db.updateMemberCn(ctx.author.id, yiIndex[0], yiIndex[1])

    @kuji_group.command(name = "history")
    async def get_history(self, ctx:commands.Command, *argv):
        historyJp = self.db.getHistoryJp(ctx.author.id)
        historyCn = self.db.getHistoryCn(ctx.author.id)
        if (-1, None) == historyJp and (-1, -1, None) == historyCn:
            await ctx.reply("同學, 你還沒抽過籤呢! 先試著抽一個看看？.")
        if not (-1, None) == historyJp:
            kuji = OMIKUJI[historyJp[0]]
            status = kuji["status"]
            img = discord.File(KujiUtil.getImageUrl(status), filename=KujiUtil.getImageName(status))
            await ctx.reply(file=img, embed=self.createEmbededJp(kuji, historyJp[1]))
        if not (-1, -1, None) == historyCn:
            yi = KujiUtil.getTargetedYi(historyCn[0], historyCn[1])
            await ctx.reply(embed=self.createEmbededCn(yi, historyCn[2]))

    def createEmbededCn(self, yi, timestamp):
        title = self.getTitle(timestamp)
        title+= "\n易經 · {} · {} {}".format(yi["name"], yi["shape"], yi["symbol"])
        embedMsg = Embed(title=title, description=yi["description"], color=KujiUtil.getYiColor(yi["name"]))
        embedMsg.set_author(name="KFP抽籤bot")
        payload = yi["payload"]
        for key in payload:
            embedMsg.add_field(name=key, value=payload[key], inline=True)
        return embedMsg


    def createEmbededJp(self, kuji, timestamp):
        status = kuji["status"]
        title = self.getTitle(timestamp)
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

    def getTitle(self, timestamp):
        timezone = pytz.timezone(self.timeZone)
        d_aware = timestamp.astimezone(timezone)
        return d_aware.strftime("%Y年%m月%d日")

def setup(client):
    client.add_cog(Kuji(client))