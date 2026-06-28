import discord
from common.NicknameUtil import NicknameUtil
from common.PoliceResponseUtil import PoliceResponseUtil
from common.PoliceUtil import PoliceUtil
from common.RoleUtil import RoleUtil
from common.Util import Util
from discord import Member, Message, User, app_commands
from discord.app_commands import Choice
from discord.ext import commands


class PoliceControl(commands.GroupCog, group_name='警察', group_description='警察監視功能'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener('on_message')
    async def police_watch_message(self, message: Message) -> None:
        if message.author.bot:
            return
        currentType = PoliceUtil.getCurrentPoliceType(
            guild_id=message.guild.id, user_id=message.author.id
        )
        if len(currentType) > 0:
            user_name = await NicknameUtil.get_user_nickname_or_default(
                guild=message.guild, user=message.author
            )
            msg = PoliceResponseUtil.getResponse(currentType).format_map(
                {
                    'name': user_name,
                    'action': PoliceUtil.getPoliceTypeChineseName(currentType),
                }
            )
            await message.reply(msg)

    @app_commands.command(name='設定', description='設定警察監視用戶')
    @app_commands.describe(
        type='警察類型',
        user='要被監視的用戶',
    )
    @app_commands.choices(
        type=[
            Choice(name='睡覺', value='SLEEP'),
            Choice(name='吃飯', value='EAT'),
            Choice(name='洗澡', value='SHOWER'),
            Choice(name='讀書', value='STUDY'),
            Choice(name='寫作業', value='HOMEWORK'),
            Choice(name='生日', value='BIRTHDAY'),
        ]
    )
    @app_commands.guild_only()
    async def set_police(
        self, interaction: discord.Interaction, type: str, user: Member
    ) -> None:
        if not await self.canRunCommand(interaction, interaction.user):
            await interaction.response.send_message("你不是警察, 無法執行這個指令")
            return
        guild_id = interaction.guild.id
        currentType = PoliceUtil.getCurrentPoliceType(guild_id=guild_id, user_id=user.id)
        user_name = await NicknameUtil.get_user_nickname_or_default(interaction.guild, user)
        if len(currentType) > 0:
            await interaction.response.send_message(
                f"{user_name}已經被{PoliceUtil.getPoliceTypeChineseName(currentType)}警察監視了, 無法增加更多警力!!"
            )
            return
        PoliceUtil.createNewPolice(guild_id=guild_id, user_id=user.id, type=type)
        await interaction.response.send_message(
            f"{user_name}現在已經被{PoliceUtil.getPoliceTypeChineseName(type)}警察監視啦!"
        )

    @app_commands.command(name='查詢', description='查看用戶是否被警察監視')
    @app_commands.describe(user='要查詢的用戶')
    @app_commands.guild_only()
    async def lookup_police(self, interaction: discord.Interaction, user: Member) -> None:
        if not await self.canRunCommand(interaction, interaction.user):
            await interaction.response.send_message("你不是警察, 無法執行這個指令")
            return
        guild_id = interaction.guild.id
        currentType = PoliceUtil.getCurrentPoliceType(guild_id=guild_id, user_id=user.id)
        user_name = await NicknameUtil.get_user_nickname_or_default(interaction.guild, user)
        if len(currentType) > 0:
            await interaction.response.send_message(
                f"{user_name}現在被{PoliceUtil.getPoliceTypeChineseName(currentType)}警察監視中!!"
            )
        else:
            await interaction.response.send_message(f"{user_name}沒有被監視")

    @app_commands.command(name='解除', description='取消用戶目前的警察監視')
    @app_commands.describe(user='要解除監視的用戶')
    @app_commands.guild_only()
    async def clear_police(self, interaction: discord.Interaction, user: Member) -> None:
        if not await self.canRunCommand(interaction, interaction.user):
            await interaction.response.send_message("你不是警察, 無法執行這個指令")
            return
        guild_id = interaction.guild.id
        user_name = await NicknameUtil.get_user_nickname_or_default(interaction.guild, user)
        if PoliceUtil.stopPolice(guild_id=guild_id, user_id=user.id):
            await interaction.response.send_message(f"已經停止對{user_name}的監視")
        else:
            await interaction.response.send_message(
                f"我們沒有在監視{user_name}啊... 還是說你想...?"
            )

    async def canRunCommand(self, interaction: discord.Interaction, user: User) -> bool:
        roleId = RoleUtil.getCategoryRole(
            guild_id=interaction.guild.id, category=Util.RoleCategory.KFP_UTIL
        )
        for role in interaction.guild.roles:
            if role.id == roleId:
                for member in role.members:
                    if user.id == member.id:
                        return True
        return False


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PoliceControl(bot))