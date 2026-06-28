import asyncio
import discord

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from common.RouletteUtil import RouletteUtil
from common.MemberUtil import MemberUtil


class Roulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='轉盤說明', description="一時賭博一時爽, 一直賭博一直爽")
    async def roulette_help(self, interaction: discord.Interaction):
        msg = "歡迎來到轉盤賭場, 以下是賭場使用方法:\n\n"
        msg += "/開始轉盤 開始轉輪盤, 在40秒內可以下注哦!\n"
        msg += "/轉盤下注 <號碼> <硬幣數量> 下注你喜歡的號碼以及所下注的硬幣數量, 可選擇的號碼有 1, 3, 5, 10, 20 \n"
        msg += "\t每個號碼的賠率:\n"
        msg += "\t\t1: 2倍\n"
        msg += "\t\t3: 4倍\n"
        msg += "\t\t5: 6倍\n"
        msg += "\t\t10: 12倍\n"
        msg += "\t\t20: 25倍"
        await interaction.response.send_message(msg)

    @app_commands.command(name="開始轉盤", description="開始一場40秒的轉盤遊戲")
    async def start_roulette_game(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("請在伺服器頻道中使用此指令。", ephemeral=True)
            return

        exist_game_channel_id = RouletteUtil.startGame(interaction.guild.id, interaction.channel.id)
        if exist_game_channel_id is not None:
            channel = interaction.guild.get_channel(exist_game_channel_id)
            channel_name = channel.name if channel else str(exist_game_channel_id)
            await interaction.response.send_message(f"現在在頻道{channel_name}正在進行遊戲呢, 趕快加入吧")
            return

        await interaction.response.send_message("遊戲開始! 還有40秒的時間可以下注!!")
        status_msg = await interaction.original_response()

        for seconds_left in range(39, 0, -1):
            await asyncio.sleep(1)
            await status_msg.edit(content=f"遊戲開始! 還有{seconds_left}秒的時間可以下注!!")

        winning_number = RouletteUtil.generateWinningNumber()
        await status_msg.edit(content=f"遊戲結束, 獲勝號碼是{winning_number}, 非常感謝你的參加!")
        await self.concludeGame(interaction, winning_number)

    @app_commands.command(name="轉盤下注", description="在進行中的轉盤遊戲下注")
    @app_commands.describe(number="下注號碼", amount="硬幣數量")
    @app_commands.choices(number=[
        Choice(name="1 (2倍)", value=1),
        Choice(name="3 (4倍)", value=3),
        Choice(name="5 (6倍)", value=5),
        Choice(name="10 (12倍)", value=10),
        Choice(name="20 (25倍)", value=20),
    ])
    async def roulette_bet(self, interaction: discord.Interaction, number: int, amount: int):
        if interaction.guild is None:
            await interaction.response.send_message("請在伺服器頻道中使用此指令。", ephemeral=True)
            return

        if amount < 1:
            await interaction.response.send_message("下注金額必須至少為 1 硬幣。", ephemeral=True)
            return

        member = MemberUtil.get_or_add_member(interaction.user.id)
        if member.coin < amount:
            await interaction.response.send_message(f"硬幣不足! 你目前只有 {member.coin} 硬幣。", ephemeral=True)
            return

        result = RouletteUtil.placeBet(
            interaction.guild.id,
            interaction.channel.id,
            interaction.user.id,
            number,
            amount,
        )

        if result == -1:
            await interaction.response.send_message("目前沒有進行中的轉盤遊戲，請先使用 /開始轉盤。", ephemeral=True)
            return
        if result != 0:
            channel = interaction.guild.get_channel(result)
            channel_name = channel.name if channel else str(result)
            await interaction.response.send_message(f"轉盤遊戲正在頻道 {channel_name} 進行中，請到該頻道下注。", ephemeral=True)
            return

        MemberUtil.add_coin(interaction.user.id, -amount)
        multiplier = RouletteUtil.getPayoutMultiplier(number)
        await interaction.response.send_message(
            f"{interaction.user.display_name} 已在號碼 {number} 下注 {amount} 硬幣（賠率 {multiplier} 倍）。"
        )

    async def concludeGame(self, interaction: discord.Interaction, winning_number: int):
        game_id = RouletteUtil.concludeGame(interaction.guild.id, winning_number)
        if game_id is None:
            return

        winners = RouletteUtil.getWinners(game_id, winning_number)
        if not winners:
            await interaction.followup.send("本局無人中獎，下次再試試手氣！")
            return

        multiplier = RouletteUtil.getPayoutMultiplier(winning_number)
        result_lines = []
        for winner_bet in winners:
            payout = winner_bet.amount * multiplier
            MemberUtil.add_coin(winner_bet.member_id, payout)
            member = interaction.guild.get_member(winner_bet.member_id)
            display_name = member.display_name if member else str(winner_bet.member_id)
            result_lines.append(
                f"{display_name} 下注 {winner_bet.amount} 硬幣，獲得 {payout} 硬幣！"
            )

        await interaction.followup.send(
            f"中獎名單（號碼 {winning_number}，{multiplier} 倍）：\n" + "\n".join(result_lines)
        )


async def setup(client):
    await client.add_cog(Roulette(client))