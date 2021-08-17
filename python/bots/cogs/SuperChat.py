import io
from PIL import Image
import requests
from discord.ext import commands
from discord import User, File
from common.MemberUtil import MemberUtil
from common.SuperChatUtil import SuperChatUtil
import re


class SuperChatMeme(commands.Cog):
    _ColorWord = {
        "BLUE": 0,
        "CYAN": 150,
        "LIGHTBLUE": 50,
        "MAGENTA": 250,
        "ORANGE": 225,
        "RED": 270,
        "YELLOW": 200,
    }

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='sc', invoke_without_command=True)
    async def superchat_group(self, ctx: commands.Context, sc_money: int, user: User, *args: str):

        # Replace msg
        msg = args
        sc_msg = ""
        for token in msg:
            # user id to name
            result = re.findall("<@!\d+>", token)
            replace = token
            if len(result) != 0:
                for userID in result:
                    member = await ctx.guild.fetch_member(userID[3:-1])
                    replace = member.display_name.join(replace.split(userID))

            # stamp to short msg
            result = re.findall("<:\w+:\d+>", replace)
            if len(result) != 0:
                for stamp in result:
                    stamp_name = re.findall(":\w+:", stamp)
                    replace = stamp_name[0].join(replace.split(stamp))

            if len(sc_msg) < 1:
                sc_msg += replace
            else:
                sc_msg = sc_msg + " " + replace

        if sc_money < 15:
            await ctx.send("至少15硬幣才能使用SuperChat!")
            return
        else:
            sc_color = SuperChatMeme._getColor(sc_money)

        # check msg too long or not
        if len(sc_msg) > SuperChatMeme._ColorWord[sc_color]:
            await ctx.send(f"字數過多!請限制在{SuperChatMeme._ColorWord[sc_color]}字數內!")
            return

        # check author have enough coins or not
        giver = MemberUtil.get_or_add_member(ctx.author.id)
        if giver.coin < sc_money:
            await ctx.send("硬幣不足!快去店外雜談區聊天賺硬幣!")
            return
        adder = MemberUtil.get_or_add_member(user.id)

        # transaction
        MemberUtil.add_coin(member_id=giver.member_id, amount=-sc_money)
        MemberUtil.add_coin(member_id=adder.member_id, amount=sc_money * 0.8)
        MemberUtil.add_coin(member_id=self.bot.user.id, amount=sc_money * 0.2)

        # create image
        avatar = self.downloadUserAvatar(ctx.author)
        imgPath = SuperChatUtil.createSC(ctx.author.name, avatar, sc_money, sc_msg, sc_color)

        img = File(imgPath, filename="result.png")

        if sc_money < 16:
            await ctx.send(f"感謝{ctx.author.display_name}很寒酸的施捨給{user.display_name}的SuperChat!")
        else:
            await ctx.send(f"感謝{ctx.author.display_name}給{user.display_name}的SuperChat!")
        await ctx.send(file=img)

    @superchat_group.command(name="help")
    async def show_help_msg(self, ctx: commands.Command):
        msg = "歡迎大家使用SuperChat功能! 使用方法如下:\n"
        msg += "!sc <硬幣數量> <使用者> <文字> 給該使用者多少硬幣，後面文字可留言(中間不可有空白)\n"
        msg += "每個等級對應的SuperChat文字輸入上限如下:\n"
        msg += "Coin. 15-29 0字元(無法留言)\n"
        msg += "Coin. 30-74 50字元\n"
        msg += "Coin. 75-149 150字元\n"
        msg += "Coin. 150-299 200字元\n"
        msg += "Coin. 300-749 225字元\n"
        msg += "Coin. 750-1499 250字元\n"
        msg += "Coin. 1500以上 270字元\n"
        msg += "註1:避免洗版，最多只會顯示三行\n"
        msg += "註2:每次SuperChat酌收20%手續費，故該用戶只會收到80%的硬幣\n"
        await ctx.send(msg)

    def downloadUserAvatar(self, user: User):
        avatar_url = user.avatar_url
        data = requests.get(avatar_url).content
        return Image.open(io.BytesIO(data))

    def _getColor(money: int):
        if 15 <= money < 30:
            sc_color = "BLUE"
        elif 30 <= money < 75:
            sc_color = "LIGHTBLUE"
        elif 75 <= money < 150:
            sc_color = "CYAN"
        elif 150 <= money < 300:
            sc_color = "YELLOW"
        elif 300 <= money < 750:
            sc_color = "ORANGE"
        elif 750 <= money < 1500:
            sc_color = "MAGENTA"
        else:
            sc_color = "RED"
        return sc_color


def setup(client):
    client.add_cog(SuperChatMeme(client))
