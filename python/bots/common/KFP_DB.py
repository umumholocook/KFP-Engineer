from common.ChannelUtil import ChannelUtil
import datetime

import common.models.BaseModel as db
from common.models.PermissionRole import PermissionRole
from common.models.GamblingBet import GamblingBet
from common.Util import Util
from common.models.Channel import Channel
from common.models.GamblingBet import GamblingBet
from common.models.GamblingGame import GamblingGame
from common.models.KfpRole import KfpRole
from common.models.PermissionRole import PermissionRole
from common.models.Member import Member
from common.models.KujiRecord import KujiRecord
from common.database.KfpMigrator import KfpMigrator

from discord.guild import Guild, Role
from peewee import SqliteDatabase

MODULES = [Channel, GamblingBet, GamblingGame, KfpRole, KujiRecord, Member, PermissionRole]

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
    
    # 增加會員的硬幣
    def increase_coin(self, guild_id: int, member_id: int, coin: int):
        query = Member.select().where(Member.member_id == member_id)
        if not query.exists():
            return
        member: Member = query.get()
        member.coin += coin
        member.save()    

    # 增加會員的經驗值, -1 代表找不到會員
    def increase_exp(self, guild_id:int, channel_id:int, member_id:int, new_exp:int):
        if channel_id in self.__ignoreXpChannel.get(guild_id, []):
            return
        query = Member.select().where(Member.member_id == member_id)
        if not query.exists():
            return -1
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

    # 獲得前n名的會員, n = max_limit
    def get_leader_board(self, max_limit: int):
        query = Member.select().order_by(Member.exp.desc()).limit(max_limit)
        result = []
        if query.exists():
            for member in query.iterator():
                result.append(member)
        return result
    
    # 設定訊息頻道ID
    def set_rankup_channel(self, guild_id: int, channel_id:int):
        query = Channel.select().where(Channel.channel_type == Util.ChannelType.RANK_UP, Channel.channel_guild_id == guild_id)
        channel: Channel
        if query.exists():
            channel = query.get()
        else:
            # channel 不存在, 新增一個
            channel = Channel(channel_type=Util.ChannelType.RANK_UP, channel_guild_id=guild_id, channel_id = channel_id)
        channel.channel_id = channel_id
        channel.save()

    # 取得訊息頻道ID
    def get_rankup_channel_id(self, guild_id: int):
        query = Channel.select().where(Channel.channel_type == Util.ChannelType.RANK_UP, Channel.channel_guild_id == guild_id)
        if query.exists():
            channel: Channel = query.get()
            return channel.channel_id
        return None

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
    def load_permissions(self, role_type: Util.ManagementType):
        result = []
        query = PermissionRole.select().where(PermissionRole.role_type == role_type)
        if query.exists():
            role: PermissionRole
            for role in query.iterator():
                result.append(role) 
        return result
    
    # 更新管理身分組的id, 通常是在bot被踢出又加入之後才會用到
    def update_permission_role(self, old_id: int, new_id: int, guild_id: int, role_type: Util.ManagementType):
        query = PermissionRole.select().where(PermissionRole.role_type == role_type, PermissionRole.role_id == old_id)
        if query.exists():
            role = query.get()
        else:
            role = PermissionRole(role_type = role_type, guild_id = guild_id)
        role.role_id = new_id
        role.save()

    # 重置所有人的🍗
    def reset_everyone_token(self):
        member_id_list = Member.select(Member.member_id)
        for member_id in member_id_list:
            Member.update(token=100).where(Member.member_id == member_id).execute()
    
    def add_permission_role(self, guild: Guild, new_role: Role, role_type: Util.ManagementType):
        role = PermissionRole(role_type = role_type, guild_id = guild.id, role_id = new_role.id)
        role.save()
        return role
    
    def has_permission(self, guild_id: int, role_id: int, type: Util.ManagementType) -> bool:
        query = PermissionRole.select().where(PermissionRole.role_type == type, PermissionRole.guild_id == guild_id, PermissionRole.role_id == role_id)
        return query.exists()
    
