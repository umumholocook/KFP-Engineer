import discord
from discord import app_commands
from discord.ext import commands

from common.ChannelUtil import ChannelUtil
from common.Util import Util


@app_commands.guild_only()
class CommandControl(commands.GroupCog, group_name="指令控制", group_description="設定可以使用指令的頻道"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return not interaction.user.bot

    @app_commands.command(name="說明", description="指令控制使用方法")
    async def command_control_help(self, interaction: discord.Interaction) -> None:
        message = "指令控制能設定可以使用指令的頻道(以執行指令的頻道為準)\n"
        message += "```"
        message += "/指令控制 指令列表 - 顯示可以控制的指令\n"
        message += "/指令控制 新增 <command type> - 設定可以使用<command type>指令的頻道\n"
        message += "/指令控制 移除 <command type> - 移除可以使用<command type>指令的頻道\n"
        message += "/指令控制 列表 <command type> - 顯示可以使用<command type>指令的頻道\n"
        message += "```"
        await interaction.response.send_message(message)

    def __has_command__(self, command: str) -> bool:
        return command.upper() in Util.ChannelType.__members__

    @app_commands.command(name="新增", description="設定可以使用指定指令的頻道")
    @app_commands.describe(command="指令類型")
    async def command_control_add(self, interaction: discord.Interaction, command: str) -> None:
        if not self.__has_command__(command):
            await interaction.response.send_message(f"指令{command}錯誤, 請檢查拼寫是否正確.")
            return

        command_enum = Util.ChannelType[command.upper()]
        ChannelUtil.addChannel(interaction.guild.id, interaction.channel.id, command_enum)
        print(f"Adding channel {interaction.channel.id} to type {command_enum.name} succeed!")
        await interaction.response.send_message(
            f"已將此頻道加入指令 '{command_enum.name}' 的可執行頻道清單.",
            ephemeral=True,
        )

    @app_commands.command(name="移除", description="移除可以使用指定指令的頻道")
    @app_commands.describe(command="指令類型")
    async def command_control_remove(self, interaction: discord.Interaction, command: str) -> None:
        if not self.__has_command__(command):
            await interaction.response.send_message(f"指令{command}錯誤, 請檢查拼寫是否正確.")
            return

        command_enum = Util.ChannelType[command.upper()]
        result = ChannelUtil.removeChannel(interaction.guild.id, interaction.channel.id, command_enum)
        if result:
            print(f"Success!: remove channel {interaction.channel.name} for '{command_enum.name}'.")
            await interaction.response.send_message(
                f"已將此頻道從指令 '{command_enum.name}' 的可執行頻道清單移除.",
                ephemeral=True,
            )
        else:
            print(f"FAILED!!: cannot remove channel {interaction.channel.name} for command '{command_enum.name}'.")
            await interaction.response.send_message(
                f"此頻道不在指令 '{command_enum.name}' 的可執行頻道清單中.",
                ephemeral=True,
            )

    @app_commands.command(name="列表", description="顯示可以使用指定指令的頻道")
    @app_commands.describe(command="指令類型")
    async def command_control_list(self, interaction: discord.Interaction, command: str) -> None:
        if not self.__has_command__(command):
            await interaction.response.send_message(f"指令{command}錯誤, 請檢查拼寫是否正確.")
            return

        command_enum = Util.ChannelType[command.upper()]
        channels = ChannelUtil.GetChannelWithGuild(interaction.guild.id, command_enum)
        if len(channels) < 1:
            await interaction.response.send_message(f"指令'{command}'沒有設定任何的可執行頻道.")
            return

        result = f"目前指令'{command}'可以在以下頻道執行:\n"
        result += "```"
        for channel in channels:
            discord_channel = await DiscordUtil.fetch_text_channel(
                self.bot, channel.channel_id
            )
            if discord_channel:
                result += f"{discord_channel.name}\n"
        result += "```"
        await interaction.response.send_message(result)

    @app_commands.command(name="指令列表", description="顯示可以控制的指令")
    async def command_control_commands(self, interaction: discord.Interaction) -> None:
        commands_list = ["profile", "bank"]
        result = "目前可以控制的指令為:\n"
        for command in commands_list:
            result += f"\t{command}\n"
        await interaction.response.send_message(result)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(CommandControl(client))