import asyncio

import discord
from discord import Embed, File, app_commands
from discord.ext import commands

from common.DiscordUtil import DiscordUtil
from common.NicknameUtil import NicknameUtil
from common.SusMemeGenerator import SusMemeGenerator
from common.Util import Util


@app_commands.guild_only()
class SusMeme(commands.GroupCog, group_name="流放", group_description="Among Us 流放投票迷因"):
    YAH = "kiara_correct"
    NAY = "kiara_false"

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

    COLOR_CHOICES = [app_commands.Choice(name=color, value=color) for color in COLOR]

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="投票", description="投票流放指定使用者")
    @app_commands.describe(
        user="要流放的使用者",
        crewmate_color="船員顏色",
    )
    @app_commands.choices(crewmate_color=COLOR_CHOICES)
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    async def sus(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        crewmate_color: str = "RANDOM",
    ) -> None:
        await interaction.response.defer()
        await self.startSusVoting(interaction, user, True, crewmate_color.upper())

    @app_commands.command(name="無頭像", description="投票流放指定使用者（不使用頭像）")
    @app_commands.describe(
        user="要流放的使用者",
        crewmate_color="船員顏色",
    )
    @app_commands.choices(crewmate_color=COLOR_CHOICES)
    async def eject(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        crewmate_color: str = "RANDOM",
    ) -> None:
        await interaction.response.defer()
        await self.startSusVoting(interaction, user, False, crewmate_color.upper())

    @app_commands.command(name="說明", description="流放指令說明")
    async def show_help_message(self, interaction: discord.Interaction) -> None:
        msg = "如何使用流放\n"
        msg += "/流放 投票 <@用戶名> 生成一個用戶名或著用戶暱稱的被票圖\n"
        msg += "/流放 無頭像 <@用戶名> 生成一個不使用頭像的被票圖\n"
        await interaction.response.send_message(msg)

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            msg = "等一下, 我還在忙..."
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        else:
            raise error

    async def startSusVoting(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        with_avatar: bool,
        crewmate_color: str,
    ) -> None:
        channel = interaction.channel

        if crewmate_color not in SusMeme.COLOR:
            msg = f"顏色{crewmate_color}錯誤, 請重新輸入\n"
            msg += "顏色種類:\n"
            msg += "BLACK\n"
            msg += "BLUE\n"
            msg += "BROWN\n"
            msg += "CYAN\n"
            msg += "GRAY\n"
            msg += "GREEN\n"
            msg += "LIME\n"
            msg += "ORANGE\n"
            msg += "PINK\n"
            msg += "PURPLE\n"
            msg += "RED\n"
            msg += "WHITE\n"
            msg += "YELLOW\n"
            await interaction.followup.send(msg)
            return

        if user.bot:
            user_name = await NicknameUtil.get_user_nickname_or_default(
                interaction.guild, interaction.user
            )
            bot_name = await NicknameUtil.get_user_nickname_or_default(
                interaction.guild, user
            )
            await self.createSusMeme(
                channel, user_name, interaction.user, True, crewmate_color
            )
            await interaction.followup.send(
                f"由於{user_name}意圖流放{bot_name}, 現已被流放"
            )
            return

        user_name = await NicknameUtil.get_user_nickname_or_default(
            interaction.guild, user
        )

        new_msg = await channel.send(f"要把{user_name}扔到宇宙裡嗎?")
        y_emoji = await Util.find_emoji_with_name(
            self.bot, interaction.guild.id, SusMeme.YAH
        )
        n_emoji = await Util.find_emoji_with_name(
            self.bot, interaction.guild.id, SusMeme.NAY
        )
        await new_msg.add_reaction(y_emoji)
        await new_msg.add_reaction(n_emoji)

        for count_down in range(0, 10):
            count = 10 - count_down
            await new_msg.edit(content=str(f"要把{user_name}扔到宇宙裡嗎?({count})"))
            await asyncio.sleep(1)
        await new_msg.edit(content=str(f"要把{user_name}扔到宇宙裡嗎?"))
        new_msg = await channel.fetch_message(new_msg.id)

        yah_count = 0
        nay_count = 0
        for reaction in new_msg.reactions:
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
            await channel.send(f"投票結果, 流放{user_name}")
            await self.createSusMeme(
                channel, user_name, user, with_avatar, crewmate_color
            )
        else:
            await channel.send(f"投票結果, 不流放{user_name}")

    async def createSusMeme(
        self,
        channel: discord.abc.Messageable,
        user_name: str,
        user: discord.User,
        with_avatar: bool,
        crewmate_color: str = "RANDOM",
    ) -> None:
        msg = await channel.send("流放中...")

        if with_avatar:
            avatar = await DiscordUtil.read_avatar_image(user)
            image_path = SusMemeGenerator.createGif(user_name, avatar, crewmate_color)
        else:
            image_path = SusMemeGenerator.createGifWithoutAvatar(
                user_name, crewmate_color
            )

        embed_msg = Embed()
        embed_msg.set_image(url="attachment://sus.gif")

        img = File(image_path, filename="sus.gif")
        await channel.send(file=img, embed=embed_msg)
        await msg.delete()

async def setup(client):
    await client.add_cog(SusMeme(client))