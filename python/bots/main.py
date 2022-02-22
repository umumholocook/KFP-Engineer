import random

from common.RPGUtil.ReviveUtil import ReviveUtil
from common.RPGUtil.StatusUpdate import StatusUpdate
from common.RPGUtil.StatusUtil import StatusUtil
import discord, os, signal, tempfile
from common.models.Channel import Channel
from pathlib import Path
from subprocess import Popen, PIPE, check_output
from discord.ext import commands, tasks
from common.KFP_DB import KfpDb
from common.ChannelUtil import ChannelUtil
from discord import Role
from common.RoleUtil import RoleUtil

VERSION = "0.6"
TOKEN=os.environ['KFP_TOKEN']
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix = '!',intents = intents)

def getTempFile():
    return Path('{}/kpf_restart'.format(tempfile.gettempdir()))

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print(' --  --  -- ')

    tmpFile = getTempFile()
    if tmpFile.exists():
        print(tmpFile)
        f = open(tmpFile, 'r')
        line = f.read().split(".")
        guild_id = int(line[0])
        pid = int(line[1])
        f.close()
        os.remove(tmpFile.absolute())
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            print(f"pid {pid} is not found. Ignore")
        else:
            print("restart successful, sending success message")
        db = KfpDb()
        channel: Channel = ChannelUtil.getRebootMessageChannel(guild_id)
        if channel:
            await bot.get_channel(channel.channel_id).send("更新結束, 現在版本 {}".format(get_version()))
    refreshStatus.start()
    reviveComaStatus.start()

@bot.event
async def on_message(message):
    print('on_message get message from {0.author} : {0.content}'.format(message)) if message.author.id != bot.user.id else None
    ctx = await bot.get_context(message)
    if message.content == "沒有暈" or message.content == "沒暈":
        await ctx.reply("我聽你放屁")
    if ctx.command != None:
        await bot.process_commands(message)

@bot.event
async def on_command_completion(ctx):
    print('on_command_completion Command {0.name} completion'.format(ctx.command))
    #await ctx.message.delete()

@bot.event
async def on_guild_role_update(before: Role, after: Role):
    RoleUtil.updateRole(before.guild.id, before.id, after.name, after.color)
    print(f"updating role with new name {after.name} and color {after.color}")

# @bot.event
# async def on_raw_raction_add(payload: RawReactionActionEvent):
#     ReactionRoleUtil.addReaction(payload)

@bot.command(name = 'invite_link',invoke_without_command = True)
async def command_invite_link(ctx, *attr):
    link = "https://discordapp.com/oauth2/authorize?&client_id={}&scope=bot&permissions={}".format(bot.user.id, 1543892049)
    await ctx.send(link)

@bot.command(name = 'update',invoke_without_command = True)
async def command_restart(ctx, *attr):
    db = KfpDb()
    ChannelUtil.setRebootMessageChannel(guild_id= ctx.guild.id, channel_id=ctx.channel.id)
    await ctx.send("現在版本 {}, 檢查更新中...".format(get_version()))
    tmpFile = getTempFile()
    tmpFile.touch()
    f = open(tmpFile, "a")
    f.write(f"{ctx.guild.id}.")
    f.write(f"{os.getpid()}")
    f.close()

    Popen([os.sep.join((os.getcwd(), "update_and_restart.sh"))], shell=True)

@bot.command(name = 'version',invoke_without_command = True)
async def command_get_version(ctx, *attr):
    await ctx.send(get_version())

@bot.group(name = 'cogs', invoke_without_command = True)
async def cogs_group(ctx, *attr):
    description = 'cogs:\n'
    for file in os.listdir(r'./cogs'):
        if file.endswith('.py'):
            description += '  |- {}\n'.format(file[:-3])
    await ctx.send(description)

@cogs_group.command(name = 'load')
@commands.is_owner()
async def cogs_load(ctx, extention):
    bot.load_extension(f'cogs.{extention}')

@cogs_group.command(name = 'unload')
@commands.is_owner()
async def cogs_unload(ctx, extention):
    bot.unload_extension(f'cogs.{extention}')

@cogs_group.command(name = 'reload')
@commands.is_owner()
async def cogs_reload(ctx, extention):
    bot.unload_extension(f'cogs.{extention}')
    bot.load_extension(f'cogs.{extention}')
    ctx.send('reload cog {}'.format(extention))

def get_version():
    git_count = check_output(['git', 'rev-list', '--all', '--count'])
    count = int(git_count) - 282
    return f"{VERSION}.{count}"

@tasks.loop(hours=1)
async def reviveComaStatus():
    statusUpdates = StatusUtil.reviveComaStatus(reviveMemberCount=5)
    # if have to revive character
    if statusUpdates != []:
        channelIdList = ReviveUtil.getReviveMsgChannel(statusUpdates)
        msg = "某冥界死神跑來跟店長抱怨公會死傷慘重, 害她最近工作變忙"
        img = ReviveUtil.getPic()
        for channel_id in channelIdList:
            await bot.get_channel(channel_id).send(file=img)
            await bot.get_channel(channel_id).send(msg)
        update: StatusUpdate
        for update in statusUpdates:
            await update.sendMessage(bot)

@tasks.loop(seconds = 60)
async def refreshStatus():
    statusUpdates = StatusUtil.applyExpiredStatus()
    update: StatusUpdate
    for update in statusUpdates:
        await update.sendMessage(bot)

exception_cogs = []

#preload cogs
temp = 'load cogs:\n'
for file in os.listdir(r'./cogs'):
    if not file.startswith("__init__") and not file in exception_cogs and file.endswith('.py'):
        temp += '  |- {}\n'.format(file[:-3])
        bot.load_extension('cogs.{}'.format(file[:-3]))
print(temp)

bot.run(TOKEN)
