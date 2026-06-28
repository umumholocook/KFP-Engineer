import random

import discord
from common.NicknameUtil import NicknameUtil
from common.models.NicknameModel import NicknameModel
from discord import Member, app_commands
from discord.ext import commands


class Nickname(commands.GroupCog, group_name='暱稱', group_description='管理用戶暱稱'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name='設定', description='設定用戶的暱稱')
    @app_commands.describe(user='要設定暱稱的用戶', name='暱稱名稱')
    @app_commands.guild_only()
    async def set_nickname(self, interaction: discord.Interaction, user: Member, name: str) -> None:
        if str(self.bot.user.id) in name:
            await interaction.response.send_message(f"{name}不能當成暱稱使用")
            return
        result = NicknameUtil.set_nickname(interaction.guild.id, user.id, name)
        if result:
            await interaction.response.send_message(f"新增用戶'{user.name}'新暱稱: {name} 成功!")
        else:
            await interaction.response.send_message(f"用戶暱稱'{name}'已經存在.")

    @app_commands.command(name='秘密設定', description='以用戶名稱設定暱稱（管理員專用）')
    @app_commands.describe(user_name='用戶名稱（部分匹配）', name='暱稱名稱')
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def secret_set_nickname(
        self, interaction: discord.Interaction, user_name: str, name: str
    ) -> None:
        if str(self.bot.user.id) in name:
            await interaction.response.send_message(f"{name}不能當成暱稱使用")
            return
        user = await self.find_user_by_name(interaction.guild, user_name)
        if not user:
            await interaction.response.send_message(f"找不到{user_name}")
            return
        result = NicknameUtil.set_nickname(interaction.guild.id, user.id, name)
        if result:
            await interaction.response.send_message(f"新增用戶'{user.name}'新暱稱: {name} 成功!")
        else:
            await interaction.response.send_message(f"用戶暱稱'{name}'已經存在.")

    @app_commands.command(name='列表', description='顯示用戶的暱稱')
    @app_commands.describe(user='要查詢的用戶')
    @app_commands.guild_only()
    async def get_all_nickname(self, interaction: discord.Interaction, user: Member) -> None:
        nicknames = NicknameUtil.get_all_nicknames(interaction.guild.id, user.id)
        if len(nicknames) < 1:
            await interaction.response.send_message(f"{user.name}沒有任何暱稱.")
            return
        result = f"{user.name}有以下暱稱:\n"
        for index, nickname in enumerate(nicknames):
            result += f"  {index + 1}.{nickname}\n"
        await interaction.response.send_message(result)

    @app_commands.command(name='列表詳情', description='顯示用戶暱稱的資料庫編號（管理員專用）')
    @app_commands.describe(user='要查詢的用戶')
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def get_all_nickname_details(self, interaction: discord.Interaction, user: Member) -> None:
        nicknames = NicknameUtil.get_all_nicknames_detail(interaction.guild.id, user.id)
        if len(nicknames) < 1:
            await interaction.response.send_message(f"{user.name}沒有任何暱稱.")
            return
        result = f"{user.name}有以下暱稱:\n"
        nickname: NicknameModel
        for nickname in nicknames:
            result += f"  {nickname.id}.{nickname.nick_name}\n"
        await interaction.response.send_message(result)

    @app_commands.command(name='移除', description='移除用戶的暱稱')
    @app_commands.describe(user='要移除暱稱的用戶', name='要移除的暱稱名稱')
    @app_commands.guild_only()
    async def remove_nickname(
        self, interaction: discord.Interaction, user: Member, name: str
    ) -> None:
        nicknames = NicknameUtil.get_all_nicknames(interaction.guild.id, user.id)
        if len(nicknames) < 1:
            await interaction.response.send_message(f"{user.name}沒有任何暱稱.")
            return
        if not NicknameUtil.remove_nickname(interaction.guild.id, user.id, name):
            await interaction.response.send_message(
                f"{name} 並不是 {user.name}的暱稱, 因此無法刪除."
            )
            return
        await interaction.response.send_message(f"{user.name}的暱稱{name}刪除成功.")

    @app_commands.command(name='移除編號', description='以資料庫編號移除用戶暱稱（管理員專用）')
    @app_commands.describe(user='要移除暱稱的用戶', name_id='暱稱的資料庫編號')
    @app_commands.default_permissions(administrator=True)
    @app_commands.guild_only()
    async def remove_nickname_by_id(
        self, interaction: discord.Interaction, user: Member, name_id: int
    ) -> None:
        nicknames = NicknameUtil.get_all_nicknames(interaction.guild.id, user.id)
        if len(nicknames) < 1:
            await interaction.response.send_message(f"{user.name}沒有任何暱稱.")
            return
        if not NicknameUtil.remove_nickname_id(interaction.guild.id, user.id, name_id):
            await interaction.response.send_message(
                f"{name_id} 並不存在於 {user.name}的暱稱裡, 因此無法刪除."
            )
            return
        await interaction.response.send_message(f"{user.name}的暱稱{name_id}刪除成功.")

    @app_commands.command(name='清除', description='清空用戶所有的暱稱')
    @app_commands.describe(user='要清除暱稱的用戶')
    @app_commands.guild_only()
    async def clear_nickname(self, interaction: discord.Interaction, user: Member) -> None:
        NicknameUtil.clear_nickname(interaction.guild.id, user.id)
        await interaction.response.send_message(f"清除用戶'{user.name}'暱稱成功!")

    @app_commands.command(name='隨機', description='隨機取得用戶的一個暱稱')
    @app_commands.describe(user='要取得暱稱的用戶')
    @app_commands.guild_only()
    async def get_nickname(self, interaction: discord.Interaction, user: Member) -> None:
        nicknames = NicknameUtil.get_all_nicknames(interaction.guild.id, user.id)
        if len(nicknames) > 0:
            nickname_to_use = random.choice(nicknames)
            await interaction.response.send_message(nickname_to_use)
        else:
            await interaction.response.send_message(f"用戶'{user.name}'沒有任何暱稱.")

    async def find_user_by_name(
        self, guild: discord.Guild, user_name: str
    ) -> discord.Member | None:
        for member in guild.members:
            if user_name in member.display_name:
                return member
        return None


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Nickname(bot))