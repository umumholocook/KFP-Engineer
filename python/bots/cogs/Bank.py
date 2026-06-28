import discord
from common.NicknameUtil import NicknameUtil
from common.InteractionUtil import InteractionUtil
from discord import User, app_commands
from discord.ext import commands
from common.Util import Util
from common.MemberUtil import MemberUtil


# 金融系統, 以大總管為主體的操作
class Bank(commands.GroupCog, group_name="銀行", group_description="銀行金融系統操作"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="餘額", description="查看目前銀行硬幣餘額")
    async def balance(self, interaction: discord.Interaction):
        if not await InteractionUtil.require_channel(interaction, Util.ChannelType.BANK):
            return
        member = MemberUtil.get_or_add_member(self.bot.user.id)
        await interaction.response.send_message(f"目前銀行有 {member.coin}枚硬幣.")

    @app_commands.command(name="存入", description="新增硬幣至銀行")
    @app_commands.describe(coins="存入的硬幣數量")
    async def bank_add(self, interaction: discord.Interaction, coins: int):
        if not await InteractionUtil.require_channel(interaction, Util.ChannelType.BANK):
            return
        MemberUtil.add_coin(self.bot.user.id, coins)
        bank = MemberUtil.get_member(self.bot.user.id)
        await interaction.response.send_message(
            f"新增 {coins}枚硬幣至銀行: 成功!\n銀行餘額: {bank.coin}"
        )

    @app_commands.command(name="付款", description="從銀行付款給指定使用者")
    @app_commands.describe(coins="付款的硬幣數量", user="收款的使用者")
    async def bank_pay(self, interaction: discord.Interaction, coins: int, user: User):
        if not await InteractionUtil.require_channel(interaction, Util.ChannelType.BANK):
            return
        bank = MemberUtil.get_or_add_member(self.bot.user.id)
        if coins < 1:
            await interaction.response.send_message("請不要來亂的好嗎?")
            return
        nick = await NicknameUtil.get_user_nickname_or_default(interaction.guild, user)
        if bank.coin < coins:
            await interaction.response.send_message(
                f"銀行餘額: {bank.coin} 不足以支付 {coins} 給 {nick}"
            )
            return
        MemberUtil.add_coin(self.bot.user.id, -1 * coins)
        MemberUtil.add_coin(user.id, coins)
        member = MemberUtil.get_member(user.id)
        message = f"金額 {coins} 付款給 {nick}成功! 雙方餘額為\n"
        message += "```"
        message += f"銀行: {bank.coin}\n"
        message += f"{nick}: {member.coin + coins}\n"
        message += "```"
        await interaction.response.send_message(message)

    @app_commands.command(name="沒收", description="沒收指定使用者的硬幣並充公至銀行")
    @app_commands.describe(coins="沒收的硬幣數量", user="被沒收的使用者")
    async def bank_remove(self, interaction: discord.Interaction, coins: int, user: User):
        if not await InteractionUtil.require_channel(interaction, Util.ChannelType.BANK):
            return
        if coins < 1:
            await interaction.response.send_message("請不要來亂的好嗎?")
            return
        member = MemberUtil.get_or_add_member(user.id)
        nick = await NicknameUtil.get_user_nickname_or_default(interaction.guild, user)
        if member.coin < coins:
            await interaction.response.send_message(
                f"'{nick}'擁有餘額: {member.coin}. 不足以扣除 {coins}"
            )
            return
        MemberUtil.add_coin(self.bot.user.id, coins)
        MemberUtil.add_coin(user.id, -1 * coins)
        bank = MemberUtil.get_or_add_member(self.bot.user.id)
        message = f"扣除'{nick}'的硬幣 '{coins}'並充公成功! 目前餘額為\n"
        message += "```"
        message += f"銀行: {bank.coin}\n"
        message += f"{nick}: {member.coin}\n"
        message += "```"
        await interaction.response.send_message(message)


async def setup(bot):
    await bot.add_cog(Bank(bot))