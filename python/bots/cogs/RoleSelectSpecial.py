import time
from random import randrange, seed

import discord
from discord import Guild, Member, Message, Role, app_commands
from discord.ext import commands
from discord.utils import get

from data import SpecialRoleData


@app_commands.guild_only()
class RoleSelectSpecial(
    commands.GroupCog, group_name="特殊身分組", group_description="特殊身分組抽選與管理"
):
    def __init__(self, client, chance=1000):
        self.bot = client
        self.chance = chance

    def check_complete(self, member: Member):
        # TODO: check is user collect complete
        pass

    def __shouldGetRole(self):
        seed(time.time())
        if self.chance < 1:
            return True
        n = randrange(self.chance)
        return n == 42  # 「生命、宇宙以及任何事情的終極答案」 --《銀河便車指南》

    def __drawSpecialRoleForMember(self, guild: Guild, member: Member):
        member_index = randrange(len(SpecialRoleData.EN_MEMBERS))
        en_member = SpecialRoleData.EN_MEMBERS[member_index]
        part_index = randrange(len(en_member))
        part = en_member[part_index]
        role = get(guild.roles, name=part["name"])
        if not role:
            print("role {} is deleted".format(part["name"]))
            return None
        if role in member.roles:
            return None
        return role

    async def sendMessage(self, message: Message, msg: str):
        t_rmbed = discord.Embed()
        t_rmbed.description = msg
        await message.channel.send(embed=t_rmbed)

    async def giveUserSpecialRole(self, message: Message):
        if not self.__shouldGetRole():
            return
        if not isinstance(message.author, discord.Member):
            return
        member = message.author
        new_role = self.__drawSpecialRoleForMember(message.guild, member)
        if not new_role:
            return

        await member.add_roles(new_role)
        msg = "恭喜<@!{}>獲得{}".format(message.author.id, new_role.name)
        await self.sendMessage(message, msg)

    async def initializeRoles(self, interaction: discord.Interaction):
        await interaction.response.defer()
        f_msg = await interaction.followup.send("初始化特殊身分組....")
        target_guild = interaction.guild
        for en_member in SpecialRoleData.EN_MEMBERS:
            for part in en_member:
                part_name = part["name"]
                await f_msg.edit(
                    content=str(f_msg.content) + "\n建立{}身份組".format(part_name)
                )
                role = get(interaction.guild.roles, name=part_name)
                if role:
                    await f_msg.edit(
                        content=str(f_msg.content)
                        + "\n{}已經存在... 合併現有資料".format(part_name)
                    )
                else:
                    await f_msg.edit(
                        content=str(f_msg.content) + "\n創建身分組{} 完成".format(part_name)
                    )
                    await target_guild.create_role(
                        name=part_name,
                        permissions=discord.Permissions(permissions=0),
                        colour=discord.Color(part["color"]),
                        mentionable=False,
                        hoist=False,
                    )
        await interaction.followup.send("特殊身分組初始化完成。")

    @commands.Cog.listener("on_role_delete")
    async def special_collect_on_role_delete(self, message: Message):
        # TODO: if special roles being delete, recreate!
        pass

    @commands.Cog.listener("on_message")
    async def special_collect_on_message(self, message: Message):
        if message.author.bot:
            return
        await self.giveUserSpecialRole(message)

    @app_commands.command(name="初始化身分組", description="初始化特殊身分組")
    async def special_collect_init(self, interaction: discord.Interaction) -> None:
        await self.initializeRoles(interaction)


async def setup(client):
    await client.add_cog(RoleSelectSpecial(client))