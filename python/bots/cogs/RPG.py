from common.RPGUtil.RPGCharacterUtil import RPGCharacterUtil
from discord.ext import commands

class RPG(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name='rpg', invoke_without_command=True)
    async def rpg_group(self, ctx: commands.Context, *attr):
        msg  = "KFP大冒險指令\n"
        msg += "```\n"
        msg += "!rpg startAdvanture 開始屬於你的大冒險!!\n"
        msg += "!rpg attack <@其他冒險者> 攻擊其他冒險者"
        msg += "```\n"
        await ctx.send(msg)

    # 開始大冒險 
    @rpg_group.command(name="startAdvanture")
    async def init_rpg_character(self, ctx: commands.Context):
        if RPGCharacterUtil.hasAdvantureStared(ctx.author.id):
            await ctx.send("你的冒險已經啟程")
            return
        
        if RPGCharacterUtil.createNewRPGCharacter(ctx.author.id) != None:
            await ctx.send(f"歡迎冒險者{ctx.author.name}, 從現在開始你的冒險之旅吧!")
            return

        await ctx.send(f"看起來你的行李好像還沒準備好, 詳情請洽冒險者公會員工.")

    # 從冒險者退休
    @rpg_group.command(name="retire")
    async def retire_rpg_character(self, ctx:commands.Context):
        if not RPGCharacterUtil.hasAdvantureStared(ctx.author.id):
            await ctx.send("看起來你還沒開始你的旅程呢. 在開始前就放棄的概念?")
            return
        RPGCharacterUtil.retireRPGCharacter(ctx.author.id)
        await ctx.send(f"冒險者{ctx.author.name}申請退休成功, 辛苦你了!")


def setup(client):
    client.add_cog(RPG(client))