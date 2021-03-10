from re import U
from discord.enums import ChannelType
from common.models.Channel import Channel
from common.Util import Util

class ChannelUtil():
    # 設定頻道
    def setChannel(guild_id: int, channel_id:int, channel_type: Util.ChannelType, single_record = False):
        if single_record:
            query = Channel.select().where(Channel.channel_type == channel_type.value, Channel.channel_guild_id == guild_id)
        else:
            query = Channel.select().where(Channel.channel_type == channel_type.value, Channel.channel_guild_id == guild_id, Channel.channel_id == channel_id)
        channel: Channel
        if query.exists():
            channel = query.get()
        else:    
            # channel 不存在, 新增一個
            channel = Channel(channel_type=channel_type.value, channel_guild_id=guild_id, channel_id = channel_id)
        channel.channel_id = channel_id
        channel.save()

    # 確定頻道存在
    def hasChannel(guild_id: int, channel_id:int, channel_type: Util.ChannelType):
        query = Channel.select().where(Channel.channel_type == channel_type.value, Channel.channel_guild_id == guild_id, Channel.channel_id == channel_id)
        return query.exists()
    
    # 新增頻道
    def addChannel(guild_id: int, channel_id:int, channel_type: Util.ChannelType):
        ChannelUtil.setChannel(guild_id, channel_id, channel_type, False)
    
    # 移除頻道
    def removeChannel(guild_id: int, channel_id:int, channel_type: Util.ChannelType):
        query = Channel.select().where(Channel.channel_guild_id == guild_id, Channel.channel_id == channel_id, Channel.channel_type == channel_type.value)
        if query.exists():
            channel: Channel = query.get()
            channel.delete_instance()

    # 取得頻道
    def GetChannelWithGuild(guild_id: int, channel_type: Util.ChannelType):
        result = []
        query = Channel.select().where(Channel.channel_guild_id == guild_id, Channel.channel_type == channel_type.value)
        if query.exists():
            channel: Channel
            for channel in query.iterator():
                result.append(channel)
        return result

    # 取得頻道, 返回 {guild_id: [channel_id, ...], guild_id_2: [channel_id, ...]}
    def __get_channel(type: Util.ChannelType):
        result = {}
        query = Channel.select().where(Channel.channel_type == type.value)
        if query.exists():
            channel: Channel
            for channel in query.iterator():
                channelList = result.get(channel.channel_guild_id, [])
                channelList.append(channel.channel_id) 
                result[channel.channel_guild_id] = channelList
        return result

     # 設定訊息頻道ID
    def setRankupChannel(guild_id:int, channel_id:int):
        ChannelUtil.setChannel(guild_id, channel_id, Util.ChannelType.RANK_UP, True)
    
    # 取得訊息頻道ID
    def getMessageChannelId(guild_id: int):
        channels = ChannelUtil.GetChannelWithGuild(guild_id, Util.ChannelType.RANK_UP)
        if len(channels) < 1:
            return None
        return channels[0].channel_id

    # 獲得不需要增加經驗的頻道
    def getXPIgnoredChannels():
        return ChannelUtil.__get_channel(Util.ChannelType.IGNORE_XP)

    # 獲得自動刪除會員發言的頻道
    def getAutoClearChannels():
        return ChannelUtil.__get_channel(Util.ChannelType.AUTO_DELETE)

    # 設定自我更新啟動時使用的頻道ID
    def setRebootMessageChannel(guild_id: int, channel_id:int):
        ChannelUtil.setChannel(guild_id, channel_id, Util.ChannelType.REBOOT_MESSAGE, True)

    # 取得自我更新啟動時使用的頻道ID
    def getRebootMessageChannel(guild_id: int):
        result = ChannelUtil.GetChannelWithGuild(guild_id, Util.ChannelType.REBOOT_MESSAGE)
        if len(result) < 1:
            return None
        return result[0]
    