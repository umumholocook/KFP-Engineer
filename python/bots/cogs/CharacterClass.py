import discord
from discord import app_commands
from discord.ext import commands


# 職業
class CharacterClass(commands.GroupCog, group_name="轉職", group_description="KFP轉職所功能"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="列表", description="列出所有職業")
    async def show_jobs(self, interaction: discord.Interaction):
        await interaction.response.send_message("轉職所準備中...")

    @app_commands.command(name="需求", description="查看職業的需求")
    @app_commands.describe(job_name="職業名稱")
    async def show_job_requirement(self, interaction: discord.Interaction, job_name: str):
        await interaction.response.send_message("轉職所準備中...")

    @app_commands.command(name="申請", description="選擇職業為自己的職業")
    @app_commands.describe(job_name="職業名稱")
    async def apply_job(self, interaction: discord.Interaction, job_name: str):
        await interaction.response.send_message("轉職所準備中...")

    @app_commands.command(name="放棄", description="放棄職業")
    @app_commands.describe(job_name="職業名稱")
    async def quit_job(self, interaction: discord.Interaction, job_name: str):
        await interaction.response.send_message("轉職所準備中...")


async def setup(bot):
    await bot.add_cog(CharacterClass(bot))