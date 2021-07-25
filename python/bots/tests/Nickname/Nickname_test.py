from common.NicknameUtil import NicknameUtil
from common.KFP_DB import KfpDb

class TestNicknameUtil():
    def setup_method(self, method):
        self.database = KfpDb(":memory:")

    def teardown_method(self, method):
        self.database.teardown()
    
    def test_getNickname_empty(self):
        nicknames = NicknameUtil.get_all_nicknames(1, 2)
        assert len(nicknames) == 0
    
    def test_setNickname_success(self):
        NicknameUtil.set_nickname(guild_id=1, user_id=1, nickname="hello")
        nicknames = NicknameUtil.get_all_nicknames(
            guild_id=1,
            user_id=1
        )
        assert nicknames == ["hello"]
    
    def test_setNicknames_success(self):
        NicknameUtil.set_nickname(guild_id=1, user_id=1, nickname="hello")
        NicknameUtil.set_nickname(guild_id=1, user_id=1, nickname="world")
        nicknames = NicknameUtil.get_all_nicknames(
            guild_id=1,
            user_id=1
        )
        assert nicknames == ["hello", "world"]
    
    def test_setNicknames_clear(self):
        NicknameUtil.set_nickname(guild_id=1, user_id=1, nickname="hello")
        NicknameUtil.set_nickname(guild_id=1, user_id=1, nickname="world")
        NicknameUtil.clear_nickname(guild_id=1, user_id=1)
        nicknames = NicknameUtil.get_all_nicknames(
            guild_id=1,
            user_id=1
        )
        assert len(nicknames) == 0
        