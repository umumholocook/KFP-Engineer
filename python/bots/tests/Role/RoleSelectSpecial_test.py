import pytest
from unittest import mock
from unittest.mock import MagicMock
from cogs.RoleSelectSpecial import RoleSelectSpecial
from common.TestUtil import TestUtil
from data import SpecialRoleData
from discord.utils import get


class TestRoleSelectSpecial():
    def setup_method(self, method):
        self.fakeMember = TestUtil.createFakeMemberWithId(234)
        self.fakeMember.roles = []
        TestUtil.setTestMember(self.fakeMember)
        self.fakeClient = TestUtil.createFakeClient()
        self.cog = RoleSelectSpecial(client=self.fakeClient, chance=0)

    def teardown_method(self, method):
        pass

    @pytest.mark.asyncio
    async def test_initializeRoles(self):
        await self.cog.initializeRoles(self.fakeClient)
        for en_member in SpecialRoleData.EN_MEMBERS:
            for part in en_member:
                assert get(self.fakeClient.guild.roles, name=part['name'])
    
    @pytest.mark.asyncio
    async def test_giveUserSpecialRoleSuccess(self):
        await self.cog.initializeRoles(self.fakeClient)
        # disable sendMessage
        self.cog.sendMessage = TestUtil.fakeSendMessage
        fakeMessage = TestUtil.createFakeMessage()
        fakeMessage.author = self.fakeMember
        await self.cog.giveUserSpecialRole(self.fakeClient, fakeMessage)
        # check to see if user has a new role
        assert len(self.fakeMember.roles) == 1

    
