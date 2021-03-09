from random import choice
from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument

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
            await ctx.send(f"既然你這麼懶, 那我就幫你決定了, 你出的是 {user_choice_chinese}")
        elif user_choice.lower() == 's' or user_choice.lower() == 'scissor' or user_choice == '剪刀':
            user_choice_chinese = '剪刀'
        elif user_choice.lower() == 'r' or user_choice.lower() == 'rock' or user_choice == '石頭':
            user_choice_chinese = '石頭'
        elif user_choice.lower() == 'p' or user_choice.lower() == 'paper' or user_choice == '布':
            user_choice_chinese = '布'
        
        result = self.whoWin(bot_choice, user_choice_chinese)
        if result == 1:
            await ctx.send(f'{ctx.author.mention} 我出的是 {bot_choice}, 你輸了！')
        elif result == -1:
            await ctx.send(f'{ctx.author.mention} 我出的是 {bot_choice}, 你贏了！')
        else:
            await ctx.send(f'{ctx.author.mention} 我出的是 {bot_choice}, 平手！')
        
    # if left win, return 1
    # if right win, return -1
    # if tie, return 0
    def whoWin(self, left:str, right:str) -> int:
        left_index = self.rps.index(left)
        right_index = self.rps.index(right)
        if (left_index == right_index):
            return 0
        if (left_index == 2 and right_index == 0) or (left_index < right_index):
            return -1
        if (left_index > right_index) or (left_index == 0 and right_index == 2):
            return 1
        return 0

def setup(bot):
    bot.add_cog(RockPaperScissors(bot))
    