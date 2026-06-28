import discord
from discord.ext import commands
from discord import Embed, File, User, app_commands
from common.Util import Util
from common.RickrollGenerator import RickrollGenerator


class Rickroll(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="瑞克搖", description="產生瑞克搖 GIF")
    @app_commands.describe(user="要瑞克搖的使用者")
    @app_commands.checks.cooldown(1, 30.0)
    async def rickroll(self, interaction: discord.Interaction, user: User):
        target = interaction.user if user.bot else user
        avatar = await Util.download_user_avatar(target)
        image_path = RickrollGenerator.createGif(avatar)

        embed_msg = Embed()
        embed_msg.set_image(url="attachment://rickrolled.gif")

        img = File(image_path, filename="rickrolled.gif")
        await interaction.response.send_message(file=img, embed=embed_msg)

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            msg = "請勿過於頻繁使用本指令"
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Rickroll(bot))