import pytest
from unittest import mock
from cogs.NewProfile import NewProfile
from discord import Guild, Member

class TestNewProfile():
    def setup_method(self, method):
        self.fakeClient = mock.patch('cogs.NewProfile.Client')
        self.fakeGuild = mock.patch('cogs.NewProfile.Guild')

        self.fakeClient.start()
        self.fakeGuild.start()
        self.cog = NewProfile(self.fakeClient, ":memory:")
    
    def teardown_method(self, method):
        self.fakeClient.stop()
        self.fakeGuild.stop()
        self.cog.db.teardown()
    
    @pytest.mark.asyncio 
    async def test_guild_join(self):
        self.fakeGuild.members = self.create_list_of_members()
        self.fakeClient.user = self.create_mock_user(0)
        await self.cog.profile_guild_join(self.fakeGuild)
        for x in range(1, 10): # user 0 is bot
            assert self.cog.db.has_member(x)

    def create_mock_user(self, user_id:int):
        member = mock.patch('cogs.NewProfile.Member')
        member.id = user_id
        member.bot = False
        return member
    
    def create_list_of_members(self):
        result = []
        for x in range(0, 10):
            result.append(self.create_mock_user(x))
        return result


