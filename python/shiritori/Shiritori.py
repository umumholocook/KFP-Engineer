import discord
import os
from discord.ext import commands

TOKEN=os.environ['KFP_SHIRITORI_TOKEN']
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix = '!',intents = intents)
gameStarted = False

@bot.event
async def on_ready():
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))
    print('Shiritori Ready!!')

@bot.command(name = 'invite_link',invoke_without_command = True)
async def command_invite_link(ctx, *attr):
    link = "https://discordapp.com/oauth2/authorize?&client_id={}&scope=bot&permissions={}".format(bot.user.id, 8192)
    await ctx.send(link)

@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    if ctx.command != None:
        await bot.process_commands(message)

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

bot.load_extension('cogs.Game')
bot.run(TOKEN)
