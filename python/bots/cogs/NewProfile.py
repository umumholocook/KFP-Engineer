from common.RPGUtil.RPGCharacterUtil import RPGCharacterUtil
from common.models.InventoryRecord import InventoryRecord
from common.RPGUtil.InventoryUtil import InventoryUtil
from discord.abc import GuildChannel, User
from discord import Embed
from discord.errors import NotFound
from discord.guild import Guild
from common.models.KfpRole import KfpRole
from common.RoleUtil import RoleUtil
from common.models.Member import Member
import discord
import os
import io
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from discord import Message, Role, app_commands
from discord.ext import commands
from random import randint
from common.KFP_DB import KfpDb
from common.Util import Util
from common.ImageUtil import ImageUtil
from common.ChannelUtil import ChannelUtil
from common.InteractionUtil import InteractionUtil


class ProfileImage(object):
    def __init__(self):
        super(ProfileImage, self).__init__()
        self.image = Image.new("RGBA", (934, 282), (0, 0, 0, 0))
        self.cardBase = Image.open(os.sep.join((os.getcwd(), "resource", "image", "card_base.png")))
        self.backGround = None
        self.icon = None
        assert os.path.exists(
            os.sep.join((os.getcwd(), "resource", "ttf", "NotoSansMonoCJKtc-Regular.otf"))
        ), "can't find {}".format(
            os.sep.join((os.getcwd(), "resource", "ttf", "NotoSansMonoCJKtc-Regular.otf"))
        )
        self.fontPath = os.sep.join((os.getcwd(), "resource", "ttf", "NotoSansMonoCJKtc-Regular.otf"))
        self.displayName = ""
        self.userName = ""
        self.rankNumber = -1
        self.levelNumber = 0
        self.xpNumber = 0
        self.coinNumber = 0

    def resizeAndCrop(self, image, x: int, y: int) -> Image:
        assert x > 0, "argument x need to more than 0, x : ".format(x)
        assert y > 0, "argument y need to more than 0, y : {}".format(y)

        reSizedImage = image.resize((x, int(x * image.size[1] / image.size[0])), Image.Resampling.LANCZOS)
        t_pos = (reSizedImage.size[1] - y) / 2 if (reSizedImage.size[1] - y) / 2 > 0 else (y - reSizedImage.size[1]) / 2
        reSizedImage = reSizedImage.crop((0, t_pos, reSizedImage.size[0], reSizedImage.size[1]))
        return reSizedImage

    def setBackGround(self, data: bytes) -> None:
        assert isinstance(data, bytes), "data need to be a byte-like argument"

        backGround = Image.open(io.BytesIO(data))
        reSizedBackGround = self.resizeAndCrop(backGround, 934, 282)
        backGround.close()
        self.backGround = reSizedBackGround

    def setIcon(self, data: bytes) -> None:
        assert isinstance(data, bytes), "data need to be a byte-like argument"

        self.icon = Image.open(io.BytesIO(data))

    def setMemberName(self, display_name: str, user_name: str) -> None:
        self.displayName = display_name
        self.userName = user_name

    def setRankNumber(self, rank_number: int) -> None:
        self.rankNumber = rank_number

    def setLevelNumber(self, level_number: int) -> None:
        self.levelNumber = level_number

    def setXp(self, xp_number: int) -> None:
        self.xpNumber = xp_number

    def setCoin(self, coin_number: int) -> None:
        self.coinNumber = coin_number

    def generateProfileImage(self) -> bytes:
        self._pasteBackGround()
        self._pasteBaseModel()
        self._pasteIcon()
        self._drawMemberText()
        self._drawRankText()
        self._drawXpAndCoin()
        imgByteArr = io.BytesIO()
        self.image.save(imgByteArr, format="PNG")
        return imgByteArr.getvalue()

    def _pasteBackGround(self) -> None:
        if self.backGround is None:
            return
        self.image.paste(self.backGround, (0, 0))

    def _pasteBaseModel(self) -> None:
        cardBaseRGBA = self.cardBase.convert("RGBA")
        alpha = cardBaseRGBA.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.6)
        cardBaseRGBA.putalpha(alpha)
        self.image = Image.composite(cardBaseRGBA, self.image, cardBaseRGBA)
        cardBaseRGBA.close()

    def _pasteIcon(self) -> None:
        self.image.paste(self.icon.resize((142, 142)), (60, 70))

    def _get_text_size(self, draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple:
        text_bbox = draw.textbbox((0, 0), text, font=font)
        width = text_bbox[2] - text_bbox[0]
        height = text_bbox[3] - text_bbox[1]
        return width, height

    def _drawMemberText(self) -> None:
        draw = ImageDraw.Draw(self.image)
        memberTextFont = ImageFont.truetype(font=self.fontPath, size=46, encoding="utf-8")
        userTextFont = ImageFont.truetype(font=self.fontPath, size=27, encoding="utf-8")
        displayNameWidth, displayNameHeight = ImageUtil.get_text_size(
            draw, self.displayName, memberTextFont
        )
        _, userNameHeight = ImageUtil.get_text_size(draw, self.userName, userTextFont)

        draw.text((250, 110), self.displayName, font=memberTextFont)
        draw.text(
            (250 + displayNameWidth + 20, 110 + displayNameHeight - userNameHeight),
            "(" + self.userName + ")",
            font=userTextFont,
            fill="#ADADAD",
        )

    def _drawRankText(self) -> None:
        draw = ImageDraw.Draw(self.image)

        level_1_text = "等級"
        level_1_size = 26
        level_1_font = ImageFont.truetype(font=self.fontPath, size=level_1_size, encoding="utf-8")

        level_2_text = str(self.levelNumber)
        level_2_size = 48
        level_2_font = ImageFont.truetype(font=self.fontPath, size=level_2_size, encoding="utf-8")

        rank_1_text = "排名"
        rank_1_size = 26
        rank_1_font = ImageFont.truetype(font=self.fontPath, size=rank_1_size, encoding="utf-8")

        rank_2_text = "#" + str(self.rankNumber)
        rank_2_size = 48
        rank_2_font = ImageFont.truetype(font=self.fontPath, size=rank_2_size, encoding="utf-8")

        x_base = 934 - 60
        x_base -= ImageUtil.get_text_size(draw, level_2_text, font=level_2_font)[0]
        draw.text((x_base, 48), level_2_text, font=level_2_font, fill="#FF0000")

        x_base -= ImageUtil.get_text_size(draw, level_1_text, font=level_1_font)[0] + 5
        draw.text((x_base, 70), level_1_text, font=level_1_font, fill="#FF0000")

        x_base -= ImageUtil.get_text_size(draw, rank_2_text, font=rank_2_font)[0] + 15
        draw.text((x_base, 48), rank_2_text, font=rank_2_font)

        x_base -= ImageUtil.get_text_size(draw, rank_1_text, font=rank_1_font)[0] + 10
        draw.text((x_base, 70), rank_1_text, font=rank_1_font)

    def _drawXpAndCoin(self) -> None:
        draw = ImageDraw.Draw(self.image)
        common_size = 27
        common_font = ImageFont.truetype(font=self.fontPath, size=common_size, encoding="utf-8")

        text_list_1 = ("硬幣:", str(self.coinNumber))
        text_list_fill_1 = ("#E1E100", "#F9F900")[::-1]
        text_list_2 = (
            str(self.xpNumber),
            "/",
            "{:0.2f}".format(Util.get_rank_exp(self.levelNumber + 1)),
            "XP",
        )
        text_list_fill_2 = ("#FFFFFF", "#ADADAD", "#ADADAD", "#ADADAD")[::-1]

        x_base = 934 - 60 - 30
        y = 171 + 15

        for i, t in enumerate(text_list_2[::-1]):
            offset = ImageUtil.get_text_size(draw, t, font=common_font)
            x_base -= offset[0] + 5
            draw.text((x_base, y), t, fill=text_list_fill_2[i], font=common_font)

        x_base -= 15

        for i, t in enumerate(text_list_1[::-1]):
            offset = ImageUtil.get_text_size(draw, t, font=common_font)
            x_base -= offset[0] + 5
            draw.text((x_base, y), t, fill=text_list_fill_1[i], font=common_font)

    def _closeAllImage(self) -> None:
        self.image.close()
        if self.backGround is not None:
            self.backGround.close()
        self.cardBase.close()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self._closeAllImage()


whitelist = [770197802470735913, 786612294762889247, 749699470819590155]


def is_white_list(guild_id: int) -> bool:
    return guild_id in whitelist


@app_commands.guild_only()
class NewProfile(commands.GroupCog, group_name="個人檔案", group_description="個人檔案與等級系統"):
    db = None
    __channels = []

    def __init__(self, client, dbFile: str, isTest=False):
        self.bot = client
        self.db = KfpDb(dbFile)
        self.isTest = isTest

    async def _require_white_list(self, interaction: discord.Interaction) -> bool:
        if not interaction.guild or not is_white_list(interaction.guild.id):
            if interaction.guild:
                print(
                    "{} is not on white list, if you are a developer, add your server to the white list".format(
                        interaction.guild.id
                    )
                )
            await interaction.response.send_message("此伺服器未啟用此功能。", ephemeral=True)
            return False
        return True

    @commands.Cog.listener("on_message")
    async def profile_on_message(self, message: Message):
        if message.author.bot:
            return
        if message.channel is None or message.channel.guild.id not in whitelist or message.author.bot:
            return
        if self.populateChannels(message, self.isTest):
            return
        if not self.channelAllowed(message.channel.id, self.isTest):
            return
        member: Member = self.db.get_member(message.author.id)
        if not member:
            self.db.add_member(message.author.id)
            member = self.db.get_member(message.author.id)
        increaseNumber = randint(10, 25)
        rank = self.db.increase_exp(
            message.channel.guild.id, message.channel.id, message.author.id, increaseNumber
        )
        assert rank > 0, "method increase_xp should not retrun less than 1 in profile_on_message"
        if member.rank != rank:
            channel = ChannelUtil.getMessageChannelId(message.guild.id)
            if channel is None:
                channelToUse = message.channel
            else:
                channelToUse = message.guild.get_channel(channel)
            RPGCharacterUtil.levelUpCharacter(message.author.id, member.rank, rank)
            await channelToUse.send("恭喜<@{}> 等級提升至{}。".format(message.author.id, rank))
            await self.updateUserKfpRoles(message, rank, channelToUse)
        self.db.increase_coin(message.guild.id, message.author.id, increaseNumber)

    @app_commands.command(name="顯示", description="顯示個人檔案圖片")
    async def profile_display(self, interaction: discord.Interaction):
        if not await self._require_white_list(interaction):
            return
        if not await InteractionUtil.require_channel(interaction, Util.ChannelType.PROFILE):
            return

        memberRow: Member = self.db.get_member(interaction.user.id)
        if memberRow is None:
            self.db.add_member(interaction.user.id)
            memberRow = self.db.get_member(interaction.user.id)

        await interaction.response.defer()

        profileByte = None
        iconData = None
        bgData = None
        iconData = await interaction.user.display_avatar.read()
        if interaction.guild.banner is not None:
            bgData = await interaction.guild.banner.read()

        with ProfileImage() as pf:
            if iconData:
                pf.setIcon(iconData)
            if bgData:
                pf.setBackGround(bgData)
            pf.setCoin(memberRow.coin)
            pf.setXp(memberRow.exp)
            pf.setLevelNumber(memberRow.rank)
            pf.setRankNumber(self.db.get_member_rank_order(interaction.user.id))
            pf.setMemberName(interaction.user.display_name, interaction.user.name)
            profileByte = pf.generateProfileImage()

        discordFile = discord.File(io.BytesIO(profileByte), filename="profile.png")
        await interaction.followup.send(file=discordFile)

    @app_commands.command(name="綁定升級頻道", description="設定升級訊息發送的頻道")
    async def profile_bind_command(self, interaction: discord.Interaction):
        if not await self._require_white_list(interaction):
            return
        channel = interaction.channel
        ChannelUtil.setRankupChannel(interaction.guild.id, channel.id)
        await interaction.response.send_message(
            "<@!{}> 設定升級訊息將會於此。".format(interaction.user.id)
        )

    @app_commands.command(name="允許頻道", description="顯示允許獲得經驗值的頻道列表")
    async def profile_allowed_channels_command(self, interaction: discord.Interaction):
        msg = "```"
        msg += "allowed channel list:\n"
        for channel_id in self.__channels:
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                msg += f"{channel.id}: {channel.name}\n"
        msg += "```"
        await interaction.response.send_message(msg)

    @app_commands.command(name="物品", description="查看目前擁有的物品")
    async def show_items_command(self, interaction: discord.Interaction):
        if interaction.user.bot:
            return
        records = InventoryUtil.getAllItemsBelongToUser(interaction.guild.id, interaction.user.id)
        msg = ""
        if len(records) > 0:
            msg += "你現在有以下物品:\n"
            record: InventoryRecord
            for record in records:
                msg += f"{record.item.name} x {record.amount}\n"
        else:
            msg += "你目前沒有任何物品"

        await interaction.response.defer(ephemeral=True)
        try:
            await interaction.user.send(msg)
            await interaction.followup.send("已將物品清單傳送至你的私訊。", ephemeral=True)
        except discord.HTTPException:
            await interaction.followup.send(msg, ephemeral=True)

    @app_commands.command(name="同步等級", description="同步所有成員的等級身份組")
    @app_commands.describe(rank="最低等級（預設 0）")
    async def reset_everyone_rank(self, interaction: discord.Interaction, rank: int = 0):
        if not await self._require_white_list(interaction):
            return
        await interaction.response.defer(ephemeral=True)
        member_id_list = Member.select(Member.member_id).where(Member.rank >= rank)
        for member_id in member_id_list:
            member: Member = self.db.get_member(member_id)
            try:
                user = await interaction.guild.fetch_member(member_id)
            except NotFound:
                continue
            await self.__updateUserRole(interaction.guild, user, member, member.rank, None, True)
        await interaction.followup.send("同步等級完成")

    @app_commands.command(name="排行榜", description="顯示員工等級排名")
    @app_commands.describe(limit="顯示名次數量（預設 10，上限 25）")
    async def profile_leaderboard(self, interaction: discord.Interaction, limit: int = 10):
        if not await self._require_white_list(interaction):
            return
        max_limit = 25
        if limit > max_limit:
            await interaction.response.send_message(
                f"{limit} 超過上限, 請選擇小於 {max_limit} 的數字"
            )
            return
        top_leaders = self.db.get_leader_board(limit)
        msg = "```"
        msg += "員工等級排名:\n"
        member: Member
        for rank, member in enumerate(top_leaders):
            guild_member = interaction.guild.get_member(member.member_id)
            user = await self.bot.fetch_user(member.member_id)
            if guild_member:
                if guild_member.nick:
                    msg += f"第{rank + 1}名: {guild_member.nick}\n"
                else:
                    msg += f"第{rank + 1}名: {guild_member.display_name}\n"
            elif user:
                msg += f"第{rank + 1}名: {user.display_name}\n"
        msg += "```"
        await interaction.response.send_message(msg)

    async def updateUserKfpRoles(self, message: Message, rank: int, channelToUse: GuildChannel):
        member = Member.select().where(Member.member_id == message.author.id)
        user = message.author
        await self.__updateUserRole(message.guild, user, member, rank, channelToUse, False)

    async def __updateUserRole(
        self,
        guild: Guild,
        user: User,
        member: Member,
        rank: int,
        channelToUse: GuildChannel,
        internal: bool,
    ):
        if user:
            if member:
                newRoles = RoleUtil.getKfpRolesFromLevel(guild.id, rank)
                if len(newRoles) > 0:
                    for newRole in newRoles:
                        newGuildRole: Role = guild.get_role(newRole.role_id)
                        if newGuildRole:
                            if newGuildRole not in user.roles:
                                oldRoles: KfpRole = RoleUtil.getCurrentRoles(
                                    guild.id, Util.RoleCategory(newRole.category)
                                )
                                if oldRoles:
                                    oldGuildRoles = []
                                    for oldRole in oldRoles:
                                        guildRole = guild.get_role(oldRole.role_id)
                                        if guildRole and guildRole in user.roles:
                                            oldGuildRoles.append(guildRole)
                                    for oldGuildRole in oldGuildRoles:
                                        await user.remove_roles(oldGuildRole)
                                await user.add_roles(newGuildRole)
                                if internal:
                                    print(
                                        "adding role {} to member {} successed!".format(
                                            newGuildRole.name, user.name
                                        )
                                    )
                                else:
                                    embed = Embed()
                                    embed.description = "恭喜<@!{}> 成為 {}".format(
                                        user.id, newGuildRole.name
                                    )
                                    await channelToUse.send(embed=embed)

    def populateChannels(self, message: Message, isTest: bool):
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

    def channelAllowed(self, channel_id: int, isTest: bool):
        if isTest:
            return True
        return channel_id in self.__channels


async def setup(client, isTest=False):
    await client.add_cog(NewProfile(client, Util.DEFAULT_DB_PATH, isTest))