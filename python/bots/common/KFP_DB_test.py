import pytest
from peewee import SqliteDatabase
from common.KFP_DB import KfpDb
from common.models.Member import Member

class TestKfpDb():
    def setup_method(self, method):
        self.guild_id = 123
        self.database = KfpDb(dbFile=":memory:")
        self.database.create_table(guild_id=self.guild_id)
        
    def teardown_method(self, method):
        database = self.database.get_database()
        database.drop_tables(Member.get_all_tables())
        database.close()

    def test_guildIdDoesNotExist(self):
        with pytest.raises(ValueError):
            self.database.add_member(guild_id=321, member_id=12346)

    def test_AddMember(self):
        self.database.add_member(self.guild_id, 12346)
        member = self.database.get_member_row(self.guild_id, 12346)
        assert member.member_id == 12346

    def test_switchGuild(self):
        Member.create_table(321)
        self.database.add_member(321, 654321)
        member = self.database.get_member_row(321, 654321)
        assert member.member_id == 654321
