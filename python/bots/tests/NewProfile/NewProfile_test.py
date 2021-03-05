import pytest
from unittest import mock
#if con not find cogs non-commont fowing code
#if not os.getcwd() in sys.path:
#    sys.path.append(os.getcwd())
from cogs import NewProfile

class FakeUser():
    def __init__(self, user_id, user_name, bot= False) -> None:
        self.id = user_id
        self.name = user_name
        self.bot= bot
        self.dispaly_name = user_name

@mock.patch('NewProfile.discord.Asset', autospec= True)
class FakeAsset(object):
    def __init__(self, data) -> None:
        super(FakeAsset, self).__init__()
        self._data = data

    async def read(self):
        return self._data
    
    def __getattribute__(self, name: str):
        if name == '_url':
            return 'fake url'
        return object.__getattribute__(self, name)

@mock.patch("NewProfile.Member", autospec= True)
class FakeMember(FakeUser):
    def __init__(self, member_id, member_name, guild, nick_name, ) -> None:
        super().__init__(member_id, member_name)
        self.guild = guild
        self.nick_name = nick_name
        self.display_name = nick_name
        self._icon_data = None
    
    def avatar_url_as(self, format='jpg', size=1024):
        assert self._icon_data != None ,'if url is none it will exception while real work'
        return FakeAsset(self._icon_data)
        
@mock.patch("NewProfile.Message", autospec= True)
class FakeMessage():
    def __init__(self, channel= None, content= None, file= None, author = None) -> None:
        self.channel = channel
        self.content = content
        self.author = author
        if channel:
            self.guild = channel.guild
        self.file = file

@mock.patch('NewProfile.commands.context', autospec= True)
class FakeContext():
    def __init__(self, client=None, channel=None, author=None, bot= False) -> None:
        self.author = author
        self.guild = client
        self.channel = channel
        self.bot = bot

      
class FakeChannel():
    def __init__(self, channel_id:id):
        self.id = channel_id
        self.name = 'test chennel{}'.format(id)
    

@mock.patch('NewProfile.TextChannel', autospec= True)
class FakeTextChannel(FakeChannel):
    def __init__(self, channel_id: id, guild):
        super().__init__(channel_id)
        self.guild = guild
    async def send(self, content= '', file= None, embed= None):
        fake_user = FakeUser(self.guild._client.id, 'fake bot', bot= True)
        fake_msg = None
        if content:
            fake_msg = FakeMessage(channel = self, author=fake_user, content= content )
        if file:
            fake_msg = FakeMessage(channel = self, author=fake_user, file= file)
        #not use yet
        #if embed:
        #    fake_msg = FakeMessage(channel = self, author=fake_user, embed= embed)
        self.guild.messageLast = fake_msg

@mock.patch('NewProfile.Guild', autospec= True)
class FakeGuild():
    def __init__(self, client_id:int, client) -> None:
        self.id = client_id
        self.name = 'test guild{}'.format(client_id)
        self.channels = []
        self.members = []
        self.banner_url = FakeAsset(None)
        self.messageLast = None
        self._client = client
    def _create_channel(self, channel_id) -> FakeTextChannel:
        new_channel = FakeTextChannel(channel_id, self)
        self.channels.append(new_channel)
        return new_channel
    def get_channel(self, channel_id):
        for channel in self.channels:
            if channel.id == channel_id:
                return channel
        return None
    def _add_member(self, member:FakeMember):
        self.members.append(member)

    def get_member(self, member_id:int):
        for member in self.members:
            if member.id == member_id:
                return member


@mock.patch('NewProfile.Client', autospec= True)
class FakeClient():
    def __init__(self, client_id:int) -> None:
        self.id = client_id
        self.guilds = []
    
    def _create_fake_guild(self, guild_id:int) -> FakeGuild:
        newguild = FakeGuild(guild_id, self)
        self.guilds.append(newguild)
        return newguild
    
    def add_cog(*argv):
        return 


