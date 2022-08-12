from common.RPGUtil.RPGCharacterUtil import RPGCharacterUtil
from common.models.InventoryRecord import InventoryRecord
from common.RPGUtil.InventoryUtil import InventoryUtil
from discord.abc import GuildChannel, User
from discord.embeds import Embed
from discord.errors import NotFound
from discord.guild import Guild
from common.models.KfpRole import KfpRole
from common.RoleUtil import RoleUtil
from common.models.Member import Member
import discord, os, io
from PIL import Image, ImageDraw, ImageFont ,ImageEnhance
from discord import Message, Role
from discord.ext import commands
from random import randint
from common.KFP_DB import KfpDb 
from common.Util import Util
from common.ChannelUtil import ChannelUtil

class ProfileImage(object):
    def __init__(self):
        super(ProfileImage,self).__init__()
        self.image = Image.new('RGBA', (934,282), (0, 0, 0, 0))
        self.cardBase = Image.open(os.sep.join((os.getcwd(), 'resource', 'image', 'card_base.png')))
        self.backGround = None
        self.icon = None
        assert os.path.exists(os.sep.join((os.getcwd(), 'resource', 'ttf', 'NotoSansMonoCJKtc-Regular.otf'))), "can't find {}".format(os.sep.join((os.getcwd(), 'resource', 'ttf', 'NotoSansMonoCJKtc-Regular.otf')))
        self.fontPath = os.sep.join((os.getcwd(), 'resource', 'ttf', 'NotoSansMonoCJKtc-Regular.otf'))
        self.displayName = ''
        self.userName = ''
        self.rankNumber = -1
        self.levelNumber = 0
        self.xpNumber = 0
        self.coinNumber = 0
        
    def resizeAndCrop(self,image, x:int, y:int) -> Image:
        assert x > 0, 'argument x need to more than 0, x : '.format(x)
        assert y > 0, 'argument y need to more than 0, y : {}'.format(y)
        
        reSizedImage = image.resize((x, int(x*image.size[1]/image.size[0])), Image.ANTIALIAS)
        t_pos = (reSizedImage.size[1]-y)/2 if (reSizedImage.size[1]-y)/2 > 0 else (y-reSizedImage.size[1])/2
        reSizedImage = reSizedImage.crop((0, t_pos, reSizedImage.size[0], reSizedImage.size[1]))
        return reSizedImage

    def setBackGround(self, data:bytes) -> None:
        assert isinstance(data, bytes), 'data need to be a byte-like argument'

        backGround = Image.open(io.BytesIO(data))
        reSizedBackGround = self.resizeAndCrop(backGround, 934, 282)
        backGround.close()
        self.backGround = reSizedBackGround
    
    def setIcon(self, data:bytes) -> None:
        assert isinstance(data, bytes), 'data need to be a byte-like argument'
        
        self.icon = Image.open(io.BytesIO(data))
    
    def setMemberName(self, display_name:str , user_name:str) -> None:
        self.displayName = display_name
        self.userName = user_name

    def setRankNumber(self, rank_number:int) -> None:
        self.rankNumber = rank_number
    
    def setLevelNumber(self, level_number:int) -> None:
        self.levelNumber = level_number
    
    def setXp(self, xp_number:int) -> None:
        self.xpNumber = xp_number

    def setCoin(self, coin_number:int) -> None:
        self.coinNumber = coin_number
    
    def generateProfileImage(self) -> bytes:
        self._pasteBackGround()
        self._pasteBaseModel()
        self._pasteIcon()
        self._drawMemberText()
        self._drawRankText()
        self._drawXpAndCoin()
        imgByteArr = io.BytesIO()
        self.image.save(imgByteArr,format="PNG")
        #with open(r'tests/NewProfile/test_image2.PNG', 'wb') as fp:
        #    self.image.save(fp, format="PNG")
        #    fp.close()
        return imgByteArr.getvalue()

    def _pasteBackGround(self) -> None:
        if self.backGround == None:
            return
        self.image.paste(self.backGround, (0, 0))
    
    def _pasteBaseModel(self) -> None:
        cardBaseRGBA = self.cardBase.convert('RGBA')
        alpha = cardBaseRGBA.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.6)
        cardBaseRGBA.putalpha(alpha)
        self.image=Image.composite(cardBaseRGBA, self.image, cardBaseRGBA)
        cardBaseRGBA.close()
    
    def _pasteIcon(self) -> None:
        self.image.paste(self.icon.resize((142,142)), (60, 70))
        
    def _drawMemberText(self) -> None:
        draw = ImageDraw.Draw(self.image)
        memberTextFont = ImageFont.truetype(font=self.fontPath, size=46,encoding='utf-8')
        userTextFont = ImageFont.truetype(font=self.fontPath, size=27,encoding='utf-8')
        displayNameSize = draw.textsize(self.displayName, font=memberTextFont)
        userNameSize = draw.textsize(self.userName, font=userTextFont)
        draw.text((250,110), self.displayName, font=memberTextFont)
        draw.text((250+displayNameSize[0]+20, 110+displayNameSize[1]-userNameSize[1]), '('+self.userName+')', font=userTextFont, fill='#ADADAD')

    def _drawRankText(self) -> None:
        draw = ImageDraw.Draw(self.image)
        level_1_text = '等級'
        level_1_size =  26
        level_1_font = ImageFont.truetype(font = self.fontPath, size=level_1_size,encoding='utf-8')

        level_2_text = str(self.levelNumber)
        level_2_size = 48
        level_2_font = ImageFont.truetype(font=self.fontPath, size=level_2_size,encoding='utf-8')

        rank_1_text = '排名'
        rank_1_size = 26
        rank_1_font = ImageFont.truetype(font=self.fontPath, size=rank_1_size,encoding='utf-8')

        rank_2_text = '#'+str(self.rankNumber)
        rank_2_size = 48
        rank_2_font = ImageFont.truetype(font=self.fontPath, size=rank_2_size,encoding='utf-8')

        x_base = 934 - 60
        x_base -= draw.textsize(level_2_text, font=level_2_font)[0]
        draw.text((x_base, 48), level_2_text, font=level_2_font ,fill='#FF0000')
        x_base -= (draw.textsize(level_1_text, font=level_1_font)[0] + 5)
        draw.text((x_base, 70), level_1_text, font=level_1_font ,fill='#FF0000')
        x_base -= (draw.textsize(rank_2_text, font=rank_2_font)[0]+15)
        draw.text((x_base, 48), rank_2_text, font=rank_2_font )
        x_base -= (draw.textsize(rank_1_text, font=rank_1_font)[0]+10)
        draw.text((x_base, 70), rank_1_text, font=rank_1_font )

    
    def _drawXpAndCoin(self) -> None:
        draw = ImageDraw.Draw(self.image)
        common_size = 27
        common_font = ImageFont.truetype(font=self.fontPath, size=common_size, encoding='utf-8')
        
        text_list_1 = ('硬幣:', str(self.coinNumber))
        text_list_fill_1 = ('#E1E100', '#F9F900')[::-1]
        text_list_2 = (str(self.xpNumber), '/', "{:0.2f}".format(Util.get_rank_exp(self.levelNumber + 1)), 'XP')
        text_list_fill_2 = ('#FFFFFF', '#ADADAD', '#ADADAD', '#ADADAD')[::-1]

        x_base = 934 - 60 - 30
        y = 171+15
        for i,t in enumerate(text_list_2[::-1]):
            offset = draw.textsize(t, font=common_font)
            x_base -= (offset[0]+5)
            draw.text((x_base, y), t, fill=text_list_fill_2[i], font=common_font)
        x_base -= 15
        for i,t in enumerate(text_list_1[::-1]):
            offset = draw.textsize(t, font=common_font)
            x_base -= (offset[0]+5)
            draw.text((x_base, y), t, fill=text_list_fill_1[i], font=common_font)
    
    def _closeAllImage(self) -> None:
        self.image.close()
        if self.backGround != None:
            self.backGround.close()
        self.cardBase.close()

    def __enter__(self):
        return self

    def __exit__(self,exception_type, exception_value, exception_traceback):
        self._closeAllImage()

