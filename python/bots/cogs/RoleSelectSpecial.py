from common import database_API
from random import seed
from random import randrange
from data import SpecialRoleData
from discord import Guild, Member, Message, Reaction, Role
from discord.ext import commands
from discord.utils import get

import discord
import json ,os
import time

class RoleSelectSpecial(commands.Cog):
    roleMap = {} # <name, id> pair

    def __init__(self, client, chance=1000):
        self.bot = client
        self.chance = chance

    def check_complete(self,member:Member):
        #TODO:check is user collect complete
        pass
    
    # 決定是否抽中特殊身份組, 如果要測試 把self.chance 設為0 
    def __shouldGetRole(self):
        seed(time.time())
        if (self.chance < 1):
            return True
        n = randrange(self.chance)
        return n == 42 # 「生命、宇宙以及任何事情的終極答案」 --《銀河便車指南》
    
    # 從特殊身份組中選一個會員還沒有的身份組
    def __drawSpecialRoleForMember(self, guild:Guild, member:Member):
        memberIndex = randrange(len(SpecialRoleData.EN_MEMBERS))
        enMember = SpecialRoleData.EN_MEMBERS[memberIndex]
        partIndex = randrange(len(enMember))
        part = enMember[partIndex]
        if part['name'] not in self.roleMap:
            return None # 此role已被刪除
        newRole = guild.get_role(self.roleMap[part['name']])
        if not newRole in member.roles:
            return newRole
        return None # 會員已有抽到的特殊身份組, 跳過
    
    # Load existing roles into memory
    def __syncRoles(self, ctx):
        for en_member in SpecialRoleData.EN_MEMBERS:
            for part in en_member:
                role = get(ctx.guild.roles, name=part['name'])
                if role:
                    self.roleMap[role.name] = role.id
        
    async def sendMessage(self, message:Message, msg:str):
        t_rmbed = discord.Embed()
        t_rmbed.description = msg
        await message.channel.send(embed= t_rmbed)
    
    async def giveUserSpecialRole(self, ctx, message:Message):
        # 1. 決定會員是不是抽中了特殊身份組
        if not self.__shouldGetRole():
            return
        # 2. 決定特殊身份組
        member = message.guild.get_member(message.author.id)
        newRole = self.__drawSpecialRoleForMember(message.guild, member)
        if not newRole:
            return # 沒抽到
        
        # 把抽中的特殊身份組分配給會員
        await member.add_roles(newRole)
        msg = "恭喜<@!{}>獲得{}".format(message.author.id, newRole.name)
        await self.sendMessage(message, msg)

    # To initialize special roles
    async def initializeRoles(self, ctx):
        f_msg = await ctx.channel.send("初始化特殊身分組....")
        target_guild = ctx.guild
        for en_member in SpecialRoleData.EN_MEMBERS:
            for part in en_member:
                part_name = part['name']
                await f_msg.edit(content= str(f_msg.content)+"\n建立{}身份組".format(part_name))
                role = get(ctx.guild.roles, name=part_name)
                if role:
                    self.roleMap[role.name] = role.id
                    await f_msg.edit(content= str(f_msg.content)+"\n{}已經存在... 合併現有資料".format(part_name))
                else:
                    await f_msg.edit(content= str(f_msg.content)+'\n創建身分組{} ....'.format(part_name))
                    new_role = await target_guild.create_role(name=part_name , permissions=discord.Permissions(permissions=0) ,colour= discord.Color(part['color']), mentionable= False, hoist=False)
                    self.roleMap[new_role.name] = new_role.id
        await ctx.channel.send("特殊身分組初始化完成。")

    @commands.Cog.listener('on_role_delete')
    async def special_collect_on_role_delete(self, message:Message):
        #TODO:if special roles being delet, recreate!
        pass

    @commands.Cog.listener('on_guild_join')
    async def special_on_ready(self, guild:Guild):
        self.__syncRoles(guild)

    @commands.Cog.listener('on_message')
    async def special_collect_on_message(self, message:Message):
        ctx = await self.bot.get_context(message)
        if ctx.command == None and ctx.author.id != self.bot.user.id:
            await self.giveUserSpecialRole(ctx, message)    

    @commands.group(name = 'special', invoke_without_command = True)
    async def special_collect_group(self, ctx:commands.Command, *attr):
        #TODO:print special collect eqiment state
        pass
    
    @special_collect_group.command(name = 'init_roles')
    async def special_collect_init(self, ctx:commands.Command, *argv):
        await self.initializeRoles(ctx)

    #TODO: design something special that shown user they got the special roles
    #Note: for inas roles, can upload some voice cut for user
        


def setup(client):
    client.add_cog(RoleSelectSpecial(client))
