from datetime import datetime, timedelta
import sqlite3
from common.ChannelUtil import ChannelUtil
from discord.reaction import Reaction
import common.models.BaseModel as db
from common.models.PermissionRole import PermissionRole
from common.models.GamblingBet import GamblingBet
from common.Util import Util
from common.models.Channel import Channel
from common.models.GamblingBet import GamblingBet
from common.models.GamblingGame import GamblingGame
from common.models.PermissionRole import PermissionRole
from common.models.Member import Member
from common.database.KfpMigrator import KfpMigrator

from discord.guild import Guild, Role
from common.models.Ranking import Ranking
from peewee import SqliteDatabase

MODULES = [Channel, GamblingBet, GamblingGame, Member, PermissionRole, Ranking]

class KfpDb():
    # {guild:[channel, channel,...] ... }
    __ignoreXpChannel = {}
    __autoClearChannel = {}

    def __init__(self, dbFile=r"./common/KFP_bot.db"):
        self.sqliteDb = SqliteDatabase(dbFile)
        KfpMigrator.KfpMigrate(self.sqliteDb)
        db.proxy.initialize(self.sqliteDb)
        self.sqliteDb.create_tables(MODULES)
        self.__ignoreXpChannel = ChannelUtil.getXPIgnoredChannels()
        self.__autoClearChannel = ChannelUtil.getAutoClearChannels()

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
    def get_member(self, member_id:int) -> Member:
        if self.has_member(member_id):
            return Member.get_by_id(member_id)
        return None
    
    # 增加新會員
    def add_member(self, member_id:int) -> Member:
        member = Member.create(member_id=member_id)
        member.save()
        return member
    
    #　增加復數會員
    def add_members(self, member_ids):
        data = []
        for member_id in member_ids:
            data.append({'member_id': member_id})
        Member.insert_many(data).execute()

    # 增加會員的經驗值
    def increase_exp(self, guild_id:int, channel_id:int, member_id:int, new_exp:int):
        if channel_id in self.__ignoreXpChannel.get(guild_id, []):
            return 
        query = Member.select().where(Member.member_id == member_id)
        if not query.exists():
            return False
        member = query.get()
        member.exp = member.exp+new_exp
        member.save()
        return self.__update_rank_if_qualified(member_id)
    
    # 更新會員的硬幣數量, 數量可以是負數, 如果會員硬幣減至0, 以交易失敗為記
    def add_coin(self, member_id:int, amount:int):
        query = Member.select().where(Member.member_id == member_id)
        if not query.exists():
            return False
        member = query.get()
        return self.update_member_coin(member, amount)
    
    def update_member_coin(self, member: Member, amount: int) -> bool :
        newValue = member.coin + amount
        if (newValue < 0):
            return False
        member.coin = newValue
        member.save()
        return True
    
    def add_token(self, member_id:int, amount:int):
        query = Member.select().where(Member.member_id == member_id)
        if query.exists():
            member = query.get()
        else:
            member = self.add_member(member_id)
        member.token += amount
        member.save()
    
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
    
    # 設定不需要增加經驗的頻道
    def set_ignore_xp_channel(self, guild_id: int, channel_id: int):
        ChannelUtil.setChannel(guild_id, channel_id, Util.ChannelType.IGNORE_XP, True)
        self.__ignoreXpChannel = ChannelUtil.getXPIgnoredChannels()

    # 取消不需要增加經驗的頻道
    def remove_ignore_xp_channel(self, guild_id: int, channel_id: int):
        ChannelUtil.removeChannel(guild_id, channel_id, Util.ChannelType.IGNORE_XP)
        self.__ignoreXpChannel = ChannelUtil.getXPIgnoredChannels()

    # 檢查此頻道是不是刪除用戶發言的頻道
    def is_channel_auto_clear(self, guild_id: int, channel_id: int) -> bool:
        return channel_id in self.__autoClearChannel.get(guild_id, [])

    # 獲得所有自動刪除頻道
    def get_auto_clear_channels(self, guild_id: int):
        return self.__autoClearChannel.get(guild_id, [])

    # 獲得管理身分組列表
    def load_permissions(self, role_type: Util.RoleType):
        result = []
        query = PermissionRole.select().where(PermissionRole.role_type == role_type)
        if query.exists():
            role: PermissionRole
            for role in query.iterator():
                result.append(role) 
        return result
        
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
            
    def counting_table_clean(self):
        Ranking.update({Ranking.count:0}).execute()
    
    # 更新管理身分組的id, 通常是在bot被踢出又加入之後才會用到
    def update_permission_role(self, old_id: int, new_id: int, guild_id: int, role_type: Util.RoleType):
        query = PermissionRole.select().where(PermissionRole.role_type == role_type, PermissionRole.role_id == old_id)
        if query.exists():
            role = query.get()
        else:
            role = PermissionRole(role_type = role_type, guild_id = guild_id)
        role.role_id = new_id
        role.save()

    # 重置所有人的🍗
    def reset_everyone_token(self):
        Member.update({Member.token:100})
    
    def add_permission_role(self, guild: Guild, new_role: Role, role_type: Util.RoleType):
        role = PermissionRole(role_type = role_type, guild_id = guild.id, role_id = new_role.id)
        role.save()
        return role
    
    def has_permission(self, guild_id: int, role_id: int, type: Util.RoleType) -> bool:
        query = PermissionRole.select().where(PermissionRole.role_type == type, PermissionRole.guild_id == guild_id, PermissionRole.role_id == role_id)
        return query.exists()
    