#因為我不想改回去多伺服器的，就鎖乾淨吧
whitelist = [770197802470735913, 786612294762889247, 749699470819590155]

def isWhiteList(ctx):
    if ctx.guild == None:
        return False
    return ctx.guild.id in whitelist

class NewProfile(commands.Cog):
    #TODO: add check permiision function, base on roles
    db = None

    __channels = []

    def __init__(self, client, dbFile:str, isTest=False):
        self.bot = client
        self.db = KfpDb(dbFile)
        self.isTest = isTest

    @commands.Cog.listener('on_message')
    async def profile_on_message(self, message:Message):
        if message.author.bot:
            return
        if message.channel == None or not message.channel.guild.id in whitelist or message.author.bot:
            return
        if self.populateChannels(message, self.isTest):
            return
        if not self.channelAllowed(message.channel.id, self.isTest):
            return
        member: Member = self.db.get_member(message.author.id)
        if not member:
            self.db.add_member(message.author.id)
            member = self.db.get_member(message.author.id)
        increaseNumber = randint(10,25)
        rank = self.db.increase_exp(message.channel.guild.id, message.channel.id, message.author.id, increaseNumber)
        assert rank > 0, 'method increase_xp should not retrun less than 1 in profile_on_message'
        if member.rank != rank:
            channel = ChannelUtil.getMessageChannelId(message.guild.id)
            if channel == None:
                channelToUse = message.channel
            else:
                channelToUse = message.guild.get_channel(channel)
            RPGCharacterUtil.levelUpCharacter(message.author.id, member.rank, rank)
            await channelToUse.send('恭喜<@{}> 等級提升至{}。'.format(message.author.id, rank))
            await self.updateUserKfpRoles(message, rank, channelToUse)
        self.db.increase_coin(message.guild.id, message.author.id, increaseNumber)
    
    @commands.group(name = 'profile', invoke_without_command = True)
    async def profile_group(self, ctx:commands.Context, *attr):
        if not isWhiteList(ctx):
            if ctx.guild:
                print("{} is not on white list, if you are a developer, add your server to the white list".format(ctx.guild.id))
            return
        if not ChannelUtil.hasChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.PROFILE):
            print("WARNING: cannot run on this channel, if you are a developer, try to use '!commandControll add profile'")
            return
        memberRow: Member = self.db.get_member(ctx.author.id)
        if memberRow == None:
            self.db.add_member(ctx.author.id)
            memberRow = self.db.get_member(ctx.author.id)

        profileByte = None
        iconData = None
        bgData = None
        avatar_url = ctx.author.avatar
        if avatar_url != None and avatar_url._url != None:
            iconData = await avatar_url.read()
        banner_url = ctx.guild.banner
        if banner_url != None and banner_url._url != None:
            bgData = await banner_url.read()
        with ProfileImage() as pf: 
            if iconData:
                pf.setIcon(iconData)
            if bgData:
                pf.setBackGround(bgData)
            pf.setCoin(memberRow.coin)
            pf.setXp(memberRow.exp)
            pf.setLevelNumber(memberRow.rank)
            pf.setRankNumber(self.db.get_member_rank_order(ctx.author.id))
            pf.setMemberName(ctx.author.display_name, ctx.author.name)
            profileByte = pf.generateProfileImage()

        discordFile = discord.File(io.BytesIO(profileByte), filename='profile.png')
        await ctx.channel.send(file= discordFile)
        

    @profile_group.command(name= 'bind')
    @commands.check(isWhiteList)
    async def profile_group_bind_command(self, ctx:commands.Context, *arg):
        channel = ctx.channel
        ChannelUtil.setRankupChannel(ctx.guild.id, channel.id)
        await channel.send('<@!{}> 設定升級訊息將會於此。'.format(ctx.author.id))

    @profile_group.command(name = 'allowed')
    async def profile_allowed_channels_command(self, ctx:commands.Context, *arg):
        msg = "```"
        msg+= "allowed channel list:\n"
        for channel_id in self.__channels:
            channel = ctx.guild.get_channel(channel_id)
            msg+= f"{channel.id}: {channel.name}\n"
        msg+= "```"
        await ctx.channel.send(msg)
    
    # @profile_group.command('force_set_level')
    # @commands.check(isWhiteList)
    # async def profile_force_set_level(self, ctx:commands.Context, rank=10):
    #     message = ctx.message
    #     member: Member = self.db.get_member(message.author.id)
    #     if not member:
    #         member = self.db.add_member(message.author.id)
    #     if member.rank != rank:
    #         self.db.force_update_rank(member.member_id, rank)
    #         channel = ChannelUtil.getMessageChannelId(message.guild.id)
    #         if channel == None:
    #             channelToUse = message.channel
    #         else:
    #             channelToUse = message.guild.get_channel(channel)
    #         await channelToUse.send('恭喜<@{}> 等級提升至{}。'.format(message.author.id, rank))
            
    #         await self.updateUserKfpRoles(message, rank, channelToUse)
    
    # @profile_group.command("force_rpg_level")
    # @commands.check(isWhiteList)
    # async def profile_force_set_level(self, ctx:commands.Context, rank=10):
    #     message = ctx.message
    #     RPGCharacterUtil.levelUpCharacter(message.author.id, 1, rank)

    # @profile_group.command('force_set_exp')
    # async def profile_force_set_exp(self, ctx:commands.Context, exp=-1):
    #     if exp < 1:
    #         return
    #     message = ctx.message
    #     member: Member = self.db.get_member(message.author.id)
    #     if not member:
    #         member = self.db.add_member(message.author.id)
    #     self.db.set_exp(member.member_id, exp)
    #     member: Member = self.db.get_member(message.author.id)
    #     await ctx.send(f"你現在有經驗值:{member.exp}")

    # @profile_group.command('get_rank_exp')
    # async def profile_get_rank_exp(self, ctx:commands.Context, rank=0):
    #     if rank < 1:
    #         return
    #     exp_needed = Util.get_rank_exp(rank)
    #     await ctx.send(f"要升級到等級{rank} 需要經驗值:{exp_needed}")

    @profile_group.command('items')
    async def show_items_command(self, ctx:commands.Context):
        if ctx.author.bot:
            return # ignore bot
        records = InventoryUtil.getAllItemsBelongToUser(ctx.guild.id, ctx.author.id)
        msg = ""
        if len(records) > 0:
            msg+= "你現在有以下物品:\n"
            record : InventoryRecord
            for record in records:
                msg += f"{record.item.name} x {record.amount}\n"
        else:
            msg +="你目前沒有任何物品"

        await ctx.author.send(msg)

    @profile_group.command('syncAllRank')
    @commands.check(isWhiteList)
    async def reset_everyone_rank(self, ctx:commands.Context, rank=0):
        member_id_list = Member.select(Member.member_id).where(Member.rank >= rank)
        for member_id in member_id_list:
            member: Member = self.db.get_member(member_id)
            try:
                user = await ctx.guild.fetch_member(member_id)
            except NotFound as e:
                continue
            await self.__updateUserRole(ctx.guild, user, member, member.rank, None, True)

    @profile_group.command(name = 'leaderboard')
    @commands.check(isWhiteList)
    async def profile_leaderboard(self, ctx:commands.Context, limit=10):
        max_limit = 25
        if limit > max_limit:
            await ctx.channel.send(f'{limit} 超過上限, 請選擇小於 {max_limit} 的數字')
            return
        top_leaders = self.db.get_leader_board(limit)
        msg = "```"
        msg+= "員工等級排名:\n"
        member: Member
        for rank, member in enumerate(top_leaders):
            guild_member = ctx.guild.get_member(member.member_id)
            user = await self.bot.fetch_user(member.member_id)
            if guild_member:
                if guild_member.nick:
                    msg+= f"第{rank+1}名: {guild_member.nick}\n"
                else:
                    msg+= f"第{rank+1}名: {guild_member.display_name}\n"
            elif user:
                msg+= f"第{rank+1}名: {user.display_name}\n"
        msg+= "```"
        await ctx.channel.send(msg)
    
    async def updateUserKfpRoles(self, message:Message, rank: int, channelToUse:GuildChannel):
        member = Member.select().where(Member.member_id == message.author.id)
        user = message.author
        await self.__updateUserRole(message.guild, user, member, rank, channelToUse, False)
    
    async def __updateUserRole(self, guild:Guild, user:User, member: Member, rank: int, channelToUse:GuildChannel, internal: bool):
        if user:
            if member:
                newRoles = RoleUtil.getKfpRolesFromLevel(guild.id, rank)
                if len(newRoles) > 0:
                    for newRole in newRoles:
                        newGuildRole: Role = guild.get_role(newRole.role_id)
                        if newGuildRole:
                            if not newGuildRole in user.roles:
                                # 用戶有新身份組 
                                # 先移除所有不符合的身份組
                                oldRoles: KfpRole = RoleUtil.getCurrentRoles(guild.id, Util.RoleCategory(newRole.category))
                                if oldRoles:
                                    oldGuildRoles = []
                                    for oldRole in oldRoles:
                                        guildRole = guild.get_role(oldRole.role_id)
                                        if guildRole and guildRole in user.roles:
                                            oldGuildRoles.append(guildRole)
                                    for oldGuildRole in oldGuildRoles:
                                        await user.remove_roles(oldGuildRole)
                                # 添加新的身份組
                                await user.add_roles(newGuildRole)
                                if internal:
                                    print("adding role {} to member {} successed!".format(newGuildRole.name, user.name))
                                else:
                                    embed = Embed()
                                    embed.description = '恭喜<@!{}> 成為 {}'.format(user.id, newGuildRole.name)
                                    await channelToUse.send(embed= embed)

    def populateChannels(self, message:Message, isTest: bool):
        if isTest:
            return False
        if len(self.__channels) == 0:
            categories = message.guild.categories
            for category in categories:
                if category.name == "🐔員工大廳-Hühnerfarm":
                    channels = category.channels
                    result = []
                    for channel in channels: 
                        result.append(channel.id)
                    self.__channels = result
                    return True
        return False
    
    def channelAllowed(self, channel_id:int, isTest: bool):
        if isTest:
            return True
        return channel_id in self.__channels
            
async def setup(client, isTest=False):
    await client.add_cog(NewProfile(client, Util.DEFAULT_DB_PATH, isTest))
