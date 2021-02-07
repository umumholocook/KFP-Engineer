import pytest
from peewee import SqliteDatabase
from common.KFP_DB import KfpDb
from common.models.Member import Member

MODELS = [Member]

class TestKfpDb():
    def setup_method(self, method):
        self.guild_id = 123
        self.database = KfpDb(dbFile=":memory:")
        
    def teardown_method(self, method):
        database = self.database.get_database()
        database.drop_tables(MODELS)
        database.close()

    def test_AddMember(self):
        self.database.add_member(12346)
        member = Member.get_by_id(12346)
        assert member.member_id == 12346
        
    def test_addMultipleMembers(self):
        member_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        self.database.add_members(member_ids)
        for member_id in member_ids:
            member = Member.get_by_id(member_id)
            assert member.member_id == member_id
    