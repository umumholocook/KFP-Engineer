import discord, asyncio

from discord.ext import commands
from discord import app_commands
from common.RouletteUtil import RouletteUtil

class Roulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # @app_commands.command(name = '轉盤賭場', description="一時賭博一時爽, 一直賭博一直爽")
    # async def roulette_help(self, interaction: discord.Interaction):
    #     msg  = "歡迎來到轉盤賭場, 以下是賭場使用方法:\n\n"
    #     msg += "/roulette_start 開始轉輪盤, 在40秒內可以下注哦!\n"
    #     msg += "/roulette_bet <號碼> <硬幣數量> 下注你喜歡的號碼以及所下注的硬幣數量, 可選擇的號碼有 1, 3, 5, 10, 20 \n"
    #     msg += "\t每個號碼的賠率:\n"
    #     msg += "\t\t1: 2倍"
    #     msg += "\t\t3: 4倍"
    #     msg += "\t\t5: 6倍"
    #     msg += "\t\t10: 12倍"
    #     msg += "\t\t20: 25倍"
    #     await interaction.response.send_message(msg)
        
    # @app_commands.command(name = "roulette_start")
    # async def start_roulette_game(self, interaction: discord.Integration):
    #     exist_game_channel_id = RouletteUtil.startGame()
    #     if exist_game_channel_id != None:
    #         # game exist in exist_game_channel_id
    #         for channel in interaction.guild.channels:
    #             if channel.id == exist_game_channel_id:
    #                 await interaction.response.send_message(f"現在在頻道{channel.name}正在進行遊戲呢, 趕快加入吧")
    #                 return
    #     else:
    #         await interaction.response.send_message("遊戲開始! 還有40秒的時間可以下注!!")
    #         for countDown in range(1, 39):
    #             await asyncio.sleep(1)
    #             seconds = 40 - countDown
    #             interaction.followup.send(f"遊戲開始! 還有{seconds}秒的時間可以下注!!")
    #         winning_number = RouletteUtil.generateWinningNumber()
    #         await interaction.response.send_message(f"遊戲結束, 獲勝號碼是{winning_number}, 非常感謝你的參加!")
    #         self.concludeGame(interaction, winning_number)
                
    # async def concludeGame(self, interaction: discord.Integration, winning_number: int):
    #     game_id = RouletteUtil.concludeGame(interaction.guild.id, winning_number)
    #     winners = RouletteUtil.getWinners(game_id, winning_number)
    #     for winnerBet in winners:
    #         member = interaction.guild.get_member(winnerBet.member_id)
            
async def setup(client):
    await client.add_cog(Roulette(client))        

                