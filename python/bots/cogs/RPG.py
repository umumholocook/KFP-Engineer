from common.models.RPGCharacter import RPGCharacter
from common.RPGUtil.RPGCharacterUtil import RPGCharacterUtil
from discord.ext import commands
from discord import User
from common.NicknameUtil import NicknameUtil

class RPG(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name='rpg', invoke_without_command=True)
    async def rpg_group(self, ctx: commands.Context, *attr):
        msg  = "KFP大冒險指令\n"
        msg += "```\n"
        msg += "!rpg startAdvanture - 開始屬於你的大冒險!!\n"
        msg += "!rpg attack <@其他冒險者> - 攻擊其他冒險者"
        msg += "!rpg status - 查看自己的冒險者數值, 可以添加 \"public\" 對外顯示"
        msg += "```\n"
        await ctx.send(msg)

    @rpg_group.command(name="draft")
    async def draft_character(self, ctx: commands.Context, user: User):
        name = await NicknameUtil.get_user_name(ctx.guild, ctx.author)
        if RPGCharacterUtil.hasAdvantureStared(user.id):
            await ctx.send(f"'{name}'已經是冒險者了, 不需要再招募.")
            return
        if RPGCharacterUtil.createNewRPGCharacter(user.id) != None:
            await ctx.send(f"非常感謝, '{name}'現在已經在冒險者公會登記為冒險者了!")
            return
        await ctx.send(f"看起來招募中心已滿, 詳情請洽冒險者公會員工.")

    # 開始大冒險 
    @rpg_group.command(name="startAdvanture")
    async def init_rpg_character(self, ctx: commands.Context):
        if RPGCharacterUtil.hasAdvantureStared(ctx.author.id):
            await ctx.send("你的冒險已經啟程")
            return
        
        if RPGCharacterUtil.createNewRPGCharacter(ctx.author.id) != None:
            await ctx.send(f"歡迎冒險者{ctx.author.display_name}, 從現在開始你的冒險之旅吧!")
            return

        await ctx.send(f"看起來你的行李好像還沒準備好, 詳情請洽冒險者公會員工.")

    # 從冒險者退休
    @rpg_group.command(name="retire")
    async def retire_rpg_character(self, ctx:commands.Context):
        if not RPGCharacterUtil.hasAdvantureStared(ctx.author.id):
            await ctx.send("看起來你還沒開始你的旅程呢. 在開始前就放棄的概念?")
            return
        RPGCharacterUtil.retireRPGCharacter(ctx.author.id)
        await ctx.send(f"冒險者{ctx.author.display_name}申請退休成功, 辛苦你了!")

    # 顯示狀態
    @rpg_group.command(name="status")
    async def show_character_stats(self, ctx:commands.Context, public = ""):
        if not RPGCharacterUtil.hasAdvantureStared(ctx.author.id):
            await ctx.send("看起來你還沒開始你的旅程呢. 請先申請成為冒險者吧")
            return
        name = await NicknameUtil.get_user_name(ctx.guild, ctx.author)
        rpg: RPGCharacter = RPGCharacterUtil.getRPGCharacter(ctx.author.id)
        result  = f"冒險者: {name}\n"
        result += f"體力: {rpg.hp_current}/{rpg.hp_max}\n"
        result += f"魔力: {rpg.mp_current}/{rpg.mp_max}\n"
        result += f"攻擊力: {rpg.attack_basic}\n"
        result += f"防禦力: {rpg.defense_basic}\n"

        if public == "public":
            await ctx.send(result)
        else:
            await ctx.author.send(result)
    
    @rpg_group.command(name="rest")
    async def character_rest(self, ctx:commands.Context):
        if not RPGCharacterUtil.hasAdvantureStared(ctx.author.id):
            return
        RPGCharacterUtil.goToRest(ctx.author)
        name = await NicknameUtil.get_user_name(ctx.guild, ctx.author)
        await ctx.send("{name}正在休息中...")
    
    @rpg_group.command(name="attack")
    async def attack_character(self, ctx:commands.Context, user: User):
        if not RPGCharacterUtil.hasAdvantureStared(ctx.author.id):
            await ctx.send("看起來你還沒開始你的旅程呢. 請先申請成為冒險者吧")
            return
        if not RPGCharacterUtil.hasAdvantureStared(user.id):
            await ctx.send("看起來對方不是冒險者呢. 請不要攻擊平民")
            return
        author: RPGCharacter = RPGCharacterUtil.getRPGCharacter(ctx.author.id)
        other: RPGCharacter = RPGCharacterUtil.getRPGCharacter(ctx.author.id)
        name = await NicknameUtil.get_user_name(ctx.guild, user)

        if other.hp_current < 1:
            await ctx.send(f"哎不是! '{name}'都已經昏厥了你還攻擊? 攻擊無效啦!")
            return
        if author.hp_current < 1:
            await ctx.send(f"你都沒有體力了! 先去休息啦! 攻擊無效.")
            return
        if author.character.member_id == user.id:
            RPGCharacterUtil.changeHp(other, -1 * author.hp_max)
            await ctx.send(f"{name} 決定朝自己的腹部捅一刀, 因為流血過多而昏厥過去了. 攻擊成功")
            return

        if RPGCharacterUtil.tryToAttack(author, other):
            atk = RPGCharacterUtil.getAttackPoint(author)
            RPGCharacterUtil.changeHp(other, -1 * atk)    
            await ctx.send(f"'{name}' 減少了 {atk}點體力. 攻擊成功!")

            if other.hp_current < 1:
                await ctx.send(f"由於你的攻擊, '{name}'生命力歸零昏厥了過去")
        else:
            await ctx.send(f"'{name}'成功的擋下了你的攻擊! 攻擊失敗!")


def setup(client):
    client.add_cog(RPG(client))