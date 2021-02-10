from unittest import mock
from unittest.mock import MagicMock
from discord import Client, TextChannel, Guild, Message, Member
from discord.ext.commands import Context
from random import randint

# 測試用
class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

class TestUtil():
    __fakeGuild = None
    __testMember = None
    __fakeRoles = []

    @mock.patch('common.TestUtil.Client', autospec=True)
    def createFakeClient(mock_client):
        mock_client.channel = TestUtil.createFakeChannel()
        mock_client.guild = TestUtil.createFakeGuild()
        mock_client.get_context = TestUtil.__createFakeContext
        return mock_client

    @mock.patch('common.TestUtil.Message', autospec=True)
    def createFakeMessage(mock_message):
        mock_message.guild = TestUtil.createFakeGuild()
        return mock_message
    
    @mock.patch('common.TestUtil.Guild', autospec=True)
    def createFakeGuild(mock_guild):
        if not TestUtil.__fakeGuild:
            TestUtil.__fakeGuild = mock_guild
            TestUtil.__fakeGuild.create_role = TestUtil.__createFakeRole
            TestUtil.__fakeGuild.get_member = TestUtil.__getMember
            TestUtil.__fakeGuild.roles = TestUtil.__fakeRoles
        return TestUtil.__fakeGuild

    @mock.patch('common.TestUtil.TextChannel', autospec=True)
    def createFakeChannel(mock_channel):
        return mock_channel
    
    @mock.patch('common.TestUtil.Member', autospec=True)
    def createFakeMember(mock_member):
        mock_member.add_roles = TestUtil.__addRoles
        return mock_member
        
    
    @mock.patch('common.TestUtil.Context', autospec=True)
    def createFakeContext(mock_context):
        return mock_context

    def __createFakeContext(message:Message):
        return TestUtil.createFakeContext()

    def createFakeMemberWithId(member_id):
        member = TestUtil.createFakeMember()
        member.id = member_id
        return member
    
    def setTestMember(member:Member):
        TestUtil.__testMember = member

    def __getMember(member_id):
        return TestUtil.__testMember

    async def __addRoles(role):
        TestUtil.__testMember.roles.append(role)

    async def __createFakeRole(**attrs):
        fakeRole = MagicMock()
        fakeRole.name = attrs['name']
        fakeRole.id = randint(1, 99)
        TestUtil.__fakeRoles.append(fakeRole)
        return fakeRole
    
    def getRoles():
        return TestUtil.__fakeRoles

    async def fakeSendMessage(message:Message, msg:str): 
        pass

