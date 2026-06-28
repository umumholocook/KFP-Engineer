import discord

from common.RockPaperScissorsUtil import RockPaperScissorsUtil
from common.MemberUtil import MemberUtil
from random import choice
from discord.app_commands import Choice
from discord.ext import commands
from discord import app_commands


class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    rps = ['剪刀', '石頭', '布']
    correct_value = ["random", '剪刀', '石頭', '布', 'r', 'p', 's', 'rock', 'paper', 'scissor', ""]

    @app_commands.command(name='猜拳', description="快樂地來一場猜拳吧")
    @app_commands.describe(type="拳型")
    @app_commands.choices(type=[
        Choice(name="剪刀", value="scissor"),
        Choice(name="石頭", value="rock"),
        Choice(name="布", value="paper"),
        Choice(name="隨便", value="random"),
    ])
    @app_commands.checks.cooldown(1, 5.0)
    async def start_game(self, interaction: discord.Interaction, type: str = "random"):
        await self._rpsGame(interaction, type)

    @app_commands.command(name='猜拳說明', description="KFP猜拳bot指令說明")
    async def print_help(self, interaction: discord.Interaction):
        helptext = "```"
        helptext += "KFP猜拳bot, 你可以使用下面的指令\n"
        helptext += "/猜拳 石頭 - 我出石頭\n"
        helptext += "/猜拳 布 - 我出布\n"
        helptext += "/猜拳 剪刀 - 我出剪刀\n"
        helptext += "/猜拳 隨便 - 幫我出拳\n"
        helptext += "```"
        await interaction.response.send_message(helptext)

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            msg = RockPaperScissorsUtil.getTooFastDialog().format(error.retry_after)
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        else:
            raise error

    async def _rpsGame(self, interaction: discord.Interaction, user_choice: str = None):
        bot_choice = choice(self.rps)

        if user_choice not in self.correct_value:
            await interaction.response.send_message(f'輸入的指令 "{user_choice}" 不正確, 請重新輸入')
            return

        if user_choice == "random" or user_choice == "":
            user_choice_chinese = choice(self.rps)
            await interaction.response.send_message(f"用戶沒有提供猜拳類型, 隨機選擇:{user_choice_chinese}")
        else:
            await interaction.response.defer()
            if user_choice.lower() in ('s', 'scissor') or user_choice == '剪刀':
                user_choice_chinese = '剪刀'
            elif user_choice.lower() in ('r', 'rock') or user_choice == '石頭':
                user_choice_chinese = '石頭'
            elif user_choice.lower() in ('p', 'paper') or user_choice == '布':
                user_choice_chinese = '布'
            else:
                await interaction.followup.send(f'輸入的指令 "{user_choice}" 不正確, 請重新輸入')
                return

        result = self.whoWin(bot_choice, user_choice_chinese)
        if result == 1:
            await interaction.followup.send(f'{interaction.user.mention} 你出 {user_choice_chinese} , 我出的是 {bot_choice}.\n{RockPaperScissorsUtil.getBotWinDialog()}')
        elif result == -1:
            await interaction.followup.send(f'{interaction.user.mention} 你出 {user_choice_chinese} , 我出的是 {bot_choice}.\n{RockPaperScissorsUtil.getBotLossDialog()}')
            await self.addToken(interaction)
        else:
            await interaction.followup.send(f'{interaction.user.mention} 你出 {user_choice_chinese} , 我出的也是 {bot_choice}.\n{RockPaperScissorsUtil.getTieDialog()}')

    async def addToken(self, interaction: discord.Interaction):
        MemberUtil.add_token(interaction.user.id, 1)
        member = MemberUtil.get_member(interaction.user.id)
        await interaction.followup.send(f'恭喜{interaction.user.mention}獲得1隻🍗, 目前擁有{member.token}隻🍗')

    def whoWin(self, left: str, right: str) -> int:
        left_index = self.rps.index(left)
        right_index = self.rps.index(right)
        if left_index == right_index:
            return 0
        if left_index == 2:
            if right_index == 0:
                return -1
            if right_index == 1:
                return 1
        if left_index == 1:
            if right_index == 0:
                return 1
            if right_index == 2:
                return -1
        if left_index == 0:
            if right_index == 1:
                return -1
            if right_index == 2:
                return 1
        return 0


async def setup(bot):
    await bot.add_cog(RockPaperScissors(bot))