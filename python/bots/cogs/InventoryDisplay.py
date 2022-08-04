from discord.ext import commands
from discord import Embed
from common.RPGUtil.InventoryUtil import InventoryUtil
from common.RPGUtil.ItemType import ItemType
from common.RPGUtil.Buff import BuffType

class InventoryDisplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='inv', invoke_without_command = True)
    async def inventory_group(self, ctx: commands.Context, *attr):
        msg = "物品清單指令\n"
        msg += "```"
        msg += "!inv list 列出玩家(你)的物品清單\n"
        msg += "!inv item <物品名稱> 列出玩家(你)的物品清單中特定物品詳細資料\n"
        msg += "```"
#####################################以下指令為開發人員專用！正式版本發布前請刪除！
        msg += "\n:warning:\n"
        msg += "```"
        msg += "!inv purge 清空使用者物品清單"
        msg += "```"
##############################################################################
        await ctx.send(msg)

    @inventory_group.command(name='list')
    async def show_inventory(self, ctx: commands.Context):
        result = InventoryUtil.getAllItemsBelongToUser(ctx.guild.id, ctx.author.id)
        result_count = len(result)  # 資料個數 = 資料輸出串列總長
        if result_count < 1:
            await ctx.send('`你尚未擁有任何物品!`')
        else:
            # 內嵌方塊: 內容初始化
            embed_inventory = Embed(
                title=f"{ctx.author.name}的物品清單",
                description="清單每頁20筆資料",
                color=0xff8000
            )

            # 內嵌方塊: 顯示全部物品
            # 這裡要用set，不然重複的物品會出現在顯示欄位
            for item_index, item_display in enumerate(result[:], start=1):
                embed_inventory.add_field(name=None, value = f'{item_index}. {item_display.item.name} x {item_display.amount}', inline=False)
                
            # 暫時放一張圖代替 (set_thumbnail())
            embed_inventory.set_thumbnail(url="https://s1.zerochan.net/Takanashi.Kiara.600.3145979.jpg")
            embed_inventory.set_footer(text=f"一共{result_count}種物品")
            await ctx.send(embed = embed_inventory)

    @inventory_group.command(name='item')
    async def show_item(self, ctx: commands.Context, item_name: str):
        result = InventoryUtil.getAllItemsBelongToUser(ctx.guild.id, ctx.author.id)
        if len(result) < 1:
            await ctx.send('`你尚未擁有任何物品!`')
        else:
            # for-else: for
            for result_item in result:
                if result_item.item.name == item_name:
                    embed_specific_item = Embed(
                        title=f"物品名稱: {result_item.item.name}",
                        description=f"描述: {result_item.item.description}",
                        color=0xff8000
                    )
                    # 內嵌方塊: 內容第1列之1，物品ID
                    embed_specific_item.add_field(
                        name = 'ID:',
                        value = '{}'.format(str(result_item.item.id).ljust(3, " ")),
                        inline = True
                    )
                    # 內嵌方塊: 內容第1列之2，持有數量
                    embed_specific_item.add_field(
                        name = '持有數量:',
                        value = '{}'.format(str(result_item.amount).ljust(3, " ")),
                        inline = True
                    )
                    # 內嵌方塊: 內容第2列之1，等級限制
                    embed_specific_item.add_field(
                        name = '等級限制:',
                        value = '{}'.format(str(result_item.item.level_required).ljust(3, " ")),
                        inline = True
                    )
                    # 內嵌方塊: 內容第2列之2，價格
                    embed_specific_item.add_field(
                        name = '價格:',
                        value = '{}'.format(str(result_item.item.token_required).ljust(3, " ")),
                        inline = True
                    )
                     # 內嵌方塊: 內容第3列之1，物品類型
                    embed_specific_item.add_field(
                        name = '物品類型:',
                        value = '{}'.format(str(result_item.item.type).ljust(3, " ")),  #顯示錯誤 e.g. ItemType.RECOVER
                        inline = True
                    )
                     # 內嵌方塊: 內容第3列之2，增幅類型
                    embed_specific_item.add_field(
                        name = '增幅類型:',
                        value = '{}'.format(str(result_item.item.buff.buff_type).ljust(3, " ")),    #顯示錯誤 e.g. HITPOINT
                        inline = True
                    )
                    # 暫時放一張圖代替 (set_thumbnail())
                    embed_specific_item.set_thumbnail(url='https://images.heb.com/is/image/HEBGrocery/001584756')
                    await ctx.send(embed = embed_specific_item)
                    break;
            # for-else: else
            else:
                await ctx.send('`你的物品清單裡沒有此物品!`')
    
############################################以下指令為開發人員專用！正式版本發布前請刪除！
    @inventory_group.command(name='purge')
    async def clear_inventory(self, ctx: commands.Context):
        # result = InventoryUtil.getAllItemsBelongToUser(ctx.guild.id, ctx.author.id)
        InventoryUtil.removeUserItems_TEST(ctx.guild.id, ctx.author.id)
#####################################################################################

async def setup(bot):
    await bot.add_cog(InventoryDisplay(bot))
