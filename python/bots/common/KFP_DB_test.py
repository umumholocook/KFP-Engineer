import pytest
import peewee
from peewee import SqliteDatabase
from common.KFP_DB import KfpDb
from common.models.Member import Member

MODELS = [Member]
default_user_id = 0

class TestKfpDb():
    def setup_method(self, method):
        self.guild_id = 123
        self.database = KfpDb(dbFile=":memory:")
        self.database.add_member(default_user_id) # add a default member
        
    def teardown_method(self, method):
        database = self.database.get_database()
        database.drop_tables(MODELS)
        database.close()

    def test_addMember(self):
        self.database.add_member(12346)
        member = self.database.get_member(12346)
        assert member.member_id == 12346
        
    def test_addMultipleMembers(self):
        member_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        self.database.add_members(member_ids)
        for member_id in member_ids:
            member = Member.get_by_id(member_id)
            assert member.member_id == member_id
    
    def test_memberHasUniqueId(self):
        with pytest.raises(peewee.IntegrityError): 
            self.database.add_member(default_user_id)

    def test_increaseXp(self):
        self.database.increase_xp(default_user_id, 10)
        member = Member.get_by_id(default_user_id)
        assert member.xp == 10

    def test_rankUp(self):
        member = Member.get_by_id(default_user_id)
        assert member.rank == 0
        self.database.increase_xp(default_user_id, 100)
        member = Member.get_by_id(default_user_id)
        assert member.rank == 1

    def test_addCoin(self):
        self.database.update_coin(default_user_id, 10)
        member = self.database.get_member(default_user_id)
        assert member.coin == 10

    def test_subtractCoin(self):
        self.database.update_coin(default_user_id, 100)
        self.database.update_coin(default_user_id, -10)
        member = self.database.get_member(default_user_id)
        assert member.coin == 90
    
    def test_notEnoughMoney(self):
        self.database.update_coin(default_user_id, 100)
        assert not self.database.update_coin(default_user_id, -1000)
        member = self.database.get_member(default_user_id)
        assert member.coin == 100
        

