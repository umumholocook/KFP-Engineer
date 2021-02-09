import pytest
from asyncio import Future
from unittest import mock
from unittest.mock import MagicMock
from random import randint
from cogs.RoleSelectSpecial import RoleSelectSpecial
from discord import Client, TextChannel, Permissions, Color, Role
from data import SpecialRoleData

class TestRoleSelectSpecial():
    def setup_method(self, method):
        self.fakeClient = self.createFakeClient()
        self.cog = RoleSelectSpecial(self.fakeClient)

    def teardown_method(self, method):
        pass

    @pytest.mark.asyncio
    async def test_initializeRoles(self):
        await self.cog.initializeRoles(self.fakeClient)
        for en_member in SpecialRoleData.EN_MEMBERS:
            for part in en_member:
                assert self.cog.roleMap[part['name']]

    @mock.patch('cogs.RoleSelectSpecial_test.Client', autospec=True)
    def createFakeClient(self, mock_client):
        mock_client.channel = self.createFakeChannel()
        mock_client.guild = self.createFakeGuild()
        return mock_client

    @mock.patch('cogs.RoleSelectSpecial.Message', autospec=True)
    def createFakeMessage(self, mock_message):
        return mock_message
    
    @mock.patch('cogs.RoleSelectSpecial.Guild', autospec=True)
    def createFakeGuild(self, mock_guild):
        mock_guild.create_role = TestRoleSelectSpecial.createFakeRole
        return mock_guild

    @mock.patch('cogs.RoleSelectSpecial_test.TextChannel', autospec=True)
    def createFakeChannel(self, mock_channel):
        return mock_channel

    async def createFakeRole(name, permissions, colour, mentionable, hoist):
        fakeRole = MagicMock()
        fakeRole.name = name
        fakeRole.id = randint(1, 99)
        return fakeRole
        
