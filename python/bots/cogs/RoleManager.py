from typing import List

import discord
from discord import Color, Permissions, Role, app_commands
from discord.ext import commands

from common.RoleUtil import RoleUtil
from common.Util import Util
from common.models.KfpRole import KfpRole
from data.DefaultRoleData import KFP_DEFAULT
from data.LEWDRoleData import KFP_LEWD
from data.UtilRoleData import KFP_UTIL

ROLE_DATA = [KFP_DEFAULT, KFP_LEWD, KFP_UTIL]


@app_commands.guild_only()
class RoleManager(commands.GroupCog, group_name="身分組", group_description="管理 KFP 身分組"):
    def __init__(self, client):
        self.bot = client

    async def _require_owner(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(
                "本功能只有群主可以使用", ephemeral=True
            )
            return False
        return True

    def findRole(self, roles: List[Role], name: str):
        result = []
        for role in roles:
            if name in role.name:
                result.append(role)
        return result

    @app_commands.command(name="初始化", description="初始化身分組")
    async def initialize_roles(self, interaction: discord.Interaction) -> None:
        if not await self._require_owner(interaction):
            return
        await interaction.response.defer()
        msg = await interaction.followup.send("初始化身分組: KFP 預設...")
        for data in ROLE_DATA:
            for role_dic in data:
                role_matcher = role_dic["matcher"]
                role_name = role_dic["name"]
                roles: Role = self.findRole(interaction.guild.roles, role_matcher)
                if len(roles) > 0:
                    await msg.edit(
                        content=str(msg.content)
                        + "\n{}已經存在... 合併現有資料".format(roles[0].name)
                    )
                else:
                    await msg.edit(
                        content=str(msg.content) + "\n創建身分組{}... ".format(role_name)
                    )
                    role = await interaction.guild.create_role(
                        name=role_name,
                        permissions=Permissions(permissions=0),
                        colour=Color(role_dic["color"]),
                        mentionable=False,
                        hoist=False,
                    )
                    await msg.edit(content=str(msg.content) + "完成".format(role_name))
                if len(roles) > 0:
                    role = roles[0]
                kfpRole: KfpRole = RoleUtil.updateRole(
                    interaction.guild.id,
                    role.id,
                    role.name,
                    role.color,
                    role_dic["category"],
                )
                RoleUtil.updateKfpRoleLevel(kfpRole, role_dic["level"])

        await interaction.followup.send("身分組初始化完成.")

    @app_commands.command(name="顯示", description="顯示所有 KFP 預設身份組")
    async def show_kfp_roles(self, interaction: discord.Interaction) -> None:
        if not await self._require_owner(interaction):
            return
        await interaction.response.defer()
        msg = await interaction.followup.send("顯示所有KFP預設身份組")
        for data in ROLE_DATA:
            for role_dic in data:
                role_name = role_dic["matcher"]
                roles: list[Role] = self.findRole(interaction.guild.roles, role_name)
                if len(roles) > 0:
                    names = ",".join(map(lambda role: role.name, roles))
                    await msg.edit(
                        content=str(msg.content)
                        + "\n找到{}身份組: {}".format(role_name, names)
                    )
        await interaction.followup.send("查找結束.")

    @app_commands.command(name="重置", description="清除身分組資料庫")
    async def reset_roles(self, interaction: discord.Interaction) -> None:
        if not await self._require_owner(interaction):
            return
        RoleUtil.wipeDataAndKeepTable()
        await interaction.response.send_message("身分組資料庫清除完畢")

    @app_commands.command(name="列表", description="列出 KFP 預設身分組")
    async def listing_roles(self, interaction: discord.Interaction) -> None:
        if not await self._require_owner(interaction):
            return
        msg = RoleManager.listRole(interaction.guild.id, Util.RoleCategory.KFP_DEFAULT)
        await interaction.response.send_message(msg)

    @app_commands.command(name="全部列表", description="列出所有類別的身分組")
    async def list_role_detail(self, interaction: discord.Interaction) -> None:
        if not await self._require_owner(interaction):
            return
        msg = ""
        for role_list in [
            Util.RoleCategory.KFP_DEFAULT,
            Util.RoleCategory.KFP_LEWD,
            Util.RoleCategory.KFP_UTIL,
        ]:
            msg += RoleManager.listRole(interaction.guild.id, role_list)
        await interaction.response.send_message(msg)

    @staticmethod
    def listRole(guild_id: int, category: Util.RoleCategory):
        role_list = RoleUtil.getCurrentRoles(guild_id, category)
        if len(role_list) == 0:
            return f"{category}沒有檢查到任何身份組, 請執行 `/身分組 初始化`\n"
        else:
            msg = ""
            for role in role_list:
                msg += f"{role.role_name}\n"
                msg += f"  id: {role.role_id}\n"
                msg += f"  顏色: {role.color}\n"
                msg += f"  等級: {role.level}\n\n"
            return msg


async def setup(client):
    await client.add_cog(RoleManager(client))