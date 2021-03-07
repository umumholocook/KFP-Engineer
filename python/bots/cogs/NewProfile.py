import discord, os, io
from PIL import Image, ImageDraw, ImageFont ,ImageEnhance
from discord import Message
from discord.ext import commands
from random import randint
from common.KFP_DB import KfpDb 
from common.Util import Util

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
        text_list_2 = (str(self.xpNumber), '/', str(int(Util.get_rank_exp(self.rankNumber + 1))), 'XP')
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

    def __init__(self, client, dbFile:str):
        self.bot = client
        self.db = KfpDb(dbFile)
        
    @commands.Cog.listener('on_message')
    async def profile_on_message(self, message:Message):
        if message.channel == None or not message.channel.guild.id in whitelist or message.author.bot:
            return
        member = message.guild.get_member(message.author.id)
        membeInDb = self.db.get_member(member.id)
        if membeInDb == None:
            self.db.add_member(member.id)
            membeInDb = self.db.get_member(member.id)
        increaseNumber = randint(10,25)
        rank = self.db.increase_exp(member.id, increaseNumber)
        assert rank != False, 'method increase_xp should not retrun None in profile_on_message'
        if membeInDb.rank != rank:
            channel = self.db.get_message_channel_id()
            if channel == None:
                await message.channel.send('恭喜<@{}> 等級提升至{}。'.format(message.author.id, rank))
            else:
                channel = message.guild.get_channel(channel)
                await channel.send('恭喜<@{}> 等級提升至{}。'.format(message.author.id, rank))
    
    @commands.group(name = 'profile', invoke_without_command = True)
    async def profile_profile_group(self, ctx:commands.Context, *attr):
        if not isWhiteList(ctx):
            if ctx.guild:
                print("{} is not on white list, if you are a developer, add your server to the white list".format(ctx.guild.id))
            return
        memberRow = self.db.get_member(ctx.author.id)
        if memberRow == None:
            self.db.add_member(ctx.author.id)
            memberRow = self.db.get_member(ctx.author.id)

        profileByte = None
        iconData = None
        bgData = None
        avatar_url = ctx.author.avatar_url_as(format='jpg', size=1024)
        if avatar_url._url != None:
            iconData = await avatar_url.read()
        banner_url = ctx.guild.banner_url
        if banner_url._url != None:
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
        

    @profile_profile_group.command(name= 'bind')
    @commands.check(isWhiteList)
    async def profile_group_bind_command(self, ctx:commands.Context, *arg):
        channel = ctx.channel
        self.db.set_rankup_channel(channel.id)
        await channel.send('<@!{}> 設定升級訊息將會於此。'.format(ctx.author.id))
            
def setup(client):
    client.add_cog(NewProfile(client, Util.DEFAULT_DB_PATH))
