from data.UtilRoleData import KFP_UTIL
from operator import contains
from common.models.KfpRole import KfpRole
from common.RoleUtil import RoleUtil
from discord import Color, Permissions, Role
from discord.ext import commands
from discord.utils import get
from data.DefaultRoleData import KFP_DEFAULT
from data.LEWDRoleData import KFP_LEWD
from data.UtilRoleData import KFP_UTIL
from common.Util import Util
from typing import List

ROLE_DATA = [KFP_DEFAULT, KFP_LEWD, KFP_UTIL]


class RoleManager(commands.Cog):
    def __init__(self, client):
        self.bot = client

    async def canUseCommand(self, ctx:commands.Context):
        if ctx.author.id != ctx.guild.owner.id:
            await ctx.channel.send('本功能只有群主可以使用')
            return False
        return True

    def findRole(self, roles: List[Role], name: str):
        result = []
        for role in roles:
            if name in role.name:
                result.append(role)
        return result

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
                role_matcher = role_dic['matcher']
                role_name = role_dic['name']
                roles: Role = self.findRole(ctx.guild.roles, role_matcher)
                if len(roles) > 0:
                    await msg.edit(content=str(msg.content)+"\n{}已經存在... 合併現有資料".format(roles[0].name))
                else:
                    await msg.edit(content=str(msg.content)+"\n創建身分組{}... ".format(role_name))
                    role = await ctx.guild.create_role(name=role_name, permissions= Permissions(permissions=0) ,colour= Color(role_dic['color']), mentionable= False, hoist=False)
                    await msg.edit(content=str(msg.content)+"完成".format(role_name))
                if len(roles) > 0:
                    role = roles[0]
                kfpRole: KfpRole = RoleUtil.updateRole(ctx.guild.id, role.id, role.name, role.color, role_dic["category"])
                RoleUtil.updateKfpRoleLevel(kfpRole, role_dic['level'])

        await ctx.channel.send("身分組初始化完成.")
    
    @role_manager_group.command(name = 'showkfp')
    async def show_kfp_roles(self, ctx:commands.Context, *argv):
        # if not await self.canUseCommand(ctx):
        #     return
        msg = await ctx.channel.send('顯示所有KFP預設身份組')
        for data in ROLE_DATA:
            for role_dic in data:
                role_name = role_dic['matcher']
                roles: list[Role] = self.findRole(ctx.guild.roles, role_name)
                if len(roles) > 0:
                    names = ",".join(map(lambda role: role.name, roles))
                    await msg.edit(content=str(msg.content)+"\n找到{}身份組: {}".format(role_name, names))
        await ctx.channel.send("查找結束.")

    # @role_manager_group.command(name = 'deleteRole')
    # async def delete_role(self, ctx:commands.Context, role_name=""):
    #     if len(role_name) < 1:
    #         return # ignore
    #     role: Role = get(ctx.guild.roles, name=role_name)
    #     if role: 
    #         await ctx.channel.send('{}找到, 移除中...'.format(role_name))
    #         await role.delete()
    #         await ctx.channel.send('{} 移除成功'.format(role_name))
    #     else:
    #         await ctx.channel.send('找不到{}.'.format(role_name))

    @role_manager_group.command(name = 'reset')
    async def reset_roles(self, ctx:commands.Context, *argv):
        # if not await self.canUseCommand(ctx):
        #     return
        RoleUtil.wipeDataAndKeepTable()
        await ctx.channel.send('身分組資料庫清除完畢')

    @role_manager_group.command(name = 'list')
    async def listing_roles(self, ctx:commands.Context, *argv):
        # if not await self.canUseCommand(ctx):
        #     return
        msg = RoleManager.listRole(ctx, Util.RoleCategory.KFP_DEFAULT)
        await ctx.channel.send(msg)
    
    @role_manager_group.command(name = "list_all")
    async def list_role_detail(self, ctx:commands.Context, *argv):
        msg = ""
        for roleList in [Util.RoleCategory.KFP_DEFAULT, Util.RoleCategory.KFP_LEWD, Util.RoleCategory.KFP_UTIL]:
            msg += RoleManager.listRole(ctx, roleList)
        await ctx.channel.send(msg)

    def listRole(ctx:commands.Context, category: Util.RoleCategory):
        roleList = RoleUtil.getCurrentRoles(ctx.guild.id, category)
        if len(roleList) == 0:
            return f"{category}沒有檢查到任何身份組, 請執行 `!role init`\n"
        else:
            msg = ""
            for role in roleList:
                msg += f"{role.role_name}\n"
                msg += f"  id: {role.role_id}\n"
                msg += f"  顏色: {role.color}\n"
                msg += f"  等級: {role.level}\n\n"
            return msg
        
                
def setup(client):
    client.add_cog(RoleManager(client))