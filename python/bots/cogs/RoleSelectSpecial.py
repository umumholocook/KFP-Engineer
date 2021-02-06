from common import database_API

import json ,os

import time
from random import seed
from random import randrange

import discord
from discord.ext import commands
from discord import Guild, Member, Message, Reaction, Role
from discord.utils import get

from data import SpecialRoleData

class RoleSelectSpecial(commands.Cog):
    roleMap = {} # <name, id> pair
    initialized = False

    def __init__(self, client):
        self.bot = client

    def check_complete(self,member:Member):
        #TODO:check is user collect complete
        pass

    def shouldGetRole():
        seed(time.time())
        n = randrange(999)
        return n == 42 # 「生命、宇宙以及任何事情的終極答案」 --《銀河便車指南》
    
    # Load existing roles into memory
    def syncRoles(self, ctx):
        for en_member in SpecialRoleData.EN_MEMBERS:
            for part in en_member:
                role = get(ctx.guild.roles, name=part['name'])
                if role:
                    self.roleMap[role.name] = role.id
    
    async def updateRole(self, message:Message, part):
        ctx = await self.bot.get_context(message)
        member = message.guild.get_member(message.author.id)
        roleName = part['name']
        t_role = message.guild.get_role(self.roleMap[roleName])
        if roleName in self.roleMap and not t_role in member.roles:
            await member.add_roles(t_role)
            t_rmbed = discord.Embed()
            t_rmbed.description = "恭喜<@!{}>獲得{}".format(message.author.id, part['name'])
            await message.channel.send(embed= t_rmbed)

    # To initialize special roles
    async def initializeRoles(self, ctx):
        f_msg = await ctx.channel.send("初始化特殊身分組....")
        target_guild = ctx.guild
        for en_member in SpecialRoleData.EN_MEMBERS:
            for part in en_member:
                part_name = part['name']
                f_msg.edit(content= str(f_msg.content)+"\n建立{}身份組".format(part_name))
                role = get(ctx.guild.roles, name=part_name)
                if role:
                    self.roleMap[role.name] = role.id
                    await f_msg.edit(content= str(f_msg.content)+"\n{}已經存在... 合併現有資料".format(part_name))
                else:
                    await f_msg.edit(content= str(f_msg.content)+'\n創建身分組{} ....'.format(part_name))
                    new_role = await target_guild.create_role(name=part_name , permissions=discord.Permissions(permissions=0) ,colour= discord.Color(part['color']), mentionable= False, hoist=False)
                    roles[new_role.name] = new_role.id
        await ctx.channel.send("特殊身分組初始化完成。")

    @commands.Cog.listener('on_role_delete')
    async def special_collect_on_role_delete(self, message:Message):
        #TODO:if special roles being delet, recreate!
        pass

    @commands.Cog.listener('on_guild_join')
    async def special_on_ready(self, guild:Guild):
        self.syncRoles(guild)

    @commands.Cog.listener('on_message')
    async def special_collect_on_message(self, message:Message):
        ctx = await self.bot.get_context(message)
        if ctx.command == None and ctx.author.id != self.bot.user.id:
            if not self.initialized:
                self.syncRoles(ctx)
                self.initializeRoles = True
            if self.shouldGetRole():
                memberIndex = randrange(len(SpecialRoleData.EN_MEMBERS))
                member = SpecialRoleData.EN_MEMBERS[memberIndex]
                partIndex = randrange(len(member))
                part = member[partIndex]
                await self.updateRole(message, part)

    @commands.group(name = 'special', invoke_without_command = True)
    async def special_collect_group(self, ctx:commands.Command, *attr):
        #TODO:print special collect eqiment state
        pass

    @special_collect_group.command(name = 'test')
    async def special_collect_test(self, ctx:commands.Command, *argv):
        await ctx.channel.send("Hello world!")
    
    @special_collect_group.command(name = 'init_roles')
    async def special_collect_init(self, ctx:commands.Command, *argv):
        await self.initializeRoles(ctx)

    #TODO: design something special that shown user they got the special roles
    #Note: for inas roles, can upload some voice cut for user
        


def setup(client):
    client.add_cog(RoleSelectSpecial(client))
