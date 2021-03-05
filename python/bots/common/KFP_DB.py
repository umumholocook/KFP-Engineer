import datetime
import common.models.BaseModel as db
from common.models.PermissionRole import PermissionRole
from common.models.GamblingBet import GamblingBet
from common.Util import Util
from common.models.Member import Member
from common.models.Channel import Channel
from common.models.GamblingGame import GamblingGame
from discord.guild import Guild, Role
from discord.ext import commands
from peewee import SqliteDatabase

MODULES = [Member, Channel]

class KfpDb():
    # {guild:[channel, channel,...] ... }
    __ignoreXpChannel = {}

    def __init__(self, dbFile=r"./common/KFP_bot.db"):
        self.sqliteDb = SqliteDatabase(dbFile)
        db.proxy.initialize(self.sqliteDb)
        self.sqliteDb.create_tables(MODULES)
        self.__ignoreXpChannel = self.__getXPIgnoredChannels()

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
    
    # 獲得不需要增加經驗的頻道
    def __getXPIgnoredChannels(self):
        result = {}
        query = Channel.select().where(Channel.channel_type == Util.ChannelType.IGNORE_XP)
        if query.exists():
            channel: Channel
            for channel in query.iterator():
                channelList = result.get(channel.channel_guild_id, [])
                channelList.append(channel.channel_id) 
                result[channel.channel_guild_id] = channelList
        return result
    
    def set_ignore_xp_channel(self, guild_id: int, channel_id: int):
        channel = Channel.create(channel_type=Util.ChannelType.IGNORE_XP, channel_guild_id=guild_id, channel_id=channel_id)
        channel.save()
        self.__ignoreXpChannel = self.__getXPIgnoredChannels()

    def remove_ignore_xp_channel(self, guild_id: int, channel_id: int):
        Channel.delete().where(Channel.channel_type == Util.ChannelType.IGNORE_XP, Channel.channel_guild_id == guild_id, Channel.channel_id == channel_id).execute()
        self.__ignoreXpChannel = self.__getXPIgnoredChannels()
    
    # 更新會員的硬幣數量, 數量可以是負數, 如果會員硬幣減至0, 以交易失敗為記
    def update_coin(self, member_id:int, amount:int):
        query = Member.select().where(Member.member_id == member_id)
        if not query.exists():
            return False
        member = query.get()
        return self.update_coin(member, amount)
    
    def update_coin(self, member: Member, amount: int) -> bool :
        newValue = member.coin+amount
        if (newValue < 0):
            return False
        member.coin = newValue
        member.save()
        return True
    
    def update_token(self, member_id:int, amount:int):
        query = Member.select().where(Member.member_id == member_id)
        if not query.exists():
            return False
        member = query.get()
        member.token = amount
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
    def set_rankup_channel(self, guild_id:int, channel_id:int):
        query = Channel.select().where(Channel.channel_type == Util.ChannelType.RANK_UP)
        if query.exists():
            channel = query.get()
        else:
            # channel 不存在, 新增一個
            channel = Channel(channel_type=Util.ChannelType.RANK_UP)
        channel.channel_guild_id = guild_id
        channel.channel_id = channel_id
        channel.save()

    # 取得訊息頻道ID
    def get_message_channel_id(self):
        query = Channel.select().where(Channel.channel_type == Util.ChannelType.RANK_UP)
        if query.exists():
            return query.get().channel_id
        return None

    def has_channel(self, guild_id: int, channel_id: int, channel_type: Util.ChannelType) -> bool:
        query = Channel.select().where(Channel.channel_type == type, Channel.channel_guild_id == guild_id, Channel.channel_id == channel_id)
        return query.exists()
    
    # 儲存一個新的頻道, 如果評道已經存在, 返回false, 反之返回true
    def add_channel(self, guild_id: int, channel_id: int, channel_type: Util.ChannelType) -> bool:
        query = Channel.select().where(Channel.channel_type == channel_type, Channel.channel_guild_id == guild_id, Channel.channel_id == channel_id)
        if query.exists():
            return False

        new_channel = Channel(channel_guild_id = guild_id, channel_id = channel_id, channel_type = channel_type)
        new_channel.save()
        return True
    
    # 設定自我更新啟動時使用的頻道ID
    def set_reboot_message_channel(self, channel_id:int):
        query = Channel.select().where(Channel.channel_type == Util.ChannelType.REBOOT_MESSAGE)
        if query.exists():
            channel = query.get()
        else:
            channel = Channel(channel_type=Util.ChannelType.REBOOT_MESSAGE)
        channel.channel_id = channel_id
        channel.save()
    
    # 取得自我更新啟動時使用的頻道ID
    def get_reboot_message_channel(self):
        query = Channel.select().where(Channel.channel_type == Util.ChannelType.REBOOT_MESSAGE)
        if query.exists():
            return query.get().channel_id
        return None
    
    # 取得現在這個群所有的賭盤
    def get_active_betting_list(self, guild_id:int):
        result = []
        query = GamblingGame.select().where(GamblingGame.guild_id == guild_id)
        if query.exists():
            game: GamblingGame
            for game in query.iterator():
                result.append(game)
        return result
    
    # 取得現在這個頻道所有的賭盤
    def get_active_betting_list_in_channel(self, guild_id: int, channel_id: int):
        result = []
        query = GamblingGame.select().where(GamblingGame.guild_id == guild_id, GamblingGame.channel_id == channel_id)
        if query.exists():
            game: GamblingGame
            for game in query.iterator():
                result.append(game)
        return result
    
    # 取得賭盤所有的賭注
    def get_bet(self, game: GamblingGame):
        query = GamblingBet.select().where(GamblingBet.game_id == game.id)
        if query.exists():
            return query.get()
        return []
    
    # 增加賭池
    def add_game_pool_amount(self, game:GamblingGame, amount: int):
        game.pool += amount
        game.save()
    
    def get_gambling_game(gambling_id: int):
        query = GamblingGame.select().where(GamblingGame.id == gambling_id)
        if query.exists():
            return query.get()
        return None

    def update_gambling_game(self, game: GamblingGame, status: Util.GamblingStatus, channel_id:int, message_id: int):
        game.status = status
        game.channel_id = channel_id
        game.message_id = message_id
        game.save()
    
    # 新增賭注
    def add_bet(self, game: GamblingGame, user_id: int, amount: int, item_index: int, timestamp=datetime.datetime.now):
        # 檢查有沒有現存的賭注
        query = GamblingBet.select().where(GamblingBet.member_id == user_id, GamblingBet.game_id == game.id, GamblingBet.item_index == item_index)
        bet: GamblingBet
        if query.exists():
            # 找到現存的賭注　更新此賭注
            bet = query.get()
            bet.charge += amount
        else:
            # 沒有找到賭注的紀錄　新建一個新的
            bet = GamblingBet(member_id = user_id, game_id = game.id, item_index = item_index, charge = amount, create = timestamp)
        bet.save()

    # 獲得管理身分組列表
    def load_permissions(self, role_type: Util.RoleType):
        result = []
        query = PermissionRole.select().where(PermissionRole.role_type == role_type)
        if query.exists():
            role: PermissionRole
            for role in query.iterator():
                result.append(role) 
        return result
    
    # 更新管理身分組的id, 通常是在bot被踢出又加入之後才會用到
    def update_permission_role(self, old_id: int, new_id: int, guild_id: int, role_type: Util.RoleType):
        query = PermissionRole.select().where(PermissionRole.role_type == role_type, PermissionRole.role_id == old_id)
        if query.exists():
            role = query.get()
        else:
            role = PermissionRole(role_type = role_type, guild_id = guild_id)
        role.role_id = new_id
        role.save()
    
    def add_permission_role(self, guild: Guild, new_role: Role, role_type: Util.RoleType):
        role = PermissionRole(role_type = role_type, guild_id = guild.id, role_id = new_role.id)
        role.save()
        return role
    
    def has_permission(self, guild_id: int, role_id: int, type: Util.Roletype) -> bool:
        query = PermissionRole.select().where(PermissionRole.role_type == type, PermissionRole.guild_id == ctx.guild.id, PermissionRole.role_id == role_id)
        return query.exists()
    
