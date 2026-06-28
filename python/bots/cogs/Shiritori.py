import discord
from datetime import datetime
from discord import app_commands
from discord.ext import commands, tasks
from common.DiscordUtil import DiscordUtil
from common.ShiritoriStringUtil import ShiritoriStringUtil


class Shiritori(commands.GroupCog, group_name="文字接龍", group_description="中文文字接龍遊戲"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.word_count = 20
        self.game_started = False
        self.countdown_time = datetime.now()
        self.countdown_wait_time = 20
        self.channel_id = 0
        self.second_remained = 5
        self.countdown_msg = None
        self.history: list[str] = []

    @app_commands.command(name="說明", description="文字接龍指令說明")
    async def help_cmd(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "```"
            "/文字接龍 開始 [字數上限] - 開始遊戲，字數上限預設 20\n"
            "/文字接龍 停止 - 停止遊戲\n"
            "/文字接龍 紀錄 - 顯示上一回的接龍結果\n"
            "/文字接龍 顯示設定 - 查看目前設定\n"
            "/文字接龍 設定字數 - 調整單次發言字數上限\n"
            "/文字接龍 設定等待 - 調整無人接龍時的等待秒數\n"
            "```"
        )

    @app_commands.command(name="開始", description="開始文字接龍")
    @app_commands.describe(字數上限="單次發言字數上限（2–50，預設使用目前設定）")
    async def start(self, interaction: discord.Interaction, 字數上限: app_commands.Range[int, 2, 50] = None):
        if self.game_started:
            await interaction.response.send_message("遊戲已經在進行中。", ephemeral=True)
            return

        self.history.clear()
        if 字數上限 is not None:
            self.word_count = 字數上限

        self.game_started = True
        self.channel_id = interaction.channel.id
        self.countdown_time = datetime.now()
        self.reset_countdown()

        if not self.clock.is_running():
            self.clock.start()

        await interaction.response.send_message(
            f"遊戲開始！字數限制是 {self.word_count} 個字。誰先起個頭？"
        )

    @app_commands.command(name="停止", description="停止文字接龍")
    async def stop(self, interaction: discord.Interaction):
        if not self.game_started:
            await interaction.response.send_message("目前沒有進行中的遊戲。", ephemeral=True)
            return
        await interaction.response.send_message("遊戲結束！")
        await self.stop_game()

    @app_commands.command(name="紀錄", description="顯示上一回的接龍結果")
    async def history(self, interaction: discord.Interaction):
        if not self.history:
            await interaction.response.send_message("還沒有任何接龍紀錄。", ephemeral=True)
            return

        await interaction.response.defer()
        history_parts = ShiritoriStringUtil.split_history_message(
            ShiritoriStringUtil.to_history_string(self.history)
        )
        for i, part in enumerate(history_parts):
            header = (
                f"哭哦，玩這麼久，結果({i + 1}/{len(history_parts)}):\n"
                if len(history_parts) > 1
                else "剛剛大家的接龍結果是:\n"
            )
            await interaction.followup.send(f"{header}```{part}```")

    @app_commands.command(name="顯示設定", description="查看文字接龍設定")
    async def show_settings(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "```"
            f"KFP 文字接龍設定\n"
            f"最高字數限制: {self.word_count}\n"
            f"bot 等待時間: {self.countdown_wait_time} 秒\n"
            "```"
        )

    @app_commands.command(name="設定字數", description="設定單次發言字數上限")
    @app_commands.describe(字數上限="2 以上")
    async def set_word_count(self, interaction: discord.Interaction, 字數上限: app_commands.Range[int, 2, 50]):
        self.word_count = 字數上限
        await interaction.response.send_message(f"最高字數限制設為: {self.word_count}")

    @app_commands.command(name="設定等待", description="設定無人接龍時 bot 等待秒數")
    @app_commands.describe(等待秒數="6 秒以上")
    async def set_wait_time(self, interaction: discord.Interaction, 等待秒數: app_commands.Range[int, 6, 120]):
        self.countdown_wait_time = 等待秒數
        await interaction.response.send_message(f"bot 等待時間設為: {self.countdown_wait_time} 秒")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not self.game_started:
            return
        if message.channel.id != self.channel_id:
            return

        self.reset_countdown()
        await self.parse_message(message)

    async def parse_message(self, message: discord.Message):
        text = ShiritoriStringUtil.remove_stickers(
            ShiritoriStringUtil.remove_emoji(message.content)
        )

        if len(text) < 2:
            await message.reply("字數太少啦")
            return
        if len(text) > self.word_count:
            await message.reply(f"超過字數上限 {self.word_count}，請重新輸入")
            return
        if self.history and not ShiritoriStringUtil.match_the_last_word(self.history, text):
            await message.reply(
                f"哎，同學，上一個人說「{self.history[-1]}」，麻煩你接「{self.history[-1][-1]}」哦"
            )
            return
        if text in self.history:
            await message.reply("這個之前有人說過啦，你換一個")
            return

        self.history.append(text)
        if len(self.history) == 1:
            await message.channel.send(f"一開始是 {text}，下一個人請接: {text[-1]}")
        else:
            await message.channel.send(f"下一個人請接: {text[-1]}")

    def reset_countdown(self):
        self.countdown_time = datetime.now()
        self.countdown_msg = None
        self.second_remained = 5

    async def stop_game(self):
        self.game_started = False
        if self.clock.is_running():
            self.clock.cancel()

        channel_id = self.channel_id
        self.channel_id = 0
        self.reset_countdown()

        channel = await DiscordUtil.fetch_text_channel(self.bot, channel_id)
        if channel and len(self.history) < 1:
            await channel.send("哭哦，居然沒有人要玩")

    @tasks.loop(seconds=1)
    async def clock(self):
        if not self.game_started or self.channel_id == 0:
            return

        channel = await DiscordUtil.fetch_text_channel(self.bot, self.channel_id)
        if not channel:
            return

        elapsed = (datetime.now() - self.countdown_time).total_seconds()
        if elapsed > self.countdown_wait_time:
            await channel.send("遊戲結束！")
            await self.stop_game()
            return

        if elapsed > (self.countdown_wait_time - 5):
            if not self.countdown_msg:
                self.countdown_msg = await channel.send(f"...{self.second_remained} ")
            else:
                await self.countdown_msg.edit(
                    content=f"{self.countdown_msg.content}...{self.second_remained} "
                )
            self.second_remained -= 1

    @clock.before_loop
    async def before_clock(self):
        await self.bot.wait_until_ready()

    async def cog_unload(self):
        if self.clock.is_running():
            self.clock.cancel()


async def setup(bot: commands.Bot):
    await bot.add_cog(Shiritori(bot))