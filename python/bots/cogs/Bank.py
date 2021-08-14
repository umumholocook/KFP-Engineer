from discord.abc import User
from discord.ext import commands
from common.Util import Util
from common.MemberUtil import MemberUtil
from common.ChannelUtil import ChannelUtil

# 金融系統, 以大總管為主體的操作
class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name='bank', invoke_without_command=True)
    async def bank_group(self, ctx: commands.Context):
        if ctx.author.bot:
            return
        if not ChannelUtil.hasChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.BANK):
            return
        member = MemberUtil.get_or_add_member(self.bot.user.id)
        await ctx.send(f"目前銀行有 {member.coin}枚硬幣.")
    
    @bank_group.command(name = 'add')
    async def bank_add(self, ctx: commands.Context, coins: int):
        if not ChannelUtil.hasChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.BANK):
            return
        MemberUtil.add_coin(self.bot.user.id, coins)
        bank = MemberUtil.get_member(self.bot.user.id)
        await ctx.send(f"新增 {coins}枚硬幣至銀行: 成功!\n銀行餘額: {bank.coin}")        
    
    @bank_group.command(name = 'pay')
    async def bank_pay(self, ctx: commands.Context, coins: int, user: User):
        if not ChannelUtil.hasChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.BANK):
            return
        bank = MemberUtil.get_or_add_member(self.bot.user.id)
        if coins < 1:
            await ctx.send("請不要來亂的好嗎?")
            return
        nick = ctx.guild.get_member(user.id).nick
        if bank.coin < coins:
            await ctx.send(f"銀行餘額: {bank.coin} 不足以支付 {coins} 給 {nick}")
            return
        MemberUtil.add_coin(self.bot.user.id, -1 * coins)
        MemberUtil.add_coin(user.id, coins)
        member = MemberUtil.get_member(user.id)
        message = f"金額 {coins} 付款給 {nick}成功! 雙方餘額為\n"
        message += "```"
        message += f"銀行: {bank.coin}\n"
        message += f"{nick}: {member.coin}\n"
        message += "```"

        await ctx.send(message)

def setup(client):
    client.add_cog(Bank(client))