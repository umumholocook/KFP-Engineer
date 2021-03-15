import pytest
import peewee
import os
from common.KFP_DB import KfpDb
from common.models.Member import Member


default_user_id = 0

class TestKfpDb():
    def setup_method(self, method):
        self.guild_id = 123
        self.database = KfpDb(dbFile=":memory:")
        self.database.add_member(default_user_id) # add a default member
        
    def teardown_method(self, method):
        self.database.teardown()
        for file in os.listdir():
            if file.endswith("test.db"):
                os.remove(file)

    def test_addMember(self):
        self.database.add_member(12346)
        member = self.database.get_member(12346)
        assert member.member_id == 12346

    def test_dataIntegrity(self):
        self.database = KfpDb(dbFile="tmp_test.db")
        self.database.add_member(12346)
        self.database = KfpDb(dbFile="tmp_test.db")
        member = self.database.get_member(12346)
        assert member.member_id == 12346
    
    def test_getMember_notExist(self):
        assert not self.database.get_member(100) # user 100 does not exist
        
    def test_addMultipleMembers(self):
        member_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        self.database.add_members(member_ids)
        for member_id in member_ids:
            member = Member.get_by_id(member_id)
            assert member.member_id == member_id
    
    def test_memberHasUniqueId(self):
        with pytest.raises(peewee.IntegrityError): 
            self.database.add_member(default_user_id)

    def test_increaseExp_notExist(self):
        assert -1 == self.database.increase_exp(0, 0, 100, 10) # user 100 does not exist

    def test_increaseExp(self):
        self.database.increase_exp(0, 0, default_user_id, 10)
        member = Member.get_by_id(default_user_id)
        assert member.exp == 10

    def test_ignore_increaseExp(self):
        self.database.set_ignore_xp_channel(3, 5)
        self.database.increase_exp(3, 5, default_user_id, 10)
        member = Member.get_by_id(default_user_id)
        assert member.exp == 0

    def test_after_remove_ignore_increaseExp(self):
        self.database.remove_ignore_xp_channel(3, 5)
        self.database.set_ignore_xp_channel(3, 5)
        self.database.remove_ignore_xp_channel(3, 5)
        self.database.increase_exp(3, 5, default_user_id, 10)
        member = Member.get_by_id(default_user_id)
        assert member.exp == 10

    def test_rankUp(self):
        member = Member.get_by_id(default_user_id)
        assert member.rank == 0
        self.database.increase_exp(0, 0, default_user_id, 100)
        member = Member.get_by_id(default_user_id)
        assert member.rank == 1
    
    def test_addCoin_notExist(self):
        assert not self.database.add_coin(100, 10) # user 100 does not exist

    def test_addCoin(self):
        self.database.add_coin(default_user_id, 10)
        member = self.database.get_member(default_user_id)
        assert member.coin == 10

    def test_subtractCoin(self):
        self.database.add_coin(default_user_id, 100)
        self.database.add_coin(default_user_id, -10)
        member = self.database.get_member(default_user_id)
        assert member.coin == 90
    
    def test_notEnoughMoney(self):
        self.database.add_coin(default_user_id, 100)
        assert not self.database.add_coin(default_user_id, -1000)
        member = self.database.get_member(default_user_id)
        assert member.coin == 100
        
    def test_getMemberRankOrder_number1(self):
        # 只有一人的時候那人是第一名
        assert self.database.get_member_rank_order(0) == 1

    def test_getMemberRankOrder_last(self):
        self.database.add_member(1)
        self.database.add_member(2)
        
        self.database.increase_exp(0, 0, 1, 100)
        self.database.increase_exp(0, 0, 2, 100)
        
        assert self.database.get_member_rank_order(0) == 3

    def test_getMemberRankOrder_first(self):
        self.database.add_member(1)
        self.database.add_member(2)
        
        self.database.increase_exp(0, 0, default_user_id, 101)
        self.database.increase_exp(0, 0, 1, 100)
        self.database.increase_exp(0, 0, 2, 100)
        
        assert self.database.get_member_rank_order(default_user_id) == 1

    def test_sameMemberRankOrder_second(self):
        self.database.add_member(1)
        self.database.add_member(2)
        self.database.add_member(3)
        
        self.database.increase_exp(0, 0, default_user_id, 100)
        self.database.increase_exp(0, 0, 1, 100)
        self.database.increase_exp(0, 0, 2, 1000)
        self.database.increase_exp(0, 0, 3, 10)

        # 經驗相同時排名相同, 並列第二
        assert self.database.get_member_rank_order(default_user_id) == 2
        assert self.database.get_member_rank_order(1) == 2
    
    def test_setRankupChannel_notExist(self):
        assert not self.database.get_rankup_channel_id(11)
    
    def test_setRankupChannel(self):
        self.database.set_rankup_channel(11, 123)
        assert self.database.get_rankup_channel_id(11) == 123

        self.database.set_rankup_channel(11, 456)
        assert self.database.get_rankup_channel_id(11) == 456

    def test_resetEveryoneToken(self):
        self.database.add_member(1)
        self.database.add_member(2)
        self.database.add_member(3)

        self.database.reset_everyone_token()

        assert self.database.get_member(1).token == 100
        assert self.database.get_member(2).token == 100
        assert self.database.get_member(3).token == 100
