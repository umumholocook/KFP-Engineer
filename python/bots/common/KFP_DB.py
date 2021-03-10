from datetime import datetime, timedelta
import sqlite3

from discord.reaction import Reaction
import common.models.BaseModel as db
from common.Util import Util
from common.models.Member import Member
from common.models.Channel import Channel
from common.models.Ranking import Ranking
from peewee import SqliteDatabase

MODULES = [Member, Channel, Ranking]

class KfpDb():
    def __init__(self, dbFile=r"./common/KFP_bot.db"):
        self.sqliteDb = SqliteDatabase(dbFile)
        db.proxy.initialize(self.sqliteDb)
        self.sqliteDb.create_tables(MODULES)

    # For test only, do not use
    def teardown(self):
        self.sqliteDb.drop_tables(MODULES)
        self.sqliteDb.close()

    # For test only, do not use
    def get_database(self):
        return self.sqliteDb

    def has_member(self, member_id:int):
        return Member.select().where(Member.member_id == member_id).exists()

    # 透過會員ID讀取會員
    def get_member(self, member_id:int):
        if self.has_member(member_id):
            return Member.get_by_id(member_id)
        return None
    
    # 增加新會員
    def add_member(self, member_id:int):
        member = Member.create(member_id=member_id)
        member.save()
    
    #　增加復數會員
    def add_members(self, member_ids):
        data = []
        for member_id in member_ids:
            data.append({'member_id': member_id})
        Member.insert_many(data).execute()

    # 增加會員的經驗值
    def increase_exp(self, member_id:int, new_exp:int):
        query = Member.select().where(Member.member_id == member_id)
        if not query.exists():
            return False
        member = query.get()
        member.exp = member.exp+new_exp
        member.save()
        return self.__update_rank_if_qualified(member_id)
        #return True
    
    # 更新會員的硬幣數量, 數量可以是負數, 如果會員硬幣減至0, 以交易失敗為記
    def update_coin(self, member_id:int, amount:int):
        query = Member.select().where(Member.member_id == member_id)
        if not query.exists():
            return False
        member = query.get()
        newValue = member.coin+amount
        if (newValue < 0):
            return False
        member.coin = newValue
        member.save()
        return True
    
    # 如果需要升級會員等級便升級
    def __update_rank_if_qualified(self, member_id:int):
        member = Member.get_by_id(member_id)
        new_rank = member.rank
        while (member.exp > Util.get_rank_exp(new_rank)):
            new_rank += 1
        if new_rank != member.rank:
            member.rank = new_rank
            member.save()
        return member.rank

    # 會員等級排名
    def get_member_rank_order(self, member_id:int):
        target_exp = Member.get_by_id(member_id).exp
        return Member.select().where((Member.exp > target_exp)).count() + 1
    
    # 設定訊息頻道ID
    def set_rankup_channel(self, channel_id:int):
        query = Channel.select().where(Channel.channel_type == Util.ChannelType.RANK_UP)
        if query.exists():
            channel = query.get()
        else:
            # channel 不存在, 新增一個
            channel = Channel(channel_type=Util.ChannelType.RANK_UP)
        
        channel.channel_discord_id = channel_id
        channel.save()

    # 取得訊息頻道ID
    def get_message_channel_id(self):
        query = Channel.select().where(Channel.channel_type == Util.ChannelType.RANK_UP)
        if query.exists():
            return query.get().channel_discord_id
        return None
        
    def increase_counting_table(self, user_id:int, key:str, guild_id:int, ):
        now = datetime.today()
        nowf = now.replace(hour=0,minute=0, second=0, microsecond=0).timestamp()
        nowe = (datetime.today() + timedelta(days=1)).timestamp()
        query = Ranking.select().where(Ranking.ranking_key == key, Ranking.user_id == user_id, Ranking.timestamp >= nowf and Ranking.timestamp < nowe)
        if not query.exists():
            ranking = Ranking.insert(rankingt_type = Util.RankingType.REACTION,
                ranking_key = key,
                user_id = user_id,
                guild_id = guild_id,
                count = 1, 
                timestamp = now.timestamp()).execute()
        else:
            ranking = query.get()
            ranking.count += 1
            ranking.timestamp = now.timestamp()
            ranking.save()

    def reduce_counting_table(self, user_id:int, key:str, guild_id:int):
        now = datetime.today()
        nowf = now.replace(hour=0,minute=0, second=0, microsecond=0).timestamp()
        nowe = (datetime.today() + timedelta(days=1)).timestamp()
        query = Ranking.select().where(Ranking.ranking_key == key, Ranking.user_id == user_id, Ranking.timestamp >= nowf and Ranking.timestamp < nowe)
        if not query.exists():
            ranking = Ranking.insert(rankingt_type = Util.RankingType.REACTION,
                ranking_key = key,
                user_id = user_id,
                guild_id = guild_id,
                count = -1, 
                timestamp = now.timestamp()).execute()
        else:
            ranking = query.get()
            ranking.count -= 1
            ranking.timestamp = now.timestamp()
            ranking.save()
    
    def get_conting_table(self,guild_id:int, timestamp_from:float, timestamp_end:float):
        assert timestamp_from != timestamp_end
        result = list()
        for query in Ranking.select().where(Ranking.rankingt_type == Util.RankingType.REACTION, Ranking.guild_id == guild_id,Ranking.timestamp >= timestamp_from and Ranking.timestamp <= timestamp_end):
            result.append(query.get())
        if result != []:
            return result
        else:
            None