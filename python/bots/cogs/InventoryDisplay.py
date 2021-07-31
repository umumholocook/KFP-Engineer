from discord.ext.commands.core import check
from discord.ext import commands
from discord import Embed
from common.InventoryUtil import InventoryUtil

class InventoryDisplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='inv', invoke_without_command = True)
    async def inventory_group(self, ctx: commands.Context, *attr):
        msg = "物品清單指令\n"
        msg += "```"
        msg += "!inv list 列出玩家(你)的物品清單\n"
        msg += "```"
        await ctx.send(msg)

    @inventory_group.command(command='list')
    async def show_inventory(self, ctx: commands.context):
        result = InventoryUtil.getAllItemsBelongToUser(ctx.guild_id, ctx.user_id)
        result_count = len(result)  # 資料個數 = 資料輸出串列總長
        if result_count < 1:
            await ctx.send('你尚未擁有認為物品!')
        else:
            # 內嵌方塊: 內容初始化
            embed_inventory = Embed(
                title=f"{ctx.author.name}的物品清單",
                description="清單每頁20筆資料",
                color=0xff8000
            )

            # 內嵌方塊: 顯示全部物品
            for item_index, item_display in enumerate(result[:], start=1):
                embed_inventory.add_field(value=f'{item_index}. {item_display}', inline=False)
                
            embed_inventory.set_thumbnail(url="https://s1.zerochan.net/Takanashi.Kiara.600.3145979.jpg") # 暫時放一張圖代替
            embed_inventory.set_footer(text=f"一共{result_count}個物品")
            await ctx.send(embed = embed_inventory)

def setup(bot):
    bot.add_cog(InventoryDisplay(bot))
