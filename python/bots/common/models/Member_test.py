import pytest
import json
import common.models.BaseModel as db
from peewee import SqliteDatabase
from common.models.Member import Member

class TestMember():
    def setup_method(self, method):
        self.guild_id = 123
        self.database = SqliteDatabase(":memory:")
        db.proxy.initialize(self.database)
        Member.create_table(guild_id=self.guild_id)
        
    def teardown_method(self, method):
        self.database.drop_tables(Member.get_all_tables())
        self.database.close()

    def test_addMultipleMembers(self):
        member_ids = [1, 2, 3, 4, 5, 6, 7, 8]
        Member.add_members(self.guild_id, member_ids)
        for member_id in member_ids:
            assert Member.get_member_row(self.guild_id, member_id).member_id == member_id