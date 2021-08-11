import io
from PIL import Image
import requests
from discord.ext import commands
from discord import User, File
from common.SuperChatUtil import SuperChatUtil
from common.NicknameUtil import NicknameUtil

class SuperChatMeme(commands.Cog):
    Color = [
        # "BLUE",
        "CYAN",
        "LIGHTBLUE",
        "MAGENTA",
        "ORANGE",
        "RED",
        "YELLOW",
        "RANDOM"
    ]

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='sc', invoke_without_command=True)
    async def superchat_group(self, ctx:commands.Context, sc_money: int, sc_msg: str, sc_color: str = "RANDOM"):
        if not sc_color in SuperChatMeme.Color:
            msg = f"顏色{sc_color}錯誤, 請重新輸入\n"
            msg += "顏色種類:\n"
            # msg += "BLUE\n"
            msg += "CYAN\n"
            msg += "LIGHTBLUE\n"
            msg += "MAGENTA\n"
            msg += "ORANGE\n"
            msg += "RED\n"
            msg += "YELLOW\n"
            await ctx.send(msg)
            return
        user_name = await NicknameUtil.get_user_nickname_or_default(ctx.guild, ctx.message.author)
        avatar = self.downloadUserAvatar(ctx.author)
        imgPath = SuperChatUtil.createSC(user_name, avatar, sc_money, sc_msg, sc_color)

        img = File(imgPath, filename="result.png")
        await ctx.send(file=img)

    @superchat_group.command(name="help")
    async def show_help_msg(self, ctx: commands.Command):
        msg = "如何使用SuperChat\n"
        msg += "!sc <硬幣數量> <文字> 中文字目前上限27字\n"
        await ctx.send(msg)

    def downloadUserAvatar(self, user: User):
        avatar_url = user.avatar_url
        data = requests.get(avatar_url).content
        return Image.open(io.BytesIO(data))

def setup(client):
    client.add_cog(SuperChatMeme(client))