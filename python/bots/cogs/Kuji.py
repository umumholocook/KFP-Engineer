import asyncio
import discord
import random
from common.MemberUtil import MemberUtil
from common.KujiUtil import KujiUtil
from common.KujiObj import KujiObj
from datetime import datetime
from discord import app_commands, File
from discord.ext import commands
from discord.app_commands import Choice
from resource.data.lungshan import LUNGSHAN
from resource.data.omikuji import OMIKUJI
from ui.Kuji.KujiEmbed import KujiEmbed


class Kuji(commands.Cog):

    def __init__(self, client):
        self.bot = client

    __RATE = 10

    @app_commands.command(name="抽籤", description="試試看今天的手氣")
    @app_commands.describe(type="種類")
    @app_commands.choices(type=[
        Choice(name="日本淺草觀音寺籤", value="jp"),
        Choice(name="易經64籤", value="cn"),
        Choice(name="龍山寺觀音籤", value="ls"),
        Choice(name="搖一下籤筒", value="shake"),
        Choice(name="查看過去紀錄", value="history"),
    ])
    async def slash_kuji(self, interaction: discord.Interaction, type: str):
        if type == "jp":
            await self.tryJp(interaction)
        elif type == "ls":
            await self.tryLs(interaction)
        elif type == "cn":
            await self.tryCn(interaction)
        elif type == "shake":
            await self.shake(interaction)
        elif type == "history":
            await self.checkHistory(interaction)

    async def tryJp(self, interaction: discord.Interaction):
        if not KujiUtil.canDrawJp(interaction.user.id):
            await interaction.response.send_message("親愛的員工, 你今天已經抽過清水寺籤了哦! 每人一天只限一次.")
            return
        if not await self.checkToken(interaction):
            return
        random.seed(random.random())
        index = random.randint(0, 98)
        kuji = OMIKUJI[index]
        imagePath = KujiUtil.generageImageForJp(KujiObj(kuji))
        img = File(imagePath, filename=KujiUtil.getKujiImageName())
        await interaction.followup.send(file=img, embed=KujiEmbed.createEmbededJp(kuji, datetime.now(), f"{self.bot.user.name} - 抽籤遊戲"))
        KujiUtil.updateMemberJp(interaction.user.id, index)

    async def tryLs(self, interaction: discord.Interaction):
        if not KujiUtil.canDrawLs(interaction.user.id):
            await interaction.response.send_message("親愛的員工, 你今天已經抽過龍山寺籤了哦! 每人一天只限一次.")
            return
        if not await self.checkToken(interaction):
            return
        random.seed(random.random())
        index = random.randint(0, 98)
        ls = LUNGSHAN[index]
        status = ls["status"]
        img = File(KujiUtil.getImageUrlLs(status), filename=KujiUtil.getImageNameLs(status))
        await interaction.followup.send(file=img, embed=KujiEmbed.createEmbededLs(ls, datetime.now(), f"{self.bot.user.name} - 抽籤遊戲"))
        KujiUtil.updateMemberLs(interaction.user.id, index)

    async def tryCn(self, interaction: discord.Interaction):
        if not KujiUtil.canDrawCn(interaction.user.id):
            await interaction.response.send_message("親愛的員工, 你今天已經抽過易經了哦! 每人一天只限一次.")
            return
        if not await self.checkToken(interaction):
            return
        random.seed(random.random())
        yiIndex = KujiUtil.getYi()
        yi = KujiUtil.getTargetedYi(yiIndex[0], yiIndex[1])
        await interaction.followup.send(embed=KujiEmbed.createEmbededCn(yi, datetime.now(), f"{self.bot.user.name} - 抽籤遊戲"))
        KujiUtil.updateMemberCn(interaction.user.id, yiIndex[0], yiIndex[1])

    async def checkHistory(self, interaction: discord.Interaction):
        historyJp = KujiUtil.getHistoryJp(interaction.user.id)
        historyCn = KujiUtil.getHistoryCn(interaction.user.id)
        historyLs = KujiUtil.getHistoryLs(interaction.user.id)

        if (-1, None) == historyJp and (-1, None) == historyLs and (-1, -1, None) == historyCn:
            await interaction.response.send_message("親愛的員工, 你今天還沒抽過籤呢! 先試著抽一個看看？.")
            return
        await interaction.response.defer()
        if not (-1, None) == historyLs:
            ls = LUNGSHAN[historyLs[0]]
            status = ls["status"]
            img = File(KujiUtil.getImageUrlLs(status), filename=KujiUtil.getImageNameLs(status))
            await interaction.followup.send(file=img, embed=KujiEmbed.createEmbededLs(ls, datetime.now(), f"{self.bot.user.name} - 抽籤遊戲"))

        if not (-1, None) == historyJp:
            kuji = OMIKUJI[historyJp[0]]
            imagePath = KujiUtil.generageImageForJp(KujiObj(kuji))
            img = File(imagePath, filename=KujiUtil.getKujiImageName())
            await interaction.followup.send(file=img, embed=KujiEmbed.createEmbededJp(kuji, historyJp[1], f"{self.bot.user.name} - 抽籤遊戲"))

        if not (-1, -1, None) == historyCn:
            yi = KujiUtil.getTargetedYi(historyCn[0], historyCn[1])
            await interaction.followup.send(embed=KujiEmbed.createEmbededCn(yi, historyCn[2], f"{self.bot.user.name} - 抽籤遊戲"))

    async def shake(self, interaction: discord.Interaction):
        random.seed(random.random())
        await interaction.response.defer()
        msg = await interaction.followup.send("搖...", wait=True)
        await asyncio.sleep(2)
        random.seed(random.random())
        await msg.edit(content="搖... 搖...")
        await asyncio.sleep(2)
        random.seed(random.random())
        await msg.edit(content="搖... 搖... 搖...")
        await asyncio.sleep(2)
        await msg.edit(content="搖好了")

    @app_commands.command(name="清除紀錄", description="清除所有抽籤紀錄（管理員）")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def clear_kuji_record(self, interaction: discord.Interaction) -> None:
        KujiUtil.clearData()
        await interaction.response.send_message("已清除所有抽籤紀錄。", ephemeral=True)

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            msg = f"出現錯誤: {error}\n你沒有足夠的權限使用這個功能"
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        else:
            raise error

    async def checkToken(self, interaction: discord.Interaction) -> bool:
        member = MemberUtil.get_or_add_member(interaction.user.id)
        if member.token < self.__RATE:
            await interaction.response.send_message(f"親愛的員工, 你的雞腿不夠不能抽籤哦! 你只有 {member.token}隻.")
            return False
        await interaction.response.defer()
        MemberUtil.add_token(member.member_id, -1 * self.__RATE)
        remaining = member.token - self.__RATE
        await interaction.followup.send(f"抽籤遊戲花費 {self.__RATE}隻雞腿, 你還剩下 {remaining}隻.")
        return True


async def setup(client):
    await client.add_cog(Kuji(client))