class TestNewProfile():
    def setup_method(self, method):
        self.client = FakeClient(1)
        self.fake_guild = self.client._create_fake_guild(786612294762889247)
        self.fake_guild._create_channel(2)
        self.fake_guild._create_channel(3)

        self.target = NewProfile.NewProfile(self.fake_guild, ':memory:')
        
        self.fake_member = FakeMember(member_id= 123, member_name='test name', guild= self.fake_guild, nick_name='test nick name')
        with open(r'./tests/NewProfile/test_icon.jpg', 'rb') as fp:
            self.fake_member._icon_data = fp.read()
            fp.close()
        self.fake_guild._add_member(self.fake_member)

    def teardown_method(self, method):
        self.target.db.teardown()
    
    @pytest.mark.asyncio
    async def test_profile_data_no_banner_and_not_bind(self):
        fakecontext = FakeContext(client= self.fake_guild, author = self.fake_member, channel= self.fake_guild.channels[0])
        await self.target.profile_profile_group(self.target, fakecontext)
        with open(r'./tests/NewProfile/test_image1.PNG', 'rb') as fp:
            assert self.fake_guild.messageLast != None ,'did not send image right.'
            # assert self.fake_guild.messageLast.file.fp.read() == fp.read()
            assert self.fake_guild.messageLast.channel.id == self.fake_guild.channels[0].id
            fp.close()
    
    @pytest.mark.asyncio
    async def test_profile_data_with_banner_and_not_bind(self):
        fakecontext = FakeContext(client= self.fake_guild, author = self.fake_member, channel= self.fake_guild.channels[0])
        bannerAsset = None
        with open(r'./tests/NewProfile/banner_test.jpg', 'rb') as fp:
            bannerAsset = FakeAsset(fp.read())
            fp.close()
        self.fake_guild.banner_url = bannerAsset
        await self.target.profile_profile_group(self.target, fakecontext)
        with open(r'./tests/NewProfile/test_image2.PNG', 'rb') as fp:
            # assert self.fake_guild.messageLast.file.fp.read() == fp.read(), 'figrue is not same'
            assert self.fake_guild.messageLast.channel.id == self.fake_guild.channels[0].id
            fp.close()
    
    @pytest.mark.asyncio
    async def test_profile_command_on_privateChannel(self):
        fakecontext = FakeContext(author = self.fake_member)
        await self.target.profile_profile_group(self.target, fakecontext)
        assert self.fake_guild.messageLast == None

    @pytest.mark.asyncio
    async def test_bind_command(self):
        wrong_id = 787878787
        fakecontext = FakeContext(client= self.fake_guild, author = self.fake_member, channel= self.fake_guild.channels[0])
        await self.target.profile_group_bind_command(self.target, fakecontext)
        assert self.fake_guild.messageLast.content == '<@!{}> 設定升級訊息將會於此。'.format(self.fake_member.id)
        assert self.fake_guild.messageLast.channel.id == self.fake_guild.channels[0].id , 'check message chennal'
        assert self.target.db.get_message_channel_id() != None , 'check database'

    def test_not_in_whiteList(self):
        fakecontext = FakeContext(client= self.fake_guild, author = self.fake_member, channel= self.fake_guild.channels[0])
        fakecontext.guild.id = 123
        result =  NewProfile.isWhiteList(fakecontext)
        assert result == False
    
    def test_in_whiteList(self):
        fakecontext = FakeContext(client= self.fake_guild, author = self.fake_member, channel= self.fake_guild.channels[0])
        result =  NewProfile.isWhiteList(fakecontext)
        assert result == True

    @pytest.mark.asyncio
    async def test_member_first_talk_without_bind(self):
        fake_message = FakeMessage(channel= self.fake_guild.channels[0], author= self.fake_member, content= 'anyway')
        await self.target.profile_on_message(fake_message)
        assert self.fake_guild.messageLast.content == '恭喜<@{}> 等級提升至{}。'.format(self.fake_member.id, 1)
        assert self.fake_guild.messageLast.channel.id == fake_message.channel.id
    
    @pytest.mark.asyncio
    async def test_member_first_talk_with_bind(self):
        self.target.db.set_rankup_channel(self.fake_guild.id, self.fake_guild.channels[1].id)
        fake_message = FakeMessage(channel= self.fake_guild.channels[0], author= self.fake_member, content= 'anyway')
        await self.target.profile_on_message(fake_message)
        assert self.fake_guild.messageLast.content == '恭喜<@{}> 等級提升至{}。'.format(self.fake_member.id, 1)
        assert self.fake_guild.messageLast.channel.id == self.fake_guild.channels[1].id

    @pytest.mark.asyncio
    async def test_member_second_talk(self):
        self.target.db.set_rankup_channel(self.fake_guild.id, self.fake_guild.channels[1].id)
        fake_message = FakeMessage(channel= self.fake_guild.channels[0], author= self.fake_member, content= 'anyway')
        await self.target.profile_on_message(fake_message)
        self.fake_guild.messageLast = None
        await self.target.profile_on_message(fake_message)
        assert self.fake_guild.messageLast == None

    @pytest.mark.asyncio
    async def test_member_talk_outof_whiteList(self):
        wrong_id = 97979797979
        self.target.db.set_rankup_channel(self.fake_guild.id, self.fake_guild.channels[1].id)
        fake_message = FakeMessage(channel= self.fake_guild.channels[0], author= self.fake_member, content= 'anyway')
        self.fake_guild.id =wrong_id
        await self.target.profile_on_message(fake_message)
        assert self.fake_guild.messageLast == None
    
    @pytest.mark.asyncio
    async def test_member_talk_on_privateChannel(self):
        wrong_id = 97979797979
        self.target.db.set_rankup_channel(self.fake_guild.id, self.fake_guild.channels[1].id)
        fake_message = FakeMessage(author= self.fake_member, content= 'anyway')
        self.fake_guild.id =wrong_id
        await self.target.profile_on_message(fake_message)
        assert self.fake_guild.messageLast == None
    
    @pytest.mark.asyncio
    async def test_member_talk_is_bot(self):
        wrong_id = 97979797979
        self.target.db.set_rankup_channel(self.fake_guild.id, self.fake_guild.channels[1].id)
        self.fake_member.bot = True
        fake_message = FakeMessage(author= self.fake_member, content= 'anyway')
        self.fake_guild.id =wrong_id
        await self.target.profile_on_message(fake_message)
        assert self.fake_guild.messageLast == None

    def test_profile_cog_setUp(self):
        NewProfile.setup(self.client)