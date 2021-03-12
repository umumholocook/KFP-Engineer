from common.models.KfpRole import KfpRole
from common.RoleUtil import RoleUtil
import os, json
from discord import Color, Permissions, Role
from discord.ext import commands
from discord.utils import get
from data.DefaultRoleData import KFP_DEFAULT

def load_json_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as fp:
            j = json.load(fp)
            fp.close()
            return j
    else:
        return False

def has_permission(file_name:str, guild_id, roles:list):
    tem_dict = load_json_file(str(guild_id)+'rank_role.json') 
    if tem_dict['permissions'] == []:
        return True
    for m_role in roles:
        if m_role.id in  tem_dict['permissions']:
            return True
    return False

ROLE_DATA = [KFP_DEFAULT]

class Manager(commands.Cog):
    def __init__(self, client):
        self.bot = client

    @commands.group(name = 'role', invoke_without_command = True)
    async def role_manager_group(self, ctx:commands.Context, *attr):
        if ctx.author.id != ctx.guild.owner.id:
            await ctx.channel.send('本功能只有群主可以使用')
            return
        
    @role_manager_group.command(name = 'init')
    async def initialize_roles(self, ctx:commands.Context, *argv):
        if ctx.author.id != ctx.guild.owner.id:
            await ctx.channel.send('本功能只有群主可以使用')
            return
        msg = await ctx.channel.send('初始化身分組{}...'.format("KFP 預設"))
        for data in ROLE_DATA:
            for role_dic in data:
                role_name = role_dic['name']
                role: Role = get(ctx.guild.roles, name=role_name)
                if role:
                    await msg.edit(content=str(msg.content)+"\n{}已經存在... 合併現有資料".format(role_name))
                else:
                    await msg.edit(content=str(msg.contnet)+"\n創建身分組{} 完成".format(role_name))
                    role = await ctx.guild.create_role(name=role_name, permissions= Permissions(permissions=0) ,colour= Color(role_dic['color']), mentionable= False, hoist=False)
                kfpRole: KfpRole = RoleUtil.updateRole(ctx.guild.id, role.id, role.name, role.color)
                RoleUtil.updateKfpRoleLevel(kfpRole, role_dic['level'])

        await ctx.channel.send("身分組初始化完成.")

    @commands.command(name = 'link_role',invoke_without_command = True)
    async def Manager_link_role_command(self, ctx, *argv):
        if len(argv)!= 2:
            await ctx.channel.send('vaild argument: link_role 條件身分組 附加身分組')
            return
        guild = ctx.guild
        channel = ctx.channel
        if not has_permission(str(guild.id)+'rank_role.json', guild.id, guild.get_member(ctx.author.id).roles):
            await channel.send('<@{}> 的權限不足使用 link_role'.format(ctx.author.id))
            return
        request_id = argv[0][3:-1]
        request_role = guild.get_role(int(request_id))
        if request_role == None:
            await channel.send('不存在身分組: id({})'.format(request_id))
            return
        target_id = argv[1][3:-1]
        target_role = guild.get_role(int(target_id))
        if request_role == None:
            await channel.send('不存在身分組: id({})'.format(target_id))
            return
        count = 0
        for member in guild.members:
            r_flag =False
            t_flag =True
            for m_role in member.roles:
                if m_role == request_role:
                    r_flag = True
                if m_role == target_role:
                    t_flag = False
            if r_flag and t_flag:
                await member.add_roles(target_role)
                count +=1
        await channel.send('附加身分成功，共{}名成員附加了身分組: {}。'.format(count, target_role.name))
        
        
        

def setup(client):
    client.add_cog(Manager(client))