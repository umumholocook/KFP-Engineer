from common.models.KfpRole import KfpRole
from common.RoleUtil import RoleUtil
from discord import Color, Permissions, Role
from discord.ext import commands
from discord.utils import get
from data.DefaultRoleData import KFP_DEFAULT
from main import bot
from common.Util import Util

ROLE_DATA = [KFP_DEFAULT]


class RoleManager(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @bot.event
    async def on_guild_role_update(before: Role, after: Role):
        RoleUtil.updateRole(before.guild.id, before.id, after.name, after.color)
        print(f"updating role with new name {after.name} and color {after.color}")

    async def canUseCommand(self, ctx:commands.Context):
        if ctx.author.id != ctx.guild.owner.id:
            await ctx.channel.send('本功能只有群主可以使用')
            return False
        return True

    @commands.group(name = 'role', invoke_without_command = True)
    async def role_manager_group(self, ctx:commands.Context, *attr):
        await self.canUseCommand(ctx)
        
    @role_manager_group.command(name = 'init')
    async def initialize_roles(self, ctx:commands.Context, *argv):
        # if not await self.canUseCommand(ctx):
        #     return
        msg = await ctx.channel.send('初始化身分組: KFP 預設...')
        for data in ROLE_DATA:
            for role_dic in data:
                role_name = role_dic['name']
                role: Role = get(ctx.guild.roles, name=role_name)
                if role:
                    await msg.edit(content=str(msg.content)+"\n{}已經存在... 合併現有資料".format(role_name))
                else:
                    await msg.edit(content=str(msg.content)+"\n創建身分組{}... ".format(role_name))
                    role = await ctx.guild.create_role(name=role_name, permissions= Permissions(permissions=0) ,colour= Color(role_dic['color']), mentionable= False, hoist=False)
                    await msg.edit(content=str(msg.content)+"完成".format(role_name))
                kfpRole: KfpRole = RoleUtil.updateRole(ctx.guild.id, role.id, role.name, role.color, role_dic["category"])
                RoleUtil.updateKfpRoleLevel(kfpRole, role_dic['level'])

        await ctx.channel.send("身分組初始化完成.")

    @role_manager_group.command(name = 'reset')
    async def reset_roles(self, ctx:commands.Context, *argv):
        # if not await self.canUseCommand(ctx):
        #     return
        RoleUtil.deleteAllData()
        await ctx.channel.send('身分組資料庫清除完畢')

    @role_manager_group.command(name = 'list')
    async def listing_roles(self, ctx:commands.Context, *argv):
        # if not await self.canUseCommand(ctx):
        #     return
        roleList = RoleUtil.getCurrentRoles(ctx.guild.id, Util.RoleCategory.KFP_DEFAULT)
        if len(roleList) == 0:
            await ctx.channel.send("沒有檢查到任何身份組, 請執行 `!role init`")
            return
        msg = ""
        for role in roleList:
            msg += f"{role.role_name}\n"
            msg += f"  id: {role.role_id}\n"
            msg += f"  顏色: {role.color}\n"
            msg += f"  等級: {role.level}\n\n"
        await ctx.channel.send(msg)
        
                
def setup(client):
    client.add_cog(RoleManager(client))