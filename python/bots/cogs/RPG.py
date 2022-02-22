from common.MemberUtil import MemberUtil
from common.models.Member import Member
from common.models.RPGStatus import RPGStatus
from common.RPGUtil.StatusType import StatusType
from common.RPGUtil.ReviveUtil import ReviveUtil
from common.RPGUtil.StatusUpdate import StatusUpdate
from common.Util import Util
from common.ChannelUtil import ChannelUtil
from common.RPGUtil.StatusUtil import StatusUtil
from common.models.RPGCharacter import RPGCharacter
from common.RPGUtil.RPGCharacterUtil import RPGCharacterUtil
from discord.ext import commands
from discord import User, Embed, File
from common.NicknameUtil import NicknameUtil
from datetime import datetime, timedelta
import random, os


class RPG(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='rpg', invoke_without_command=True)
    async def rpg_group(self, ctx: commands.Context, *attr):
        msg = "KFP大冒險指令\n"
        msg += "```\n"
        msg += "!rpg startAdventure - 開始屬於你的大冒險!!\n"
        msg += "!rpg retire - 回家種田, 不做冒險者了.\n"
        msg += "!rpg attack <@其他冒險者> - 攻擊其他冒險者.\n"
        msg += "!rpg sneak_attack <@其他冒險者> - 偷襲其他冒險者.一天只有一次機會\n"
        msg += "!rpg status - 查看自己的冒險者數值, 可以添加 \"public\" 對外顯示.\n"
        msg += "!rpg rest - 休息, 休息之後體力會恢復.\n"
        msg += "```\n"
        await ctx.send(msg)

    @rpg_group.command(name="draft")
    async def draft_character(self, ctx: commands.Context, user: User):
        if not ChannelUtil.hasChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.RPG_GUILD):
            return
        name = await NicknameUtil.get_user_name(ctx.guild, user)
        if RPGCharacterUtil.hasAdventureStared(user.id):
            await ctx.send(f"'{name}'已經是冒險者了, 不需要再招募.")
            return
        if RPGCharacterUtil.createNewRPGCharacter(user.id) != None:
            await ctx.send(f"非常感謝, '{name}'現在已經在冒險者公會登記為冒險者了!")
            return
        await ctx.send(f"看起來招募中心已滿, 詳情請洽冒險者公會員工.")

    # 開始大冒險 
    @rpg_group.command(name="startAdventure")
    async def init_rpg_character(self, ctx: commands.Context):
        if not ChannelUtil.hasChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.RPG_GUILD):
            return
        if RPGCharacterUtil.hasAdventureStared(ctx.author.id):
            await ctx.send("你的冒險已經啟程")
            return

        member: Member = MemberUtil.get_or_add_member(ctx.author.id)
        if member.coin < 5000:
            await ctx.send(f"看來你的硬幣不足呢, 先在群裡說說話賺取經驗吧.")
            return

        isNew = True
        if RPGCharacterUtil.getRPGCharacter(ctx.author.id) != None:
            isNew = False
        if RPGCharacterUtil.createNewRPGCharacter(ctx.author.id) != None:
            user = self.bot.get_user(ctx.author.id)
            name = await NicknameUtil.get_user_name(ctx.guild, user)
            MemberUtil.add_coin(ctx.author.id, -5000)
            MemberUtil.add_coin(ctx.bot.user.id, 5000)
            if isNew:
                await ctx.send(f"歡迎冒險者'{name}'的加入, 從現在開始你的冒險之旅吧!")
            else:
                await ctx.send(f"歡迎回來'{name}', 已恢復您冒險者的身分!")
            return

        await ctx.send(f"看起來你的行李好像還沒準備好, 詳情請洽冒險者公會員工.")

    @rpg_group.command(name="force_update")
    async def force_update(self, ctx: commands.Context):
        if not ChannelUtil.hasChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.RPG_GUILD):
            return
        results = StatusUtil.getAllStatus(StatusType.REST)
        rest_over = []
        now = datetime.now()
        status: RPGStatus
        for status in results:
            if status.expire_time < now:
                rest_over.append(status)
        msg = f"目前休息中的人為 {len(results)}人\n"
        msg += f"可以解除休息的人數為 {len(rest_over)}人\n"
        if len(rest_over) > 0:
            msg += f"解除休息中..."
        await ctx.send(msg)
        for status in rest_over:
            character = RPGCharacterUtil.getRPGCharacter(status.member_id)
            user = self.bot.get_user(status.member_id)
            name = await NicknameUtil.get_user_name(ctx.guild, user)
            if character == None:
                msg = f"找不到人物{status.member_id}, 刪除舊狀態..."
            else:
                msg = f"刪除'{name}'的休息狀態..."
                RPGCharacterUtil.changeHp(character, status.buff.buff_value)
            await ctx.send(msg)
            status.delete_instance()
            await ctx.send(f"'{name}'的休息狀態成功")

    @rpg_group.command(name="revive")
    async def revive_rpg_character(self, ctx: commands.Command, user: User):
        if not ChannelUtil.hasChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.BANK):
            return
        if not RPGCharacterUtil.hasAdventureStared(user.id):
            await ctx.send("看起來對方不是冒險者呢. 無法回血")
            return
        other: RPGCharacter = RPGCharacterUtil.getRPGCharacter(user.id)
        author: RPGCharacter = RPGCharacterUtil.getRPGCharacter(ctx.author.id)
        name = await NicknameUtil.get_user_name(ctx.guild, user)
        if author.character.member_id == user.id:
            await ctx.send(f"此功能不是拿來幫你自己加血的, 請不要濫用職權.")
            return
        RPGCharacterUtil.changeHp(other, other.hp_max)
        await ctx.send(f"{name}生命值回復成功.")

    @rpg_group.command(name="reviveall")
    async def revive_all(self, ctx: commands.Command):
        if not ChannelUtil.hasChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.BANK):
            return
        statusUpdates = StatusUtil.reviveComaStatus(reviveMemberCount=0)
        if statusUpdates != []:
            channelIdList = ReviveUtil.getReviveMsgChannel(statusUpdates)
            msg = "某冥界死神跑來跟店長抱怨公會死傷慘重, 害她最近工作變忙"
            img = ReviveUtil.getPic()
            for channel_id in channelIdList:
                await self.bot.get_channel(channel_id).send(file=img)
                await self.bot.get_channel(channel_id).send(msg)
            update: StatusUpdate
            for update in statusUpdates:
                await update.sendMessage(self.bot)


    # 從冒險者退休
    @rpg_group.command(name="retire")
    async def retire_rpg_character(self, ctx: commands.Context):
        if not ChannelUtil.hasChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.RPG_GUILD):
            return
        if not RPGCharacterUtil.hasAdventureStared(ctx.author.id):
            await ctx.send("看起來你還沒開始你的旅程呢. 在開始前就放棄的概念?")
            return
        if StatusUtil.isResting(ctx.author, ctx.guild.id):
            await ctx.send("你正在休息. 休息的人是不會申請退休的(~~除非你在夢遊~~).")
            return
        author: RPGCharacter = RPGCharacterUtil.getRPGCharacter(ctx.author.id)
        if StatusUtil.isComa(ctx.author, ctx.guild.id):
            await ctx.send(f"你都沒有體力了! 先去休息啦!")
            return
        if author.last_attack + timedelta(hours=12) > datetime.now():
            await ctx.send(f"由於你在過去12個小時內攻擊過其他人, 所以不能退休哦")
            return
        RPGCharacterUtil.retireRPGCharacter(ctx.author.id)
        await ctx.send(f"冒險者{ctx.author.display_name}申請退休成功, 辛苦你了!")

    # 顯示狀態
    @rpg_group.command(name="status")
    async def show_character_stats(self, ctx: commands.Context, public=""):
        if not RPGCharacterUtil.hasAdventureStared(ctx.author.id):
            await ctx.send("看起來你還沒開始你的旅程呢. 請先申請成為冒險者吧")
            return
        name = await NicknameUtil.get_user_name(ctx.guild, ctx.author)
        rpg: RPGCharacter = RPGCharacterUtil.getRPGCharacter(ctx.author.id)
        result = f"冒險者: {name}\n"
        result += f"體力: {rpg.hp_current}/{rpg.hp_max}\n"
        result += f"魔力: {rpg.mp_current}/{rpg.mp_max}\n"
        result += f"攻擊力: {rpg.attack_basic}\n"
        result += f"防禦力: {rpg.defense_basic}\n"

        if public == "public":
            await ctx.send(result)
        else:
            await ctx.author.send(result)

    @rpg_group.command(name="rest")
    async def character_rest(self, ctx: commands.Context):
        if not RPGCharacterUtil.hasAdventureStared(ctx.author.id):
            await ctx.send(f"非冒險者就回家睡覺啦... 在這邊幹嘛?")
            return
        if StatusUtil.isResting(ctx.author, ctx.guild.id):
            await ctx.send(f"你正在休息中... 請稍後")
            return
        StatusUtil.startResting(ctx.author, ctx.guild.id)
        name = await NicknameUtil.get_user_name(ctx.guild, ctx.author)
        await ctx.send(f"{name}正在休息中...")
    
    @rpg_group.command(name="snake_attack")
    async def snake_attack(self, ctx: commands.Context):

        embedMsg = Embed()
        embedMsg.set_image(url='attachment://snake_attack.gif')

        img = File(os.sep.join((os.getcwd(), "resource", "image", "snake_attack.gif")), filename="snake_attack.gif")
        await ctx.send(file=img, embed=embedMsg)
        pass

    @rpg_group.command(name="sneak_attack")
    async def sneak_attack_character(self, ctx: commands.Context, user: User):
        if not ChannelUtil.hasChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.RPG_BATTLE_GROUND):
            return
        if not RPGCharacterUtil.hasAdventureStared(ctx.author.id):
            await ctx.send("看起來你還沒開始你的旅程呢. 請先申請成為冒險者吧")
            return
        if not RPGCharacterUtil.hasAdventureStared(user.id):
            await ctx.send("看起來對方不是冒險者呢. 請不要偷襲平民")
            return
        author: RPGCharacter = RPGCharacterUtil.getRPGCharacter(ctx.author.id)
        other: RPGCharacter = RPGCharacterUtil.getRPGCharacter(user.id)
        author_name = await NicknameUtil.get_user_name(ctx.guild, ctx.author)
        name = await NicknameUtil.get_user_name(ctx.guild, user)
        guild = self.bot.get_guild(ctx.guild.id)
        member = guild.get_member(user.id)

        if StatusUtil.isResting(ctx.author, ctx.guild.id):
            await ctx.send("你正在休息. 偷襲無效.")
            return
        if StatusUtil.isComa(user, ctx.guild.id):
            await ctx.send(f"哎不是! '{name}'都已經昏厥了你還偷襲? 偷襲無效啦!")
            return
        if StatusUtil.isComa(ctx.author, ctx.guild.id):
            await ctx.send(f"你都沒有體力了! 要怎麼偷襲! 偷襲無效.")
            return
        if author.character.member_id == user.id:
            dead = RPGCharacterUtil.changeHp(other, -1 * author.hp_max)
            if dead:
                StatusUtil.createComaStatus(ctx.guild.id, user, other.hp_max)
            await ctx.send(f"{name} 查覺到自己的行為, 但是阻止不了自己偷襲自己. 於是流血過多而昏厥過去. 攻擊成功")
            return
        if StatusUtil.isAlerted(user, ctx.guild.id):
            await ctx.send(f"由於已經被偷襲過, '{name}'現在非常警戒並擋下了你的攻擊! 攻擊失敗!")
            msg = f"注意!{author_name}企圖偷襲你但是被你識破了!"
            await member.send(msg)
            return

        # try to sneak attack
        success = random.randint(0, 1) == 0
        if success:
            multiplier = [2, 2, 2, 2, 2, 2, 8, 8, 10, 20]
            random_index = random.randrange(len(multiplier))
            atk = RPGCharacterUtil.getAttackPoint(author) * multiplier[random_index]
            dead = RPGCharacterUtil.changeHp(other, -1 * atk)
            if dead:
                StatusUtil.createComaStatus(ctx.guild.id, user, other.hp_max)
            RPGCharacterUtil.attackSuccess(author)
            await ctx.send(f"'{name}' 減少了 {atk}點體力. 偷襲成功!")

            if StatusUtil.isComa(user, ctx.guild.id):
                await ctx.send(f"由於你的攻擊, '{name}'生命力歸零昏厥了過去")
            # sent a message let member know is being attack
            msg = f"注意!你被{author_name}偷襲了!"
            await member.send(msg)
        else:
            await ctx.send(f"由於你的腳步聲太大, '{name}'注意到並擋下了你的攻擊! 攻擊失敗!")
        # the other person is now alerted
        StatusUtil.createOrUpdateAlertStatus(member.id, ctx.guild.id, 86400)

    @rpg_group.command(name="attack")
    async def attack_character(self, ctx: commands.Context, user: User):
        if not ChannelUtil.hasChannel(ctx.guild.id, ctx.channel.id, Util.ChannelType.RPG_BATTLE_GROUND):
            return
        if not RPGCharacterUtil.hasAdventureStared(ctx.author.id):
            await ctx.send("看起來你還沒開始你的旅程呢. 請先申請成為冒險者吧")
            return
        if not RPGCharacterUtil.hasAdventureStared(user.id):
            await ctx.send("看起來對方不是冒險者呢. 請不要攻擊平民")
            return
        author: RPGCharacter = RPGCharacterUtil.getRPGCharacter(ctx.author.id)
        other: RPGCharacter = RPGCharacterUtil.getRPGCharacter(user.id)
        author_name = await NicknameUtil.get_user_name(ctx.guild, ctx.author)
        name = await NicknameUtil.get_user_name(ctx.guild, user)
        guild = self.bot.get_guild(ctx.guild.id)
        member = guild.get_member(user.id)

        if StatusUtil.isResting(ctx.author, ctx.guild.id):
            await ctx.send("你正在休息. 攻擊無效.")
            return
        if StatusUtil.isComa(user, ctx.guild.id) or StatusUtil.isResting(user.id, ctx.guild.id):
            await ctx.send(f"哎不是! '{name}'都已經昏厥了你還攻擊? 攻擊無效啦!")
            return
        if StatusUtil.isResting(user.id, ctx.guild.id):
            await ctx.send(f"卑鄙源之助! '{name}'正在休息你還攻擊? 攻擊無效啦!")
            return
        if StatusUtil.isComa(ctx.author, ctx.guild.id):
            await ctx.send(f"你都沒有體力了! 先去休息啦! 攻擊無效.")
            return
        if author.character.member_id == user.id:
            dead = RPGCharacterUtil.changeHp(other, -1 * author.hp_max)
            if dead:
                StatusUtil.createComaStatus(guild_id=ctx.guild.id, user=user, hp_max=other.hp_max)
            await ctx.send(f"{name} 決定朝自己的腹部捅一刀, 因為流血過多而昏厥過去了. 攻擊成功")
            return
        if RPGCharacterUtil.tryToAttack(author, other):
            atk = RPGCharacterUtil.getAttackPoint(author)
            dead = RPGCharacterUtil.changeHp(other, -1 * atk)
            if dead:
                StatusUtil.createComaStatus(ctx.guild.id, user, other.hp_max)
            RPGCharacterUtil.attackSuccess(author)
            await ctx.send(f"'{name}' 減少了 {atk}點體力. 攻擊成功!")

            if StatusUtil.isComa(user, ctx.guild.id):
                await ctx.send(f"由於你的攻擊, '{name}'生命力歸零昏厥了過去")
            # sent a message let member know is being attack
            msg = f"注意!你被{author_name}攻擊了!"
            await member.send(msg)
        else:
            await ctx.send(f"'{name}'成功的擋下了你的攻擊! 攻擊失敗!")


def setup(client):
    client.add_cog(RPG(client))
