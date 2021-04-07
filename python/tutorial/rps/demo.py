from discord.ext import commands
from random import choice

bd = commands.Bot(command_prefix="!")

@bd.event
async def on_ready():
    print("Bot is ready")

@bd.event
async def on_message(message):
    print(f"收到消息 {message.author}: {message.content}") if message.author.id != bd.user.id else None
    await bd.process_commands(message)

@bd.command(name = 'rps', invoke_without_command = True)
async def hit_bd(ctx, *attr):
    print(f"收到指令, 指令為{attr}")
    if len(attr) > 1:
        await ctx.channel.send("你不要來亂啦!!")
    if len(attr) < 0:
        await ctx.channel.send("你不要來亂啦!!")
    await rpsGame(ctx, attr[0])

rps = ['剪刀', '石頭', '布']
correct_value = [None, 'r', 'p', 's']

async def rpsGame(ctx:commands.Context, user_choice:str=None):
    if not user_choice in correct_value:
        await ctx.channel.send(f"錯誤指令{user_choice} 你不要來亂啦!!")
        return
    user_choice_chinese: str
    if user_choice == None:
        user_choice_chinese = choice(rps)
    elif user_choice.lower() == 's':
        user_choice_chinese = '剪刀'
    elif user_choice.lower() == 'r':
        user_choice_chinese = '石頭'
    elif user_choice.lower() == 'p':
        user_choice_chinese = '布'
    bot_choice = choice(rps)
    await whoWin(ctx, bot_choice, user_choice_chinese)

async def whoWin(ctx:commands.Context, bot:str, user:str):
    bot_command = rps.index(bot) # 0, 1, 2
    user_command = rps.index(user)
    if bot_command == user_command:
        await ctx.channel.send(f"你出{user}, 我出{bot} 平手！！")
        return
    if bot_command == 0:
        if user_command == 1:
            await ctx.channel.send(f"你出{user}, 我出{bot} 你贏了！！")
            return
        if user_command == 2:
            await ctx.channel.send(f"你出{user}, 我出{bot} 你輸了！！")
            return
    if bot_command == 1:
        if user_command == 2:
            await ctx.channel.send(f"你出{user}, 我出{bot} 你贏了！！")
            return
        if user_command == 0:
            await ctx.channel.send(f"你出{user}, 我出{bot} 你輸了！！")
            return
    if bot_command == 2:
        if user_command == 0:
            await ctx.channel.send(f"你出{user}, 我出{bot} 你贏了！！")
            return
        if user_command == 1:
            await ctx.channel.send(f"你出{user}, 我出{bot} 你輸了！！")
            return

print("starting bot...")
bd.run("ODI1MDExNjE1MDY5MzcyNDM2.YF3t8Q.kl4jQEq7oXcn1229rA91nTNzLgw")
