from common.models.Channel import Channel
from common.ChannelUtil import ChannelUtil
from common.Util import Util
from discord.ext import commands

class CommandControl(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='commandControl', invoke_without_command=True)
    async def command_control_group(self, ctx: commands.Context):
        message  = "指令控制(commandControl)能設定可以使用指令的頻道(以執行指令的頻道為準)\n"
        message += "```"
        message += "!commandControl commands - 顯示可以控制的指令\n"
        message += "!commandControl add <command type> - 設定可以使用<command type>指令的頻道\n"
        message += "!commandControl remove <command type> - 移除可以使用<command type>指令的頻道\n"
        message += "!commandControl list <command type> - 顯示可以使用<command type>指令的頻道\n"
        message += "```"
        await ctx.send(message)

    def __hasCommand__(self, command: str):
        return command.upper() in Util.ChannelType.__members__

    @command_control_group.command(name= 'add')
    async def command_control_add(self, ctx:commands.Context, command: str):
        if not self.__hasCommand__(command):
            await ctx.send(f"指令{command}錯誤, 請檢查拼寫是否正確.")
            return
        commandEnum = Util.ChannelType[command.upper()]
        ChannelUtil.addChannel(ctx.guild.id, ctx.channel.id, commandEnum)
        print(f"Adding channel {ctx.channel.id} to type {commandEnum.name} succeed!")

    @command_control_group.command(name= 'remove')
    async def command_control_remove(self, ctx: commands.Context, command: str):
        if not self.__hasCommand__(command):
            await ctx.send(f"指令{command}錯誤, 請檢查拼寫是否正確.")
        commandEnum = Util.ChannelType[command.upper()]
        result = ChannelUtil.removeChannel(ctx.guild.id, ctx.channel.id, commandEnum)
        if result:
            print(f"Success!: remove channel {ctx.channel.name} for '{commandEnum.name}'.")
        else:
            print(f"FAILED!!: cannot remove channel {ctx.channel.name} for command '{commandEnum.name}'.")

    @command_control_group.command(name= 'list')
    async def command_control_list(self, ctx: commands.Context, command: str):
        if not self.__hasCommand__(command):
            await ctx.send(f"指令{command}錯誤, 請檢查拼寫是否正確.")
        commandEnum = Util.ChannelType[command.upper()]
        channels = ChannelUtil.GetChannelWithGuild(ctx.guild.id, commandEnum)
        if len(channels) < 1:
            await ctx.send(f"指令'{command}'沒有設定任何的可執行頻道.")
        else:
            channel: Channel
            result  = f"目前指令'{command}'可以在以下頻道執行:\n"
            result += "````"
            for channel in channels:
                c = self.bot.get_channel(channel.channel_id)
                result += f"{c.name}\n"
            result += "````"
            await ctx.send(result)

    @command_control_group.command(name = 'commands')
    async def command_control_commands(self, ctx: commands.Context):
        commands = ['profile', 'bank']
        result = "目前可以控制的指令為:\n"
        for command in commands:
            result += f"\t{command}\n"
        await ctx.send(result)

def setup(client):
    client.add_cog(CommandControl(client))