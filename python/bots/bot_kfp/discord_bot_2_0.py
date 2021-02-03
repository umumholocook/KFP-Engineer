import discord
from discord.ext import commands
from discord.ext.commands import errors as disErros
import asyncio, os
import sys, traceback, json

TOKEN = 'ODA2MzgxODE4ODQwMzUwNzMw.YBonlw.1Razl5F24ZFZ7xDyApiJtTLnxxw'
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix = '!',intents = intents)
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print(' --  --  -- ')

@bot.event
async def on_message(message):
    print('on_message get message from {0.author} : {0.content}'.format(message)) if message.author.id != bot.user.id else None
    ctx = await bot.get_context(message)
    if ctx.command != None:
        await bot.process_commands(message)


@bot.event
async def on_command_completion(ctx):
    print('on_command_completion Command {0.name} completion'.format(ctx.command))
    #await ctx.message.delete()

@bot.command(name = 'invite_link',invoke_without_command = True)
async def command_invite_link(ctx, *attr):
    link = "https://discordapp.com/oauth2/authorize?&client_id={}&scope=bot&permissions={}".format(bot.user.id, 1543892049)
    await ctx.send(link)
    
@bot.group(name = 'cogs', invoke_without_command = True)
async def cogs_group(ctx, *attr):
    description = 'cogs:\n'
    for file in os.listdir(r'./cogs'):
        if file.endswith('.py'):
            description += '  |- {}\n'.format(file[:-3])
    await ctx.send(description)
@cogs_group.command(name = 'load')
async def cogs_load(ctx, extention):
    if ctx.author.id == bot.owner_id:
        bot.load_extension(f'cogs.{extention}')
@cogs_group.command(name = 'unload')
async def cogs_unload(ctx, extention):
    if ctx.author.id == bot.owner_id:
        bot.unload_extension(f'cogs.{extention}')
@cogs_group.command(name = 'reload')
async def cogs_reload(ctx, extention):
    if ctx.author.id == bot.owner_id:
        bot.unload_extension(f'cogs.{extention}')
        bot.load_extension(f'cogs.{extention}')
        ctx.send('reload cog {}'.format(extention))

#preload cogs
temp = 'load cogs:\n'
for file in os.listdir(r'./cogs'):
    if file.endswith('.py'):
        temp += '  |- {}\n'.format(file[:-3])
        bot.load_extension('cogs.{}'.format(file[:-3]))
print(temp)
bot.run(TOKEN)
