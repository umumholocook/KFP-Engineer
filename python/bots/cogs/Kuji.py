from common.MemberUtil import MemberUtil
import random
from common.KujiUtil import KujiUtil
from datetime import datetime
from discord import File
from discord.ext import commands
from resource.data.lungshan import LUNGSHAN
from resource.data.omikuji import OMIKUJI
from ui.Kuji.KujiEmbed import KujiEmbed

class Kuji(commands.Cog):

    def __init__(self, client):
        self.bot = client
    
    __RATE = 2

    @commands.group(name = 'kuji', invoke_without_command = True)
    async def kuji_group(self, ctx:commands.Context, *attr):
        helptext = "```"
        helptext+="抽籤遊戲, 每人每種籤一天限抽一次, 一次 {}隻雞腿\n".format(self.__RATE)
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

    @kuji_group.command(name = "clearRecord")
    async def clear_db(self, ctx:commands.Command, *argv):
        KujiUtil.clearData()

    @kuji_group.command(name = "jp")
    async def draw_jp(self, ctx:commands.Command, *argv):
        if not KujiUtil.canDrawJp(ctx.author.id):
            await ctx.reply("親愛的員工, 你今天已經抽過清水寺籤了哦! 每人一天只限一次.")        
            return
        if not await self.checkToken(ctx):
            return
        random.seed(random.random())
        index = random.randint(0, 98)
        kuji = OMIKUJI[index]
        status = kuji["status"]
        img = File(KujiUtil.getImageUrl(status), filename=KujiUtil.getImageName(status))
        await ctx.reply(file=img, embed=KujiEmbed.createEmbededJp(kuji, datetime.now(), f"{self.bot.user.name} - 抽籤遊戲"))
        KujiUtil.updateMemberJp(ctx.author.id, index)

    @kuji_group.command(name = "ls")
    async def draw_ls(self, ctx:commands.Command, *argv):
        if not KujiUtil.canDrawLs(ctx.author.id):
            await ctx.reply("親愛的員工, 你今天已經抽過龍山寺籤了哦! 每人一天只限一次.")        
            return
        if not await self.checkToken(ctx):
            return
        random.seed(random.random())
        index = random.randint(0, 98)
        ls = LUNGSHAN[index]
        status = ls["status"]
        img = File(KujiUtil.getImageUrlLs(status), filename=KujiUtil.getImageNameLs(status))
        await ctx.reply(file=img, embed=KujiEmbed.createEmbededLs(ls, datetime.now(), f"{self.bot.user.name} - 抽籤遊戲"))
        KujiUtil.updateMemberLs(ctx.author.id, index)

    @kuji_group.command(name = "cn")
    async def draw_cn(self, ctx:commands.Command, *argv):
        if not KujiUtil.canDrawCn(ctx.author.id):
            await ctx.reply("親愛的員工, 你今天已經抽過易經了哦! 每人一天只限一次.")
            return
        if not await self.checkToken(ctx):
            return
        random.seed(random.random())
        yiIndex = KujiUtil.getYi()
        yi = KujiUtil.getTargetedYi(yiIndex[0], yiIndex[1])
        await ctx.reply(embed=KujiEmbed.createEmbededCn(yi, datetime.now(), f"{self.bot.user.name} - 抽籤遊戲"))
        KujiUtil.updateMemberCn(ctx.author.id, yiIndex[0], yiIndex[1])

    @kuji_group.command(name = "history")
    async def get_history(self, ctx:commands.Command, *argv):
        historyJp = KujiUtil.getHistoryJp(ctx.author.id)
        historyCn = KujiUtil.getHistoryCn(ctx.author.id)
        historyLs = KujiUtil.getHistoryLs(ctx.author.id)
        if (-1, None) == historyJp and (-1, None) == historyLs and (-1, -1, None) == historyCn:
            await ctx.reply("親愛的員工, 你還沒抽過籤呢! 先試著抽一個看看？.")
        if not (-1, None) == historyLs:
            ls = LUNGSHAN[historyLs[0]]
            status = ls["status"]
            img = File(KujiUtil.getImageUrlLs(status), filename=KujiUtil.getImageNameLs(status))
            await ctx.reply(file=img, embed=KujiEmbed.createEmbededLs(ls, datetime.now(), f"{self.bot.user.name} - 抽籤遊戲"))

        if not (-1, None) == historyJp:
            kuji = OMIKUJI[historyJp[0]]
            status = kuji["status"]
            img = File(KujiUtil.getImageUrl(status), filename=KujiUtil.getImageName(status))
            await ctx.reply(file=img, embed=KujiEmbed.createEmbededJp(kuji, historyJp[1], f"{self.bot.user.name} - 抽籤遊戲"))

        if not (-1, -1, None) == historyCn:
            yi = KujiUtil.getTargetedYi(historyCn[0], historyCn[1])
            await ctx.reply(embed=KujiEmbed.createEmbededCn(yi, historyCn[2], f"{self.bot.user.name} - 抽籤遊戲"))

    async def checkToken(self, ctx:commands.Command):
        member = MemberUtil.get_or_add_member(ctx.author.id)
        if member.token < self.__RATE:
            await ctx.reply(f"親愛的員工, 你的雞腿不夠不能抽籤哦! 你只有 {member.token}隻.")
            return False
        MemberUtil.add_token(member.member_id, -1 * self.__RATE)
        await ctx.reply(f"抽籤遊戲花費 {self.__RATE}隻雞腿, 你還剩下 {member.token}隻.")
        return True

def setup(client):
    client.add_cog(Kuji(client))