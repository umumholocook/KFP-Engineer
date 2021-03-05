from common.models.GamblingBet import GamblingBet
import common.models.BaseModel as db
from common.Util import Util
from common.models.Member import Member
from common.models.Channel import Channel
from common.models.GamblingGame import GamblingGame
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
    def get_active_betting_list(guild_id:int):
        result = []
        query = GamblingGame.select().where(GamblingGame.guild_id == guild_id)
        if query.exists():
            game: GamblingGame
            for game in query.iterator():
                result.append(game)
        return result
    
    # 取得賭盤所有的賭注
    def get_bet(game: GamblingGame):
        query = GamblingBet.select().where(GamblingBet.game_id == game.id)
        if query.exists():
            return query.get()
        return []
    
    def get_gambling_game(gambling_id: int):
        query = GamblingGame.select.where(GamblingGame.id == gambling_id)
        if query.exists():
            return query.get()
        return None

    def update_gambling_game(self, game: GamblingGame, status: Util.GamblingStatus, channel_id:int, message_id: int):
        game.status = status
        game.channel_id = channel_id
        game.message_id = message_id
        game.save()
