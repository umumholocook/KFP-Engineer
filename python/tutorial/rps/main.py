import os, discord
from discord.ext import commands
from random import choice

TOKEN=os.environ['KFP_TOKEN']

intents = discord.Intents.default() # 描述bot本身是想要收到什麼樣的資訊
intents.members = True
bot = commands.Bot(command_prefix = '!',intents = intents)

@bot.event
async def on_ready():
    print('Bot is ready')

@bot.event
async def on_message(message):
    print('on_message get message from {0.author} : {0.content}'.format(message)) if message.author.id != bot.user.id else None
    ctx = await bot.get_context(message)
    if ctx.command != None:
        await bot.process_commands(message)

@bot.command(name = 'rps',invoke_without_command = True)
async def command_get_version(ctx, *attr):
    if len(attr) < 1:
        await _rpsGame(ctx)
    else:
        await _rpsGame(ctx, attr[0])

rps = ['剪刀', '石頭', '布']
correct_value = [None, '剪刀', '石頭', '布', 'r', 'p', 's', 'rock', 'paper', 'scissor']

async def _rpsGame(ctx:commands.Context, user_choice:str=None):
        bot_choice = choice(rps)
        user_choice_chinese: str
        if not user_choice in correct_value:
            await ctx.send(f"輸入的指令 \"{user_choice}\" 不正確, 請重新輸入")
        if user_choice == None:
            user_choice_chinese = choice(rps)
            await ctx.send(f"用戶沒有提供猜拳類型, 隨機選擇:{user_choice_chinese}")
        elif user_choice.lower() == 's' or user_choice.lower() == 'scissor' or user_choice == '剪刀':
            user_choice_chinese = '剪刀'
        elif user_choice.lower() == 'r' or user_choice.lower() == 'rock' or user_choice == '石頭':
            user_choice_chinese = '石頭'
        elif user_choice.lower() == 'p' or user_choice.lower() == 'paper' or user_choice == '布':
            user_choice_chinese = '布'
        
        result = whoWin(bot_choice, user_choice_chinese)
        if result == 1:
            await ctx.send(f'{ctx.author.mention} 你出 {user_choice_chinese} , 我出的是 {bot_choice}.\n 我贏了')
        elif result == -1:
            await ctx.send(f'{ctx.author.mention} 你出 {user_choice_chinese} , 我出的是 {bot_choice}.\n 你贏了')
        else:
            await ctx.send(f'{ctx.author.mention} 你出 {user_choice_chinese} , 我出的也是 {bot_choice}.\n 平手！')

def whoWin(left:str, right:str) -> int:
    left_index = rps.index(left)
    right_index = rps.index(right)
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

print("Stariting bot... ")
bot.run(TOKEN)