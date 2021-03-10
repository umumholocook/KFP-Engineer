import os, json, sys, asyncio
from discord.ext import commands
from discord import Reaction
from discord.user import User
from datetime import datetime, timedelta
if not os.getcwd() in sys.path:
    sys.path.append(os.getcwd())
from common.KFP_DB import KfpDb

REGISTER_LIST_FILE_PATH = os.sep.join((os.getcwd(), 'resource', 'ReactionRankingRegisterList.json'))

class Ranking(commands.Cog):

    def __init__(self, client, db_file):
        self.client = client
        self.db = KfpDb(db_file)
        self.registerList = self.LoadRegisterList()
        self.DaytimerTask = self.client.loop.create_task(self.ranking_timer_task(self.NextDaySecond))
        self.WeekTimerTask = self.client.loop.create_task(self.ranking_timer_task(self.NextWeekSecond))
        self.MonthTimerTask = self.client.loop.create_task(self.ranking_timer_task(self.NextMonthSecond))
    
    def LoadRegisterList(self) -> dict:
        fp = None
        result = {}
        if os.path.exists(REGISTER_LIST_FILE_PATH):
            fp = open(REGISTER_LIST_FILE_PATH, 'r', encoding='utf-8')
            try:
                result = json.load(fp)
            except:
                fp.close()
                os.remove(REGISTER_LIST_FILE_PATH)
                return self.LoadRegisterList()
        else:
            fp = open(REGISTER_LIST_FILE_PATH, 'w', encoding='utf-8')
            json.dump(result, fp, indent= 2)
        fp.close()
        return result

    def SaveRegisterList(self):
        with open(REGISTER_LIST_FILE_PATH, 'w') as fp:
            json.dump(self.registerList, fp, indent= 2)
            fp.close()

    def RegisterCountingTable(self, ranking_name:str, reaction_id:str) -> None:
        if not self.registerList.get(ranking_name, False):
            self.registerList[ranking_name] = []
        self.registerList[ranking_name].append(str(reaction_id))
        self.SaveRegisterList()
    
    def NextDaySecond(self):
        nowZero = datetime.today().replace(hour= 0, minute= 0,second= 0, microsecond= 0)
        nextDay = nowZero + timedelta(days=1)
        return nextDay.timestamp() - datetime.today().timestamp()
    
    def NextWeekSecond(self):
        nowZero = datetime.today().replace(hour= 0, minute= 0,second= 0, microsecond= 0)
        temp = timedelta(days= 7) if nowZero.weekday() == 7 else timedelta(days=(7 - nowZero.weekday()))
        nextWeek = nowZero + temp
        return nextWeek.timestamp() - datetime.today().timestamp()

    def NextMonthSecond(self):
        nowZero = datetime.today().replace(hour= 0, minute= 0,second= 0, microsecond= 0)
        nextMonth = datetime(nowZero.year,nowZero.month+1,1, 0,0,1,0) if nowZero.month != 12 else datetime(nowZero.year+1, 1, 1, 0, 0, 1, 0)
        return nextMonth.timestamp() - datetime.today().timestamp()
        
    async def ranking_timer_task(self, fnCorrection):
        while not self.client.is_closed():
            s = fnCorrection()
            await asyncio.sleep(s)
            try:
                await self.ranking_announcement(s, datetime.today().timestamp())
            except:
                pass #也許需要對應的log 系統

    async def ranking_announcement(self, timedeltaSecond:int, timeNow:int):
        #TODO: send annuncment
        
        pass

    @commands.Cog.listener('on_ready')
    async def ranking_on_ready(self):
        await self.DaytimerTask
        await self.WeekTimerTask
        await self.MonthTimerTask

    @commands.Cog.listener('on_reaction_add')
    async def ranking_on_reaction_add(self, rct : Reaction, user : User) -> None:
        #and rct.message.author != user
        for rankingName in self.registerList:
            if str(rct.emoji.id) in self.registerList[rankingName]:
                self.db.increase_counting_table(rct.message.author.id, rankingName, user.guild.id)
        pass

    @commands.Cog.listener('on_reaction_remove')
    async def ranking_on_reaction_remove(self, rct : Reaction, user : User) -> None:
        #if rct.message.author != user:
        for rankingName in self.registerList:
            if str(rct.emoji.id) in self.registerList[rankingName]:
                self.db.reduce_counting_table(rct.message.author.id, rankingName, user.guild.id)
    
    @commands.group(name= 'ranking', invoke_without_command = True)
    async def Ranking_ranking_group(self, ctx, *arg):
        sendMsg='ranking regist 排行榜名稱 紀錄的貼圖1 [紀錄的貼圖2]...\nranking list :列出目前排行榜'
        await ctx.send(sendMsg)

    @Ranking_ranking_group.command(name = 'regist')
    async def Ranking_register_command(self, ctx:commands.Context, rankingName:str, *reactions):
        for reaction in reactions:
            i = reaction.find(':', 2)
            if reaction.startswith('<') and reaction.endswith('>') and i > 0:
                reaction_id = reaction[i+1: -1]
            else:
                await ctx.send('參數錯誤: {}', reaction)
                return

            if not str(rankingName) in self.registerList.keys():
                self.RegisterCountingTable(rankingName, reaction_id)
                await ctx.send('註冊 {} 至排名 {}列表。'.format(reaction, rankingName))
            else:
                if not str(reaction_id) in self.registerList[rankingName]:
                    self.RegisterCountingTable(rankingName, reaction_id)
                    await ctx.send('註冊 {} 至排名 {}列表。'.format(reaction, rankingName))
                else:
                    await ctx.send('{} 已經註冊過了，換個名字吧!'.format(rankingName))
    
    @Ranking_ranking_group.command(name= 'list')
    async def Ranking_list_command(self, ctx):
        sendMsg = ''
        for rankingName in self.registerList:
            sendMsg += rankingName + ':\n　　'
            for reactionId in self.registerList[rankingName]:
                tEmoji = self.client.get_emoji(int(reactionId))
                sendMsg += '<:' + tEmoji.name + ':' + str(reactionId) + '>　'
            sendMsg += '\n'
        await ctx.send(sendMsg)
    
    @Ranking_ranking_group.command(name= 'remove')
    async def Ranking_remove_command(self, ctx, rankingName):
        if not self.registerList.get(rankingName, False) == False:
            self.registerList.pop(rankingName)
            await ctx.send('刪除 {}。'.format(rankingName))
        else:
            await ctx.send('沒有名字為 {} 的排行表'.format(rankingName))


def setup(client, ):
    client.add_cog(Ranking(client, r"./common/KFP_bot.db"))
    