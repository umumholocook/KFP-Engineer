from common.RPGUtil.ItemType import ItemType
from common.RPGUtil.Buff import BuffType
from common.RPGUtil.InventoryUtil import InventoryUtil, ErrorCode
from common.RPGUtil.ItemUtil import ItemUtil
from discord.ext import commands
from common.MemberUtil import MemberUtil
from common.GamblingUtil import GamblingUtil


class Shop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='shop', invoke_without_command=True)
    async def shop_group(self, ctx: commands.Context, *attr):
        msg = "歡迎來到KFP炸機店小賣部\n"
        msg += "本小賣部一律使用雞腿來購買商品\n"
        msg += "```"
        msg += "!shop buy <購買數量> <商品名稱> 購買指定數量的商品\n"
        msg += "!shop menu 展示目前販賣中的商品\n"
        msg += "!shop exchange <雞腿數量> 用硬幣兌換雞腿\n"
        msg += "!shop token 顯示目前擁有的雞腿數量\n"
        msg += "!shop detail <商品名稱> 列出商品詳細資料\n"
        msg += "```"
        await ctx.send(msg)

    # list 上架的商品
    @shop_group.command(name="menu")
    async def show_menu(self, ctx: commands.Command):
        result = InventoryUtil.ShopMenu(ctx.guild.id)
        if len(result) < 1:
            await ctx.send('目前商品都被買光了!')
        else:
            msg = "```\n"
            msg += "{:^63}".format("===商品價目表===")
            msg += "\n"
            for products in result:
                msg += " 購買ID: {}".format(str(products.item.id).ljust(3, " "))
                msg += " 商品名稱: {}".format(products.item.name).ljust(15, " ")
                msg += " 等級限制: {}".format(str(products.item.level_required).ljust(3, " "))
                msg += " 價格: {}".format(str(products.item.token_required).ljust(3, " "))
                msg += " 供應數量: {}\n".format(str(products.amount).ljust(3, " ")
                                            if products.amount > 0 else "無限".ljust(3, " "))
            msg += "```"
            await ctx.send(msg)

    @shop_group.command(name="buy")
    async def buy_item(self, ctx: commands.Command, count: int, item_name: str):
        result = InventoryUtil.buyShopitem(ctx.guild.id, ctx.author.id, item_name, count)
        if result == ErrorCode.CannotFindProduct:
            await ctx.send("沒有該項商品，請確認!")
        elif result == ErrorCode.LevelDoesNotReach:
            await ctx.send("等級不夠，無法購買!")
        elif result == ErrorCode.TokenDoesNotEnough:
            await ctx.send("雞腿不夠，無法購買!")
        elif result == ErrorCode.SupplyDoesNotEnough:
            await ctx.send("商品數量不足，無法購買!")
        else:
            await ctx.send(f"{count}個{result.item.name} 購買成功!")
        InventoryUtil.checkZeroAmount(ctx.guild.id)

    # 管理員用
    @shop_group.command(name="secret")
    async def list_items(self, ctx: commands.Command):
        msg = "```"
        msg += "如何新增?\n"
        msg += "\t1.先使用create來創立商品\n"
        msg += "\t2.把新建立的商品使用add上架販售\n"
        msg += "\n"
        msg += "指令集:\n"
        msg += "!shop add <數量> <商品名稱> 上架<商品名稱>到商店裡，若已存在則會增加供應量\n"
        msg += "!shop create <商品名稱> <道具類型> <增幅類型> <增幅數值> <增幅持續時間> <等級限制> <價錢> <商品描述> 新增一個Item\n"
        msg += "道具類型(1~5): 1.一般道具 2.攻擊道具 3.防禦道具 4.回復道具 5.狀態道具\n"
        msg += "增幅類型(1~4): 1.無 2.攻擊力 3.防禦力 4.魔法力 5.生命力\n"
        msg += "!shop change <新的供應數量> <商品名稱> 更改shopitem的供應量\n"
        msg += "!shop hidden <商品名稱> <商品隱藏與否(True為隱藏/False為顯示)>\n"
        msg += "!shop itemStatus <商品名稱> 確認item是否上架(或上架但隱藏)\n"
        msg += "!shop listItem 將目前創建好的item列出\n"
        msg += "!shop deleteItem <商品名稱> 刪除特定item\n"
        msg += "!shop clearAllItems 將目前創建好的所有item刪除(若已上架則會一併清除ShopItem)\n"
        msg += "!shop listHidden 顯示隱藏狀態的商品\n"
        msg += "\n\n"
        msg += "註1:change指令會直接改動目前供應數量，適用時機為\n"
        msg += "\t1.將無限量供應商品修正為有限供應，或\n"
        msg += "\t2.強制改動供應數量\n"
        msg += "註2:若add商品數量後menu中仍未發現商品，可使用itemStatus確認商品是否為隱藏狀態，若是則使用shop hidden顯示該項商品\n"
        msg += "```"
        await ctx.send(msg)

    @shop_group.command(name="exchange")
    async def exchange_token(self, ctx: commands.Command, need_token: int):
        member = MemberUtil.get_or_add_member(ctx.author.id)
        if member is None:
            await ctx.send("沒硬幣還想換雞腿，趕快去店外雜談區聊天賺硬幣!")
        else:
            coinspertoken = GamblingUtil.get_token_rate()
            spend = need_token * coinspertoken
            if member.coin > spend:
                MemberUtil.add_coin(member_id=member.id, amount=-spend)
                MemberUtil.add_token(member_id=member.id, amount=need_token)
                await ctx.send(f"成功兌換{need_token}個雞腿，目前剩下{member.coin}個硬幣")
            else:
                msg = f"兌換失敗!不足{spend - member.coin}個硬幣\n"
                msg += f"目前匯率為 一隻雞腿{coinspertoken}個硬幣"
                await ctx.send(msg)

    @shop_group.command(name="add")
    async def add_item(self, ctx: commands.Command, item_count: int, item_name: str):
        if item_count == 0:
            await ctx.send(f"新增數量為0?那你新增幹嘛?浪費我的時間")
        elif item_count < -1:
            await ctx.send(f"新增不能為負數，請重新輸入!")
        else:
            result = InventoryUtil.addItemToShop(ctx.guild.id, item_name, item_count)
            if result == -1:
                await ctx.send(f"{item_name}上架失敗!請確認商品名字是否正確!")
            elif result == -2:
                await ctx.send(f"{item_name}上架失敗!該物品目前無限量供應!")
            elif result == -3:
                await ctx.send(f"{item_name}目前限量存在，若需更改為無限量供應，請使用!shop change指令")
            else:
                if result.amount != item_count:
                    await ctx.send(f"{item_name}已存在{result.amount - item_count}個，已更新提供數量至{result.amount}個!")
                else:
                    await ctx.send(f"{item_count}個{item_name} 商品上架成功!")

    @shop_group.command(name="create")
    async def create_item(self, ctx: commands.Command, item_name: str, itemtype: int, buff_type: int, buff_value: int
                          , buff_round: int, level_required: int, price: int, description: str):
        if len(item_name) > 15:
            await ctx.send(f"名稱不可超過15個中英字元!")
        elif price < 0:
            await ctx.send(f"價錢不可為負!請重新輸入!")
        elif not 0 < itemtype < len(ItemType) + 1:
            await ctx.send(f"道具類型錯誤!請重新輸入!")
        elif not 0 < buff_type < len(BuffType) + 1:
            await ctx.send(f"增幅類型只有五種!請重新輸入!")
        elif buff_round < -1:
            await ctx.send(f"增幅持續時間不可為負數(-1為永遠不毀滅)!請重新輸入!")
        else:
            result = ItemUtil.createItem(ctx.guild.id, item_name, ItemType.list()[itemtype], BuffType.list()[buff_type], buff_value, buff_round, description
                                         , level_required, price)
            if result == -1:
                await ctx.send(item_name + ' 已經存在!')
            else:
                await ctx.send(item_name + ' 新增成功!')

    @shop_group.command(name="listItem")
    async def list_item(self, ctx: commands.Command):
        result = ItemUtil.ListAllItem(ctx.guild.id)
        if len(result) < 1:
            await ctx.send('目前沒有商品')
        else:
            msg = "```"
            for products in result:
                msg += " 購買ID: {}".format(str(products.id).ljust(3, " "))
                msg += " 商品名稱: {}".format(products.name).ljust(15, " ")
                msg += " 等級限制: {}".format(str(products.level_required).ljust(3, " "))
                msg += " 價格: {}\n".format(str(products.token_required).ljust(3, " "))
            msg += "```"
            await ctx.send(msg)

    @shop_group.command(name="token")
    async def get_user_token(self, ctx: commands.Command):
        member = MemberUtil.get_or_add_member(ctx.author.id)
        if member is None:
            await ctx.send(f"你目前擁有0個雞腿")
        else:
            await ctx.send(f"你目前擁有{member.token}個雞腿")

    @shop_group.command(name="change")
    async def change_shopitem_amount(self, ctx: commands.Command, amount: int, item_name: str):
        if amount < -1:
            await ctx.send("商品供應數量不能為負數!")
        else:
            result = InventoryUtil.changeSupplyAmount(ctx.guild.id, item_name, amount)
            if result == -1:
                await ctx.send("查無此項目，請確認商品名稱是否輸入錯誤!")
            elif result == -2:
                await ctx.send("該商品存在但尚未上架!")
            else:
                if amount == 0:
                    await ctx.send("數量為0，建議下架商品實在點")
                else:
                    await ctx.send(f"修改成功! 目前{item_name}供給數量已改成{result.amount}")

    @shop_group.command(name="hidden")
    async def change_shopitemHidden_status(self, ctx: commands.Command, item_name: str, hidden: bool):
        result = InventoryUtil.changeShopitemHiddenStatus(ctx.guild.id, item_name, hidden)
        if result == -1:
            await ctx.send("查無此項目，請確認商品名稱是否輸入錯誤!")
        elif result == -2:
            await ctx.send("該商品存在但尚未上架!")
        else:
            if hidden == True:
                await ctx.send(f"修改成功! 目前{item_name}狀態改為隱藏")
            else:
                await ctx.send(f"修改成功! 目前{item_name}供給數量為{result.amount}")

    @shop_group.command(name="itemStatus")
    async def check_Shopitem_status(self, ctx: commands.Command, item_name: str):
        result = InventoryUtil.checkShopitemStatus(ctx.guild.id, item_name)
        if result == -1:
            await ctx.send("查無此項目，請確認商品名稱是否輸入錯誤!")
        elif result == -2:
            await ctx.send(f"{item_name}存在但尚未上架!")
        else:
            msg = f"{item_name}已上架，狀態為"
            if result.hidden is True:
                msg += "隱藏"
            else:
                msg += "顯示"
            await ctx.send(msg)

    @shop_group.command(name="deleteItem")
    async def delete_item(self, ctx: commands.Command, item_name: str):
        result = ItemUtil.deleteItem(ctx.guild.id, item_name)
        if result == -1:
            await ctx.send("找不到該item，請確認名稱是否輸入錯誤!")
        else:
            await ctx.send(f"{item_name} 已被成功刪除!")

    @shop_group.command(name="clearAllItems")
    async def clear_all_items(self, ctx: commands.Command):
        ItemUtil.deleteItems(ctx.guild.id)
        await ctx.send("本群所有item清理結束")

    @shop_group.command(name="listHidden")
    async def list_hidden_shopItem(self, ctx: commands.Command):
        result = InventoryUtil.listHiddenShopItem(ctx.guild.id)
        if len(result) < 1:
            await ctx.send("沒有任何商品隱藏")
        else:
            msg = "```\n"
            for product in result:
                msg += product.item.name + "\n"
            msg += "```"
            await ctx.send(msg)

    @shop_group.command(name="detail")
    async def showShopitemDetail(self, ctx: commands.Command, item_name: str):
        item = ItemUtil.searchItem(guild_id=ctx.guild.id, item_name=item_name)
        if item is None:
            await ctx.send("找不到該商品，請確認名稱是否輸入錯誤!")
        result = InventoryUtil.findShopItem(ctx.guild.id, item)
        if result is None:
            await ctx.send("找不到該商品，請確認名稱是否輸入錯誤!")
        else:
            if result.item.type == ItemType.ATTACK:
                itemtype = "攻擊道具"
            elif result.item.type == ItemType.DEFENCE:
                itemtype = "防禦道具"
            elif result.item.type == ItemType.RECOVER:
                itemtype = "恢復道具"
            elif result.item.type == ItemType.STATUS:
                itemtype = "狀態道具"
            else:
                itemtype = "一般道具"

            if result.item.buff.buff_type == BuffType.ATTACK:
                bufftype = "攻擊力"
            elif result.item.buff.buff_type == BuffType.DEFENCE:
                bufftype = "防禦力"
            elif result.item.buff.buff_type == BuffType.MAGIC:
                bufftype = "魔法力"
            elif result.item.buff.buff_type == BuffType.HIT_POINT:
                bufftype = "生命力"
            else:
                bufftype = "無屬性"

            msg = "```"
            msg += f"商品名稱: {result.item.name}\n"
            msg += f"商品價錢: {result.item.token_required}\n"
            msg += f"等級限制: {result.item.level_required}\n"
            msg += f"道具種類: {itemtype}\n"
            msg += f"增幅種類: {bufftype}\n"
            msg += f"增幅數值: {result.item.buff.buff_value}\n"
            msg += "增幅時間: {}\n".format(result.item.buff.buff_round if result.item.buff.buff_round > 0 else "永不毀滅")
            msg += f"商品描述: {result.item.description}\n"
            msg += "```"
            await ctx.send(msg)


def setup(client):
    client.add_cog(Shop(client))
