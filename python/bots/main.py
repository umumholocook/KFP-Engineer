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
from discord import Role, RawReactionActionEvent
from common.RoleUtil import RoleUtil
from common.LeaderboardUtil import LeaderboardUtil
from common.BotAvatarUtil import downloadImage, fetchUserAvatarUrl, getBotAvatarImageFilePath

VERSION = "0.7"
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
    if message.content == "沒有暈" or "沒暈" in message.content:
        await ctx.reply("我聽你放屁")
    if "自殺" in message.content:
        member = ctx.guild.get_member(message.author.id)
        await member.send("哈囉, 不好意思打擾了, 剛剛好像出現了一些比較敏感的詞, 下面有些資訊可能可以幫到您.\n\n"
        "台灣:\n110、119可分別撥打到台灣的警察局及消防局以處理緊急情況。\n\n衛生福利部鼓勵民眾平常多關愛自己、也多關心身邊的人，一句問候、一個微笑，都能溫暖人心。若您或身邊的人有遇到心理困擾，目前各縣市政府衛生局社區心理衛生中心都可以提供或轉介心理諮詢的服務，亦可撥打衛生福利部安心專線(0800-788-995，請幫幫救救我)提供24小時免費心理諮詢服務，或撥打生命線1995及張老師1980，亦可提供適當的心理支持。\n\n" +
        "香港:\n香港撒瑪利亞防止自殺會：2896 0000.\n生命熱線：24小時熱線: 2382 0000 /長者熱線: 2382 0881 / 青少年專線: 2382 0777.\n向晴熱線: 18288\n\n" +
        "中國:\n北京自殺研究防治中心專線 800-810-1117 / 010-82951332\n上海生命線 ： 400-821-1215\n青少年法律與心理諮詢熱線：12355\n\n" +
        "馬來西亞:\n馬來西亞生命線 603-4265 7995. 星期一到五 7pm to 10pm 、星期六 2pm to 5pm\nBefrienders 03-79568144 or 03-79568145.\n\n" +
        "新加坡:\n新加坡援人協會(Samaritans of Singapore, SOS)：1800-221 4444\n 心理衛生學院(Institute of Mental Health)緊急求助電話服務：6389 2222\n\n" +
        "紐西蘭:\n1737, need to talk? 全國心理健康和藥物成癮干預服務：1737\nYouthline：0800 376 633或短訊234\n\n")
    if "suicide" in message.content or "suicidal" in message.content:
        member = ctx.guild.get_member(message.author.id)
        await member.send("Hi, sorry to bother you, but since you mentioned it, maybe you might find the following information helpful?\n\n"
        "USA:\n911 is the national emergency number\nThe National Suicide Prevention Lifeline can be reached at 1-800-273-8255. (24/7)\nThe Crisis Text Line can be reached by texting HOME to 741-741 (24/7)\nThe TrevorLifeline can be reached at 1-866-488-7386 (24/7, for lesbian, gay, bisexual, transgender and questioning youth)\nThe Trans Lifeline can be reached at 1-877-565-8860.\n\n" +
        "Canada:\n911 is the national emergency number in Canada.\nCanada Suicide Prevention Service can be reached at 1-833-456-4566 or 45645 (Text, 4 p.m. to midnight ET only)\nCrisis Text Line powered by Kids Help Phone  by texting HOME (English) or PARLER (French) to 686868.\nTrans Lifeline can be reached at 1-877-330-6366\n\n" +
        "UK:\n999 and 112 is the national emergency number in the United Kingdom\nNational Suicide Prevention Helpline UK can be reached on 0800 689 5652.\nSOS Silence of Suicide  is a registered charity supporting children & adults struggling with poor mental health and suicidal ideation. They provide a standard rate phone support service open 8pm until Midnight, Friday to Monday inclusive. You can reach them on 0300 1020 505\n\n")
    if ctx.command != None:
        await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload: RawReactionActionEvent):
    channel = await bot.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if message.author.bot:
        return
        
    author_id = message.author.id
    emoji = payload.emoji

    LeaderboardUtil.addReaction(author_id, emoji)

@bot.event
async def on_raw_reaction_remove(payload: RawReactionActionEvent):
    channel = await bot.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if message.author.bot:
        return

    author_id = message.author.id
    emoji = payload.emoji

    LeaderboardUtil.removeReaction(author_id, emoji)

@bot.event
async def on_command_completion(ctx):
    print('on_command_completion Command {0.name} completion'.format(ctx.command))
    #await ctx.message.delete()

@bot.event
async def on_guild_role_update(before: Role, after: Role):
    RoleUtil.updateRole(before.guild.id, before.id, after.name, after.color)
    print(f"updating role with new name {after.name} and color {after.color}")

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

@bot.command(name = "refresh_image",invoke_without_command = True)
async def command_refresh_bot_image(ctx, *attr):
    if ctx.author.bot:
        return
    url: str = fetchUserAvatarUrl()
    if not url:
        await ctx.send("機器人頭像不需要更新.")
        return
    downloadImage(url)
    filePointer = open(getBotAvatarImageFilePath(), 'rb')
    newAvator = filePointer.read()
    await bot.user.edit(avatar=newAvator)
    await ctx.send("機器人頭像更新完成.")

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

@tasks.loop(minutes=15)
async def updateBotAvatar():
    url: str = fetchUserAvatarUrl()
    if not url:
        print("bot avator doesn't need update")
        return
    downloadImage(url)
    filePointer = open(getBotAvatarImageFilePath(), 'rb')
    newAvator = filePointer.read()
    await bot.user.edit(avatar=newAvator)

exception_cogs = []

#preload cogs
temp = 'load cogs:\n'
for file in os.listdir(r'./cogs'):
    if not file.startswith("__init__") and not file in exception_cogs and file.endswith('.py'):
        temp += '  |- {}\n'.format(file[:-3])
        bot.load_extension('cogs.{}'.format(file[:-3]))
print(temp)

bot.run(TOKEN)
