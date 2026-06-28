import discord
from discord import Embed, File
from common.YagooUtil import YagooUtil
from discord.ext import commands
from discord import app_commands


class YagooMeme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='最佳女孩', description="Best Girl 跟你打招呼, 最多四個字")
    @app_commands.describe(text="要顯示的文字")
    @app_commands.checks.cooldown(1, 3.0)
    async def yagoo_group(self, interaction: discord.Interaction, text: str = "早安你好"):
        imageInfo = YagooUtil.drawYagoo(text)

        tempFileName = imageInfo[0]
        tempFilePath = imageInfo[1]

        embedMsg = Embed()
        embedMsg.set_image(url='attachment://' + tempFileName)
        image = File(tempFilePath, filename=tempFileName)
        await interaction.response.send_message(file=image, embed=embedMsg)

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


async def setup(client):
    await client.add_cog(YagooMeme(client))