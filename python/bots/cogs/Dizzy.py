import discord
from discord import File
from discord import app_commands
from common.DizzyUtil import DizzyUtil
from discord.ext import commands


class DizzyMeme(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="阿暈", description="產生阿暈迷因圖片")
    @app_commands.describe(text="要顯示的文字")
    @app_commands.checks.cooldown(1, 3.0)
    async def dizzy(self, interaction: discord.Interaction, text: str = "阿暈你好"):
        image_info = DizzyUtil.drawDizzy(text)
        temp_file_name = image_info[0]
        temp_file_path = image_info[1]
        image = File(temp_file_path, filename=temp_file_name)
        await interaction.response.send_message(file=image)

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            msg = "指令太快, 請等{:.2f}秒".format(error.retry_after)
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        else:
            raise error


async def setup(bot):
    await bot.add_cog(DizzyMeme(bot))