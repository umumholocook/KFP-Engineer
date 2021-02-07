import sqlite3
import common.models.BaseModel as db
from common.Util import Util
from common.models.Member import Member
from common.models.Channel import Channel
from peewee import SqliteDatabase

class KfpDb():

    def __init__(self, dbFile="./common/KFP_bot.db"):
        self.sqliteDb = SqliteDatabase(dbFile)
        db.proxy.initialize(self.sqliteDb)
        self.sqliteDb.create_tables([Member, Channel])

    # For test only, do not use
    def get_database(self):
        return self.sqliteDb

    # 透過會員ID讀取會員
    def get_member(self, member_id:int):
        return Member.get_by_id(member_id)
    
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
        member = Member.get_by_id(member_id)
        member.exp = member.exp+new_exp
        member.save()
        self.__update_rank_if_qualified(member_id)
    
    # 更新會員的硬幣數量, 數量可以是負數, 如果會員硬幣減至0, 以交易失敗為記
    def update_coin(self, member_id:int, amount:int):
        member = Member.get_by_id(member_id)
        newValue = member.coin+amount
        if (newValue < 0):
            return False
        member.coin = newValue
        member.save()
        return True
    
    # 如果需要升級會員等級便升級
    def __update_rank_if_qualified(self, member_id:int):
        member = Member.get_by_id(member_id)
        new_rank = member.rank + 1
        while (member.exp > Util.get_rank_exp(new_rank)):
            new_rank += 1
        if new_rank != member.rank:
            member.rank = new_rank
            member.save()

    # 會員等級排名
    def get_member_rank_order(self, member_id:int):
        target_exp = Member.get_by_id(member_id).exp
        return Member.select().where((Member.exp > target_exp)).count() + 1
    
    # 設定訊息頻道ID
    def set_rankup_channel(self, channel_id:int):
        query = Channel.select().where(Channel.channel_type == Util.ChannelType.RANK_UP)
        if query.exists():
            channel = Channel.get(channel_type=Util.ChannelType.RANK_UP)
        else:
            # channel 不存在
            channel = Channel(channel_type=Util.ChannelType.RANK_UP)
        
        channel.channel_discord_id = channel_id
        channel.save()

        
