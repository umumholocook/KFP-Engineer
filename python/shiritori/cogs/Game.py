from discord import Message
from discord.ext import commands, tasks
from datetime import datetime
from cogs.StringUtil import StringUtil

class Game(commands.Cog):

    def __init__(self, client):
        self.bot = client
        self.wordCount = 20
        self.lastString = ""
        self.gameStarted = False
        self.countDownTime = 0
        self.channelId = 0
        self.secondRemained = 5
        self.msg = None
        self.history = []

    # Listen to command
    @commands.Cog.listener('on_message')
    async def special_collect_on_message(self, message:Message):
        ctx = await self.bot.get_context(message)
        if ctx.command == None and ctx.author.id != self.bot.user.id:
            if self.gameStarted:
                self.resetParams()
                await self.parseMessage(message)

    @commands.group(name = 'shiritori', invoke_without_command = True)
    async def shiritori_group(self, ctx:commands.Command, *attr):
        helptext = "```"
        helptext+="!shiritori start <字數上限> - 開始遊戲, 字數上限預設20\n"
        helptext+="!shiritori stop - 停止遊戲\n"
        helptext+="!shiritori history - 顯示上一回的接龍結果"
        helptext+="```"
        await ctx.send(helptext)
        pass

    @shiritori_group.command(name = "history")
    async def show_history(self, ctx:commands.Command, *argv):
        await ctx.send("剛剛大家的接龍結果是: {}".format(StringUtil.toHistoryString(self.history)))

    @shiritori_group.command(name = "stop")
    async def game_stop(self, ctx:commands.Command, *argv):
        await self.stopGame()
    
    @shiritori_group.command(name = "start")
    async def game_start(self, ctx:commands.Command, *argv):
        self.history.clear()
        if len(argv) > 0:
            try:
                arg = int(argv[0])
                self.wordCount = min(arg, self.wordCount)
            except ValueError:
                await ctx.send("字數是數字啦!!!試試2-20之間的數字")
                return
        self.gameStarted = True
        await ctx.send("遊戲開始！字數限制是{}個字. 誰先起個頭?".format(self.wordCount))
        self.channelId = ctx.channel.id
        self.countDownTime = datetime.now()
        await self.clock.start()
    
    async def stopGame(self):
        self.gameStarted = False
        self.clock.stop()
        self.resetParams()
        channel = self.bot.get_channel(self.channelId)
        self.channelId = 0
        await channel.send("遊戲結束！")
        if len(self.history) < 1:
            await channel.send("哭哦, 居然沒有人要玩")

    def resetParams(self):
        self.countDownTime = datetime.now()
        self.msg = None
        self.secondRemained = 5

    async def parseMessage(self, message:Message):
        ctx = await self.bot.get_context(message)
        msg = StringUtil.removeStickers(StringUtil.removeEmoji(message.content))
        self.resetParams()
        if len(msg) < 2:
            await ctx.reply("字數太少啦")
            return
        if len(msg) > self.wordCount:
            await ctx.reply("超過字數上限{}, 請重新輸入".format(self.wordCount))
            return
        if len(self.history) > 0 and not StringUtil.matchTheLastWord(self.history, msg):
            await ctx.reply("哎, 同學, 上一個人說'{}', 麻煩你接'{}'哦".format(self.history[-1], self.history[-1][-1]))
            return
        if msg in self.history:
            await ctx.reply("這個之前有人說過啦你換一個")
            return
        self.history.append(msg)
        if len(self.history) == 1:
            await ctx.send("一開始是 {}, 下一個人請接: {}".format(msg, msg[-1]))
        else:
            await ctx.send("下一個人請接: {}".format(msg[-1]))
        

    @tasks.loop(seconds=1)
    async def clock(self):
        if self.gameStarted:
            sec = (datetime.now() - self.countDownTime).total_seconds()
            if self.channelId == 0:
                return
            channel = self.bot.get_channel(self.channelId)
            if sec > 10:
                await self.stopGame()
            if sec > 5:
                if not self.gameStarted:
                    return
                if not self.msg:
                    self.msg = await channel.send("...{} ".format(self.secondRemained))
                else:
                    await self.msg.edit(content= str(self.msg.content)+"...{} ".format(self.secondRemained))
                self.secondRemained -= 1


def setup(client):
    client.add_cog(Game(client))