import random
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from common.ChannelUtil import ChannelUtil
from common.DiscordUtil import DiscordUtil
from common.InteractionUtil import InteractionUtil
from common.MemberUtil import MemberUtil
from common.NicknameUtil import NicknameUtil
from common.RPGUtil.ReviveUtil import ReviveUtil
from common.RPGUtil.RPGCharacterUtil import RPGCharacterUtil
from common.RPGUtil.StatusType import StatusType
from common.RPGUtil.StatusUpdate import StatusUpdate
from common.RPGUtil.StatusUtil import StatusUtil
from common.Util import Util
from common.models.Member import Member
from common.models.RPGCharacter import RPGCharacter
from common.models.RPGStatus import RPGStatus


@app_commands.guild_only()
class RPG(commands.GroupCog, group_name="冒險", group_description="KFP大冒險"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="說明", description="KFP大冒險指令說明")
    async def help(self, interaction: discord.Interaction) -> None:
        msg = "KFP大冒險指令\n"
        msg += "```\n"
        msg += "/冒險 開始 - 開始屬於你的大冒險!!\n"
        msg += "/冒險 退休 - 回家種田, 不做冒險者了.\n"
        msg += "/冒險 攻擊 <@其他冒險者> - 攻擊其他冒險者.\n"
        msg += "/冒險 偷襲 <@其他冒險者> - 偷襲其他冒險者.一天只有一次機會\n"
        msg += "/冒險 狀態 - 查看自己的冒險者數值, 可選擇公開顯示.\n"
        msg += "/冒險 休息 - 休息, 休息之後體力會恢復.\n"
        msg += "```\n"
        await interaction.response.send_message(msg)

    @app_commands.command(name="招募", description="招募指定使用者成為冒險者")
    @app_commands.describe(user="要招募的使用者")
    @app_commands.default_permissions(manage_roles=True)
    async def draft_character(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        if not await InteractionUtil.require_channel(interaction, Util.ChannelType.RPG_GUILD):
            return
        name = await NicknameUtil.get_user_name(interaction.guild, user)
        if RPGCharacterUtil.hasAdventureStared(user.id):
            await interaction.response.send_message(
                f"'{name}'已經是冒險者了, 不需要再招募."
            )
            return
        if RPGCharacterUtil.createNewRPGCharacter(user.id) is not None:
            await interaction.response.send_message(
                f"非常感謝, '{name}'現在已經在冒險者公會登記為冒險者了!"
            )
            return
        await interaction.response.send_message("看起來招募中心已滿, 詳情請洽冒險者公會員工.")

    @app_commands.command(
        name="開始", description="如果你想要我的財寶, 那就成為冒險者吧!"
    )
    async def init_rpg_character(self, interaction: discord.Interaction) -> None:
        if not await InteractionUtil.require_channel(interaction, Util.ChannelType.RPG_GUILD):
            return
        if RPGCharacterUtil.hasAdventureStared(interaction.user.id):
            await interaction.response.send_message("你的冒險已經啟程")
            return

        member: Member = MemberUtil.get_or_add_member(interaction.user.id)
        if member.coin < 5000:
            await interaction.response.send_message(
                "看來你的硬幣不足呢, 先在群裡說說話賺取經驗吧."
            )
            return

        is_new = True
        if RPGCharacterUtil.getRPGCharacter(interaction.user.id) is not None:
            is_new = False
        if RPGCharacterUtil.createNewRPGCharacter(interaction.user.id) is not None:
            name = await NicknameUtil.get_user_name(interaction.guild, interaction.user)
            MemberUtil.add_coin(interaction.user.id, -5000)
            MemberUtil.add_coin(self.bot.user.id, 5000)
            if is_new:
                await interaction.response.send_message(
                    f"歡迎冒險者'{name}'的加入, 從現在開始你的冒險之旅吧!"
                )
            else:
                await interaction.response.send_message(
                    f"歡迎回來'{name}', 已恢復您冒險者的身分!"
                )
            return

        await interaction.response.send_message(
            "看起來你的行李好像還沒準備好, 詳情請洽冒險者公會員工."
        )

    @app_commands.command(name="強制更新", description="強制解除已過期的休息狀態")
    @app_commands.default_permissions(manage_roles=True)
    async def force_update(self, interaction: discord.Interaction) -> None:
        if not await InteractionUtil.require_channel(interaction, Util.ChannelType.RPG_GUILD):
            return
        await interaction.response.defer()
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
            msg += "解除休息中..."
        await interaction.followup.send(msg)
        for status in rest_over:
            character = RPGCharacterUtil.getRPGCharacter(status.member_id)
            user = await DiscordUtil.fetch_guild_member(interaction.guild, status.member_id)
            name = await NicknameUtil.get_user_name(interaction.guild, user or interaction.user)
            if character is None:
                msg = f"找不到人物{status.member_id}, 刪除舊狀態..."
            else:
                msg = f"刪除'{name}'的休息狀態..."
                RPGCharacterUtil.changeHp(character, status.buff.buff_value)
            await interaction.followup.send(msg)
            status.delete_instance()
            await interaction.followup.send(f"'{name}'的休息狀態成功")

    @app_commands.command(name="復活", description="將指定冒險者生命值回滿")
    @app_commands.describe(user="要復活的冒險者")
    @app_commands.default_permissions(manage_roles=True)
    async def revive_rpg_character(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        if not await InteractionUtil.require_channel(interaction, Util.ChannelType.BANK):
            return
        if not RPGCharacterUtil.hasAdventureStared(user.id):
            await interaction.response.send_message("看起來對方不是冒險者呢. 無法回血")
            return
        other: RPGCharacter = RPGCharacterUtil.getRPGCharacter(user.id)
        author: RPGCharacter = RPGCharacterUtil.getRPGCharacter(interaction.user.id)
        name = await NicknameUtil.get_user_name(interaction.guild, user)
        if author.character.member_id == user.id:
            await interaction.response.send_message(
                "此功能不是拿來幫你自己加血的, 請不要濫用職權."
            )
            return
        RPGCharacterUtil.changeHp(other, other.hp_max)
        await interaction.response.send_message(f"{name}生命值回復成功.")

    @app_commands.command(name="全員復活", description="復活所有昏厥中的冒險者")
    @app_commands.default_permissions(manage_roles=True)
    async def revive_all(self, interaction: discord.Interaction) -> None:
        if not await InteractionUtil.require_channel(interaction, Util.ChannelType.BANK):
            return
        await interaction.response.defer()
        status_updates = StatusUtil.reviveComaStatus(reviveMemberCount=0)
        if status_updates != []:
            channel_id_list = ReviveUtil.getReviveMsgChannel(status_updates)
            msg = "某冥界死神跑來跟店長抱怨公會死傷慘重, 害她最近工作變忙"
            img = ReviveUtil.getPic()
            for channel_id in channel_id_list:
                channel = await DiscordUtil.fetch_text_channel(self.bot, channel_id)
                if channel:
                    await channel.send(file=img)
                    await channel.send(msg)
            update: StatusUpdate
            for update in status_updates:
                await update.sendMessage(self.bot)

    @app_commands.command(name="退休", description="從冒險者退休")
    async def retire_rpg_character(self, interaction: discord.Interaction) -> None:
        if not await InteractionUtil.require_channel(interaction, Util.ChannelType.RPG_GUILD):
            return
        if not RPGCharacterUtil.hasAdventureStared(interaction.user.id):
            await interaction.response.send_message(
                "看起來你還沒開始你的旅程呢. 在開始前就放棄的概念?"
            )
            return
        if StatusUtil.isResting(interaction.user, interaction.guild.id):
            await interaction.response.send_message(
                "你正在休息. 休息的人是不會申請退休的(~~除非你在夢遊~~)."
            )
            return
        author: RPGCharacter = RPGCharacterUtil.getRPGCharacter(interaction.user.id)
        if StatusUtil.isComa(interaction.user, interaction.guild.id):
            await interaction.response.send_message("你都沒有體力了! 先去休息啦!")
            return
        if author.last_attack + timedelta(hours=12) > datetime.now():
            await interaction.response.send_message(
                "由於你在過去12個小時內攻擊過其他人, 所以不能退休哦"
            )
            return
        RPGCharacterUtil.retireRPGCharacter(interaction.user.id)
        await interaction.response.send_message(
            f"冒險者{interaction.user.display_name}申請退休成功, 辛苦你了!"
        )

    @app_commands.command(name="狀態", description="自己的狀態查詢")
    @app_commands.describe(public="是否公開顯示於頻道")
    async def show_character_stats(
        self, interaction: discord.Interaction, public: bool = False
    ) -> None:
        if not RPGCharacterUtil.hasAdventureStared(interaction.user.id):
            await interaction.response.send_message(
                "看起來你還沒開始你的旅程呢. 請先申請成為冒險者吧"
            )
            return
        name = await NicknameUtil.get_user_name(interaction.guild, interaction.user)
        rpg: RPGCharacter = RPGCharacterUtil.getRPGCharacter(interaction.user.id)
        result = f"冒險者: {name}\n"
        result += f"體力: {rpg.hp_current}/{rpg.hp_max}\n"
        result += f"魔力: {rpg.mp_current}/{rpg.mp_max}\n"
        result += f"攻擊力: {rpg.attack_basic}\n"
        result += f"防禦力: {rpg.defense_basic}\n"

        if public:
            await interaction.response.send_message(result)
        else:
            try:
                await interaction.user.send(result)
                await interaction.response.send_message("已將狀態私訊給您。", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message(
                    "無法私訊您，請先開啟私訊。", ephemeral=True
                )

    @app_commands.command(name="狀態除錯", description="顯示自己的除錯狀態資訊")
    @app_commands.describe(public="是否公開顯示於頻道")
    @app_commands.default_permissions(manage_roles=True)
    async def show_character_stats_debug(
        self, interaction: discord.Interaction, public: bool = False
    ) -> None:
        if not RPGCharacterUtil.hasAdventureStared(interaction.user.id):
            await interaction.response.send_message(
                "看起來你還沒開始你的旅程呢. 請先申請成為冒險者吧"
            )
            return
        name = await NicknameUtil.get_user_name(interaction.guild, interaction.user)
        rpg: RPGCharacter = RPGCharacterUtil.getRPGCharacter(interaction.user.id)
        result = f"冒險者: {name}\n"
        result += f"體力: {rpg.hp_current}/{rpg.hp_max}\n"
        result += f"魔力: {rpg.mp_current}/{rpg.mp_max}\n"
        result += f"攻擊力: {rpg.attack_basic}\n"
        result += f"防禦力: {rpg.defense_basic}\n"
        result += f"absorbBare: {RPGCharacterUtil.getAbsoreDebug(rpg)}\n"
        result += f"armorPoint: {RPGCharacterUtil.getArmorPointDebug(rpg)}\n"
        result += f"armorAbsorb: {RPGCharacterUtil.getArmorAbsoreDebug(RPGCharacterUtil.getArmorPointDebug(rpg), 0)}\n"

        if public:
            await interaction.response.send_message(result)
        else:
            try:
                await interaction.user.send(result)
                await interaction.response.send_message("已將狀態私訊給您。", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message(
                    "無法私訊您，請先開啟私訊。", ephemeral=True
                )

    @app_commands.command(name="休息", description="休息療傷")
    async def character_rest(self, interaction: discord.Interaction) -> None:
        if not RPGCharacterUtil.hasAdventureStared(interaction.user.id):
            await interaction.response.send_message("非冒險者就回家睡覺啦... 在這邊幹嘛?")
            return
        if StatusUtil.isResting(interaction.user, interaction.guild.id):
            await interaction.response.send_message("你正在休息中... 請稍後")
            return
        StatusUtil.startResting(interaction.user, interaction.guild.id)
        name = await NicknameUtil.get_user_name(interaction.guild, interaction.user)
        await interaction.response.send_message(f"{name}正在休息中...")

    @app_commands.command(name="偷襲", description="偷襲其他冒險者")
    @app_commands.describe(user="要偷襲的冒險者")
    async def sneak_attack_character(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        if not await InteractionUtil.require_channel(
            interaction, Util.ChannelType.RPG_BATTLE_GROUND
        ):
            return
        if not RPGCharacterUtil.hasAdventureStared(interaction.user.id):
            await interaction.response.send_message(
                "看起來你還沒開始你的旅程呢. 請先申請成為冒險者吧"
            )
            return
        if not RPGCharacterUtil.hasAdventureStared(user.id):
            await interaction.response.send_message(
                "看起來對方不是冒險者呢. 請不要偷襲平民"
            )
            return
        author: RPGCharacter = RPGCharacterUtil.getRPGCharacter(interaction.user.id)
        other: RPGCharacter = RPGCharacterUtil.getRPGCharacter(user.id)
        author_name = await NicknameUtil.get_user_name(interaction.guild, interaction.user)
        name = await NicknameUtil.get_user_name(interaction.guild, user)

        if StatusUtil.isResting(interaction.user, interaction.guild.id):
            await interaction.response.send_message("你正在休息. 偷襲無效.")
            return
        if StatusUtil.isComa(user, interaction.guild.id):
            await interaction.response.send_message(
                f"哎不是! '{name}'都已經昏厥了你還偷襲? 偷襲無效啦!"
            )
            return
        if StatusUtil.isComa(interaction.user, interaction.guild.id):
            await interaction.response.send_message("你都沒有體力了! 要怎麼偷襲! 偷襲無效.")
            return
        if author.character.member_id == user.id:
            await interaction.response.send_message(
                f"刀插中了{name}的身體... 等等... 為什麼刀插中了一隻雞腿? ...剛剛是不是有個橘色頭髮的人經過?"
            )
            return
        if StatusUtil.isAlerted(user, interaction.guild.id):
            await interaction.response.send_message(
                f"由於已經被偷襲過, '{name}'現在非常警戒並擋下了你的攻擊! 攻擊失敗!"
            )
            await DiscordUtil.send_user_dm(user, f"注意!{author_name}企圖偷襲你但是被你識破了!")
            return

        success = random.randint(0, 1) == 0
        if success:
            multiplier = [2, 2, 2, 2, 2, 2, 8, 8, 10, 20]
            random_index = random.randrange(len(multiplier))
            atk = RPGCharacterUtil.getAttackPoint(author, other) * multiplier[random_index]
            dead = RPGCharacterUtil.changeHp(other, -1 * atk)
            if dead:
                StatusUtil.createComaStatus(interaction.guild.id, user, other.hp_max)
            RPGCharacterUtil.attackSuccess(author)
            await interaction.response.send_message(f"'{name}' 減少了 {atk}點體力. 偷襲成功!")

            if StatusUtil.isComa(user, interaction.guild.id):
                await interaction.followup.send(
                    f"由於你的攻擊, '{name}'生命力歸零昏厥了過去"
                )
            await DiscordUtil.send_user_dm(user, f"注意!你被{author_name}偷襲了!")
        else:
            await interaction.response.send_message(
                f"由於你的腳步聲太大, '{name}'注意到並擋下了你的攻擊! 攻擊失敗!"
            )
        StatusUtil.createOrUpdateAlertStatus(user.id, interaction.guild.id, 86400)

    @app_commands.command(name="攻擊", description="攻擊某位玩家")
    @app_commands.describe(user="要攻擊的冒險者")
    async def attack_character(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        if not await InteractionUtil.require_channel(
            interaction, Util.ChannelType.RPG_BATTLE_GROUND
        ):
            return
        if not RPGCharacterUtil.hasAdventureStared(interaction.user.id):
            await interaction.response.send_message(
                "看起來你還沒開始你的旅程呢. 請先申請成為冒險者吧"
            )
            return
        if not RPGCharacterUtil.hasAdventureStared(user.id):
            await interaction.response.send_message(
                "看起來對方不是冒險者呢. 請不要攻擊平民"
            )
            return
        author: RPGCharacter = RPGCharacterUtil.getRPGCharacter(interaction.user.id)
        other: RPGCharacter = RPGCharacterUtil.getRPGCharacter(user.id)
        author_name = await NicknameUtil.get_user_name(interaction.guild, interaction.user)
        name = await NicknameUtil.get_user_name(interaction.guild, user)

        if StatusUtil.isResting(interaction.user, interaction.guild.id):
            await interaction.response.send_message("你正在休息. 攻擊無效.")
            return
        if StatusUtil.isComa(user, interaction.guild.id) or StatusUtil.isResting(
            user, interaction.guild.id
        ):
            await interaction.response.send_message(
                f"哎不是! '{name}'都已經昏厥了你還攻擊? 攻擊無效啦!"
            )
            return
        if StatusUtil.isResting(user, interaction.guild.id):
            await interaction.response.send_message(
                f"卑鄙源之助! '{name}'正在休息你還攻擊? 攻擊無效啦!"
            )
            return
        if StatusUtil.isComa(interaction.user, interaction.guild.id):
            await interaction.response.send_message("你都沒有體力了! 先去休息啦! 攻擊無效.")
            return
        if author.character.member_id == user.id:
            await interaction.response.send_message(
                f"當刀柄接近{name}的身體的時候, 旁邊出現了一隻手阻止了你. 雖然不知道是誰, 但依稀有著一頭橘色的頭髮..."
            )
            return
        if RPGCharacterUtil.tryToAttack(author, other):
            atk = RPGCharacterUtil.getAttackPoint(author, other)
            dead = RPGCharacterUtil.changeHp(other, -1 * atk)
            if dead:
                StatusUtil.createComaStatus(interaction.guild.id, user, other.hp_max)
            RPGCharacterUtil.attackSuccess(author)
            await interaction.response.send_message(f"'{name}' 減少了 {atk}點體力. 攻擊成功!")

            if StatusUtil.isComa(user, interaction.guild.id):
                await interaction.followup.send(
                    f"由於你的攻擊, '{name}'生命力歸零昏厥了過去"
                )
            await DiscordUtil.send_user_dm(user, f"注意!你被{author_name}攻擊了!")
        else:
            await interaction.response.send_message(
                f"'{name}'成功的擋下了你的攻擊! 攻擊失敗!"
            )


async def setup(client):
    await client.add_cog(RPG(client))