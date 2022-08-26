import io, asyncio, requests
from typing import List
from common.NicknameUtil import NicknameUtil
from common.SusMemeGenerator import SusMemeGenerator
from common.Util import Util
from PIL import Image
from discord.ext import commands
from discord import User, File, Embed

class SusMeme(commands.Cog):
    YAH = "kiara_correct"
    NAY = "kiara_false"
    # YAH = "👀"
    # NAY = "💯"

    COLOR = [
        "BLACK",
        "BLUE",
        "BROWN",
        "CYAN",
        "GRAY",
        "GREEN",
        "LIME",
        "ORANGE",
        "PINK",
        "PURPLE",
        "RED",
        "WHITE",
        "YELLOW",
        "RANDOM",
    ]

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name = 'sus', invoke_without_command=True)
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def sus_group(self, ctx:commands.Context, user:User, crewmate_color:str = "random"):
        if (ctx.message.author.id == 596719831001071629):
            await ctx.message.delete()
        else:
            await self.startSusVoting(ctx, user, True, crewmate_color.upper())
    
    @sus_group.error
    async def sus_error(self, ctx:commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = "等一下, 我還在忙..."
            await ctx.reply(msg)
        else:
            raise error
    
    @sus_group.command(name = "no_icon")
    async def eject(self, ctx:commands.Command, user:User, crewmate_color:str = "random"):
        await self.startSusVoting(ctx, user, False, crewmate_color.upper())
    
    @sus_group.command(name = "help")
    async def show_help_message(self, ctx:commands.Command):
        msg = "如何使用sus\n"
        msg+= "!sus <@用戶名> 生成一個用戶名或著用戶暱稱的被票圖\n"
        msg+= "!sus no_icon <@用戶名> 生成一個不使用頭像的被票圖\n"

        await ctx.send(msg)

    async def startSusVoting(self, ctx:commands.Context, user: User, withAvatar: bool, crewmate_color: str):
        if not crewmate_color in SusMeme.COLOR:
            msg = f"顏色{crewmate_color}錯誤, 請重新輸入\n"
            msg+= "顏色種類:\n"
            msg+= "BLACK\n"
            msg+= "BLUE\n"
            msg+= "BROWN\n"
            msg+= "CYAN\n"
            msg+= "GRAY\n"
            msg+= "GREEN\n"
            msg+= "LIME\n"
            msg+= "ORANGE\n"
            msg+= "PINK\n"
            msg+= "PURPLE\n"
            msg+= "RED\n"
            msg+= "WHITE\n"
            msg+= "YELLOW\n"
            await ctx.send(msg)
            return

        if user.bot:
            user_name = await NicknameUtil.get_user_nickname_or_default(ctx.guild, ctx.message.author)
            bot_name = await NicknameUtil.get_user_nickname_or_default(ctx.guild, user)
            await self.createSusMeme(ctx, user_name, ctx.message.author, True)
            await ctx.send(f"由於{user_name}意圖流放{bot_name}, 現已被流放")
            return

        user_name = await NicknameUtil.get_user_nickname_or_default(ctx.guild, user)

        newMsg = await ctx.send(f"要把{user_name}扔到宇宙裡嗎?")
        yEmoji = await Util.find_emoji_with_name(self.bot, ctx.guild.id, SusMeme.YAH)
        nEmoji = await Util.find_emoji_with_name(self.bot, ctx.guild.id, SusMeme.NAY)
        await newMsg.add_reaction(yEmoji)
        await newMsg.add_reaction(nEmoji)

        for countDown in range(0, 10):
            count = 10 - countDown
            await newMsg.edit(content=str(f"要把{user_name}扔到宇宙裡嗎?({count})"))
            await asyncio.sleep(1)
        await newMsg.edit(content=str(f"要把{user_name}扔到宇宙裡嗎?"))
        newMsg = await ctx.fetch_message(newMsg.id)
        
        yah_count = 0
        nay_count = 0
        for reaction in newMsg.reactions:
            if isinstance(reaction.emoji, str):
                if SusMeme.YAH == reaction.emoji:
                    yah_count = reaction.count
                if SusMeme.NAY == reaction.emoji:
                    nay_count = reaction.count
            else:
                if SusMeme.YAH == reaction.emoji.name:
                    yah_count = reaction.count
                if SusMeme.NAY == reaction.emoji.name:
                    nay_count = reaction.count

        if yah_count > nay_count:
            await ctx.send(f"投票結果, 流放{user_name}")
            await self.createSusMeme(ctx, user_name, user, withAvatar, crewmate_color)
        else:
            await ctx.send(f"投票結果, 不流放{user_name}")

    
    async def createSusMeme(self, ctx:commands.Context, user_name: str, user:User, withAvatar: bool, crewmate_color: str = "RANDOM"):
        msg = await ctx.send("流放中...")

        if withAvatar:
            avatar = self.downloadUserAvatar(user)
            imagePath = SusMemeGenerator.createGif(user_name, avatar, crewmate_color)
        else:
            imagePath = SusMemeGenerator.createGifWithoutAvatar(user_name, crewmate_color)
        
        embedMsg = Embed()
        embedMsg.set_image(url='attachment://sus.gif')

        img = File(imagePath, filename="sus.gif")
        await ctx.send(file=img, embed=embedMsg)
        await msg.delete()

    def downloadUserAvatar(self, user: User):
        avatar_url = user.avatar.url
        data = requests.get(avatar_url).content
        return Image.open(io.BytesIO(data))

    def isGif(self, image: Image):
        try:
            image.seek(1)
        except EOFError:
            return False
        else:
            return True

async def setup(client):
    await client.add_cog(SusMeme(client))