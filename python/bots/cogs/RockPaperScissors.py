from common.RockPaperScissorsUtil import RockPaperScissorsUtil
from common.MemberUtil import MemberUtil
from random import choice
from discord.ext import commands

class RockPaperScissors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    rps = ['剪刀', '石頭', '布']
    correct_value = [None, '剪刀', '石頭', '布', 'r', 'p', 's', 'rock', 'paper', 'scissor']

    @commands.group(name = 'rps', invoke_without_command = True)
    @commands.cooldown(1, 5, type=commands.BucketType.user)
    async def rps_game(self, ctx:commands.Context, *attr):
        print(attr)
        if len(attr) < 1:
            await self._rpsGame(ctx)
        else:
            await self._rpsGame(ctx, attr[0])

    @rps_game.error
    async def rps_error(self, ctx:commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = RockPaperScissorsUtil.getTooFastDialog().format(error.retry_after)
            await ctx.send(msg)
        else:
            raise error

    @rps_game.command(name = "help")
    async def print_help(self, ctx:commands.Command, *argv):
        helptext = "```"
        helptext+="KFP猜拳bot, 你可以使用下面的指令\n"
        helptext+="!rps r - 我出石頭\n"
        helptext+="!rps paper - 我出布\n"
        helptext+="!rps 剪刀 - 我出剪刀\n"
        helptext+="```"
        await ctx.send(helptext)

    async def _rpsGame(self, ctx:commands.Context, user_choice:str=None):
        bot_choice = choice(self.rps)
        user_choice_chinese: str
        if not user_choice in self.correct_value:
            await ctx.send(f"輸入的指令 \"{user_choice}\" 不正確, 請重新輸入")
        if user_choice == None:
            user_choice_chinese = choice(self.rps)
            await ctx.send(f"用戶沒有提供猜拳類型, 隨機選擇:{user_choice_chinese}")
        elif user_choice.lower() == 's' or user_choice.lower() == 'scissor' or user_choice == '剪刀':
            user_choice_chinese = '剪刀'
        elif user_choice.lower() == 'r' or user_choice.lower() == 'rock' or user_choice == '石頭':
            user_choice_chinese = '石頭'
        elif user_choice.lower() == 'p' or user_choice.lower() == 'paper' or user_choice == '布':
            user_choice_chinese = '布'
        
        result = self.whoWin(bot_choice, user_choice_chinese)
        if result == 1:
            await ctx.send(f'{ctx.author.mention} 你出 {user_choice_chinese} , 我出的是 {bot_choice}, 你輸了！')
        elif result == -1:
            await ctx.send(f'{ctx.author.mention} 你出 {user_choice_chinese} , 我出的是 {bot_choice}, 你贏了！')
            await self.addToken(ctx)
        else:
            await ctx.send(f'{ctx.author.mention} 你出 {user_choice_chinese} , 我出的也是 {bot_choice}, 我們平手！')
        
    async def addToken(self, ctx:commands.Context):
        MemberUtil.add_token(ctx.author.id, 1)
        member = MemberUtil.get_member(ctx.author.id)
        await ctx.send(f'恭喜{ctx.author.mention}獲得1隻🍗, 目前擁有{member.token}隻🍗')

    # if left win, return 1
    # if right win, return -1
    # if tie, return 0
    def whoWin(self, left:str, right:str) -> int:
        left_index = self.rps.index(left)
        right_index = self.rps.index(right)
        if (left_index == right_index):
            return 0
        if (left_index == 2):
            if (right_index == 0):
                return -1
            if (right_index == 1):
                return 1
        if (left_index == 1):
            if (right_index == 0):
                return 1
            if (right_index == 2):
                return -1
        if (left_index == 0):
            if (right_index == 1):
                return -1
            if (right_index == 2):
                return 1
        return 0

def setup(bot):
    bot.add_cog(RockPaperScissors(bot))
    