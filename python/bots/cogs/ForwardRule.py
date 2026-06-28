import asyncio
import io

import aiohttp
import discord
from common.DiscordUtil import DiscordUtil
from common.ForwardUtil import ForwardUtil
from common.models.Forward import Forward
from discord import File, Guild, Message, app_commands
from discord.ext import commands


class ForwardRule(commands.GroupCog, group_name='轉發', group_description='跨頻道消息轉發設定'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener('on_message')
    async def forward_rule_on_message(self, message: Message) -> None:
        if message.author.bot:
            return
        forward_rules = ForwardUtil.get_forward(message.guild.id, message.channel.id)
        if len(forward_rules) > 0:
            forward: Forward
            should_delete = False
            for forward in forward_rules:
                channel = await DiscordUtil.fetch_text_channel(
                    self.bot, forward.receive_channel_id
                )
                if channel:
                    files = await self.getFiles(message)
                    await channel.send(content=message.content, files=files)
                    should_delete |= forward.delete_original
            if should_delete:
                await message.delete()
                thanks_msg = await message.channel.send("非常感謝你的投訴, 我們會即刻處理")
                await asyncio.sleep(3)
                await thanks_msg.delete()

    async def getFiles(self, message: Message) -> list[File]:
        result = []
        for attachment in message.attachments:
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status != 200:
                        continue
                    data = io.BytesIO(await resp.read())
                    result.append(File(data, attachment.filename))
        return result

    @app_commands.command(name='發送設定', description='設置要監聽的頻道並取得接收設定說明')
    @app_commands.describe(delete_original='轉發後是否刪除原始訊息')
    @app_commands.guild_only()
    async def set_send(
        self, interaction: discord.Interaction, delete_original: bool = True
    ) -> None:
        guild_id = interaction.guild.id
        channel_id = interaction.channel.id
        msg = "請在接收的頻道裡使用 `/轉發 接收設定` 指令:\n"
        msg += f"- 發送伺服器 ID: `{guild_id}`\n"
        msg += f"- 發送頻道 ID: `{channel_id}`\n"
        msg += f"- 刪除原始訊息: `{delete_original}`"
        await interaction.response.send_message(msg)

    @app_commands.command(name='接收設定', description='設置接收轉發訊息的頻道')
    @app_commands.describe(
        send_guild_id='發送訊息的伺服器 ID',
        send_channel_id='發送訊息的頻道 ID',
        delete_original='轉發後是否刪除原始訊息',
    )
    @app_commands.guild_only()
    async def set_receive(
        self,
        interaction: discord.Interaction,
        send_guild_id: int,
        send_channel_id: int,
        delete_original: bool,
    ) -> None:
        if send_guild_id != interaction.guild.id:
            await interaction.response.send_message("目前不支持跨服務器復誦")
            return
        sendChannel = await DiscordUtil.fetch_text_channel(self.bot, send_channel_id)
        if ForwardUtil.create_forward(
            send_guild_id,
            send_channel_id,
            interaction.guild.id,
            interaction.channel.id,
            delete_original,
        ):
            await interaction.response.send_message(
                f"從{sendChannel.name}轉至{interaction.channel.name}的復誦建立完成"
            )
        else:
            await interaction.response.send_message("復誦建立失敗")

    @app_commands.command(name='列表', description='顯示目前已有的轉發規則')
    @app_commands.guild_only()
    async def list_forwards(self, interaction: discord.Interaction) -> None:
        forward_list = ForwardUtil.get_all_forward()
        forward: Forward
        msg = "```"
        if len(forward_list) > 0:
            for forward in forward_list:
                send_channel = await DiscordUtil.fetch_text_channel(
                    self.bot, forward.send_channel_id
                )
                receive_channel = await DiscordUtil.fetch_text_channel(
                    self.bot, forward.receive_channel_id
                )
                guild = send_channel.guild if send_channel else None
                msg += "復誦規則:\n"
                msg += (
                    f"{forward.id}, 從{guild.name if guild else forward.send_guild_id}群 "
                    f"{send_channel.name if send_channel else forward.send_channel_id}頻道 "
                    f"復誦到{receive_channel.name if receive_channel else forward.receive_channel_id}, "
                    f"刪除原留言: {forward.delete_original}\n"
                )
        else:
            msg += "目前沒有任何復誦規則, 請使用 `/轉發` 查詢設置方法"
        msg += "```"
        await interaction.response.send_message(msg)

    @app_commands.command(name='刪除', description='刪除指定的轉發規則')
    @app_commands.describe(forward_id='要刪除的轉發規則 ID')
    @app_commands.guild_only()
    async def delete_forward(
        self, interaction: discord.Interaction, forward_id: int
    ) -> None:
        ForwardUtil.delete(forward_id)
        await interaction.response.send_message(f"成功移除復誦規則`{forward_id}`")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ForwardRule(bot))