import discord, os, signal, tempfile

from common.BotAvatarUtil import downloadImage, fetchUserAvatarUrl, getBotAvatarImageFilePath
from common.ChannelUtil import ChannelUtil
from common.KFP_DB import KfpDb
from common.LeaderboardUtil import LeaderboardUtil
from common.RoleUtil import RoleUtil
from common.RPGUtil.ReviveUtil import ReviveUtil
from common.RPGUtil.StatusUpdate import StatusUpdate
from common.RPGUtil.StatusUtil import StatusUtil
from common.models.Channel import Channel
from discord.ext import commands, tasks
from discord import app_commands, Embed, File, RawReactionActionEvent, Role
from pathlib import Path
from subprocess import check_output, Popen

VERSION = "0.8"
TOKEN=os.environ['KFP_TOKEN']

class Steward(commands.Bot):    
    def __init__(self, intents: discord.Intents):
        super().__init__(
            command_prefix="!",
            intents = intents
        )
        
    async def on_ready(self):
        await self.wait_until_ready()
        
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
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
                await self.get_channel(channel.channel_id).send("更新結束, 現在版本 {}".format(get_version()))
        else:
            db = KfpDb()
        refreshStatus.start()
        print("refreshStatus started")
        reviveComaStatus.start()
        print("revive started")
        updateBotAvatar.start()
        print("update bot avatart started")
    
    def _get_futa_path(self):
        return os.sep.join((os.getcwd(), "resource", "image", "no_futa.webp"))

    async def on_message(self, message: discord.Message):
        print(f"on_message get message from {message.author} : {message.content}") if message.author.id != bot.user.id else None
        ctx = await self.get_context(message)
        if message.content == "沒有暈" or "沒暈" in message.content:
            await ctx.reply("我聽你放屁")
        if "扶他" in message.content and "不要扶他" not in message.content:
            embedMsg = Embed()
            embedMsg.set_image(url='attachment://rickrolled.gif')
            img = File(self._get_futa_path(), filename="rickrolled.gif")
            await ctx.reply(file=img, embed=embedMsg)
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
            await self.process_commands(message)
    
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        channel = await self.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author.bot:
            return
            
        author_id = message.author.id
        emoji = payload.emoji

        LeaderboardUtil.addReaction(author_id, emoji)
    
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        channel = await self.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author.bot:
            return

        author_id = message.author.id
        emoji = payload.emoji

        LeaderboardUtil.removeReaction(author_id, emoji)
    
    async def on_command_completion(self, ctx: commands.Context):
        print('on_command_completion Command {0.name} completion'.format(ctx.command))
                
    async def on_guild_rolw_update(self, before: Role, after: Role):
        RoleUtil.updateRole(before.guild.id, before.id, after.name, after.color)
        print(f"updating role with new name {after.name} and color {after.color}")
    
    async def setup_hook(self):
        #preload cogs
        exception_cogs = []
        
        temp = 'load cogs:\n'
        for file in os.listdir(r'./cogs'):
            if not file.startswith("__init__") and not file in exception_cogs and file.endswith('.py'):
                temp += '  |- {}\n'.format(file[:-3])
                
                await self.load_extension(name='cogs.{}'.format(file[:-3]))
        print(temp)

        await self.tree.sync()
        print("Tree sync completed")

# Setup bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = Steward(intents)
tree = bot.tree

# Helper methods

def getTempFile():
        return Path('{}/kpf_restart'.format(tempfile.gettempdir()))
    
def get_version():
    git_count = check_output(['git', 'rev-list', '--all', '--count'])
    count = int(git_count) - 282
    return f"{VERSION}.{count}"

# Setup looping tasks

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
    
# setup slash commands

@tree.command(name = "invite_link", description = "邀請大總管連結")
@commands.has_permissions(manage_roles=True)
async def command_invite_link(interaction: discord.Interaction):
    link = "https://discordapp.com/oauth2/authorize?&client_id={}&scope=bot&permissions={}".format(bot.user.id, 1543892049)
    await interaction.response.send_message(link)

@tree.command(name = "update", description = "檢查並更新大總管")
@commands.has_permissions(manage_roles=True)
async def command_update(interaction: discord.Interaction):
    discord.Permissions
    db = KfpDb()
    ChannelUtil.setRebootMessageChannel(guild_id= interaction.guild.id, channel_id=interaction.channel.id)
    await interaction.response.send_message("現在版本 {}, 檢查更新中...".format(get_version()))
    tmpFile = getTempFile()
    tmpFile.touch()
    f = open(tmpFile, "a")
    f.write(f"{interaction.guild_id}.")
    f.write(f"{os.getpid()}")
    f.close()

    Popen([os.sep.join((os.getcwd(), "update_and_restart.sh"))], shell=True)
    
@tree.command(name = "version", description = "檢查大總管版本")
@commands.has_permissions(manage_roles=True)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(get_version())
    
@tree.command(name = "檢查版本", description = "檢查大總管版本")
@commands.has_permissions(manage_roles=True)
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(get_version())

@tree.command(name = "refresh_image", description = "立刻更新大總管頭貼")
@commands.has_permissions(manage_roles=True)
async def command_refresh_bot_image(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    url: str = fetchUserAvatarUrl()
    if not url:
        await interaction.response.send_message("大總管頭像不需要更新.")
        return
    downloadImage(url)
    filePointer = open(getBotAvatarImageFilePath(), 'rb')
    newAvator = filePointer.read()
    await bot.user.edit(avatar=newAvator)
    await interaction.response.send_message("大總管頭像更新完成.")

@tree.error
async def permission_error(error: app_commands.AppCommandError, interaction: discord.Integration):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(f"出現錯誤: {error}\n 你沒有足夠的權限使用這個功能", ephemeral = True)
    else: raise error
    

bot.run(TOKEN)
