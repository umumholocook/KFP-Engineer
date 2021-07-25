from common.models.Channel import Channel
from common.ChannelUtil import ChannelUtil
from common.KFP_DB import KfpDb
from common.Util import Util

class TestChannelUtil():
    def setup_method(self, method):
        self.database = KfpDb(dbFile=":memory:")

    def teardown_method(self, method):
        self.database.teardown()

    def test_setChannel(self):
        ChannelUtil.setChannel(123, 321, Util.ChannelType.RANK_UP)
        result: Channel = ChannelUtil.GetChannelWithGuild(123, Util.ChannelType.RANK_UP)[0]
        assert result.channel_id == 321
        assert result.channel_guild_id == 123
        assert result.channel_type == Util.ChannelType.RANK_UP.value
    
    def test_setRankupChannel(self):
        ChannelUtil.setRankupChannel(0, 123)
        assert ChannelUtil.getMessageChannelId(0) == 123

        ChannelUtil.setRankupChannel(0, 456)
        assert ChannelUtil.getMessageChannelId(0) == 456

    def test_setRankupChannel_notExist(self):
        assert not ChannelUtil.getMessageChannelId(123)
        


