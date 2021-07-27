from common.InventoryUtil import InventoryUtil, ErrorCode
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
        msg += "!shop buy <購買ID> <購買數量> 購買指定數量的商品\n"
        msg += "!shop menu 展示目前販賣中的商品\n"
        msg += "!shop exchange <雞腿數量> 用硬幣兌換雞腿\n"
        msg += "!shop token 顯示目前擁有的雞腿數量\n"
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
                msg += " 供應數量: {}\n".format(str(products.item.token_required).ljust(3, " ")
                                            if type(products.item.token_required) is int else "無限".ljust(3, " "))
            msg += "```"
            await ctx.send(msg)

    @shop_group.command(name="buy")
    async def buy_item(self, ctx: commands.Command, count: int, item_index: int):
        result = InventoryUtil.buyItem(ctx.guild.id, ctx.author.id, item_index, count)
        InventoryUtil.checkZeroAmount(ctx.guild.id)
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

    # 管理員用
    @shop_group.command(name="secret")
    async def list_items(self, ctx: commands.Command):
        msg = "```"
        msg += "如何新增?\n"
        msg += "\t1.先使用create來創立商品\n"
        msg += "\t2.把新建立的商品使用add上架販售\n"
        msg += "\n"
        msg += "指令集:\n"
        msg += "!shop add <商品名稱> <數量> 上架item成為shopitem，若已存在則會增加供應量\n"
        msg += "!shop create <商品名稱> <等級限制> <價錢> 新增一個Item\n"
        msg += "!shop change <商品名稱> <新的供應數量> 更改shopitem的供應量\n"
        msg += "!shop hidden <商品名稱> <商品隱藏與否(True為隱藏/False為顯示)>\n"
        msg += "!shop itemStatus <商品名稱> 確認item是否上架(或上架但隱藏)"
        msg += "!shop listItem 將目前創建好的item列出\n"
        msg += "\n\n"
        msg += "註1:change指令會直接改動目前供應數量，適用時機為\n"
        msg += "\t1.將無限量供應商品修正為有限供應，或\n"
        msg += "\t2.強制改動供應數量\n"
        msg += "註2:若add商品數量後menu中仍未發現商品，可使用itemStatus確認商品是否為隱藏狀態，若是則使用shop hidden顯示該項商品\n"
        msg += "```"
        await ctx.send(msg)

    @shop_group.command(name="exchange")
    async def exchange_token(self, ctx: commands.Command, need_token: int):
        member = MemberUtil.get_member(ctx.author.id)
        if member is None:
            await ctx.send("沒硬幣還想換雞腿，真是笑死人了")
        else:
            coinspertoken = GamblingUtil.get_token_rate()
            spend = need_token * coinspertoken
            if member.coin > spend:
                MemberUtil.add_coin(member_id=member.id, amount=-spend)
                MemberUtil.add_token(member_id=member.id, amount=need_token)
                await ctx.send(f"成功兌換{need_token}個雞腿，目前剩下{member.coin}coins")
            else:
                msg = f"兌換失敗!不足{need_token * coinspertoken - coinspertoken}coins"
                msg += f"目前匯率為 一隻雞腿需要{coinspertoken}coins"
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
    async def create_item(self, ctx: commands.Command, item_name: str, level_required: int, price: int):
        if len(item_name) > 15:
            await ctx.send(f"名稱不可超過15個中英字元!")
        elif price < 0:
            await ctx.send(f"價錢不可為負!請重新輸入!")
        else:
            result = InventoryUtil.createItem(ctx.guild.id, item_name, level_required, price)
            if result == -1:
                await ctx.send(item_name + ' 已經存在!')
            else:
                await ctx.send(item_name + ' 新增成功!')

    @shop_group.command(name="listItem")
    async def list_item(self, ctx: commands.Command):
        result = InventoryUtil.ListAllItem(ctx.guild.id)
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
    async def change_itemHidden_status(self, ctx: commands.Command, item_name: str, hidden: bool):
        result = InventoryUtil.changeItemHiddenStatus(ctx.guild.id, item_name, hidden)
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
    async def check_item_status(self, ctx: commands.Command, item_name: str):
        result = InventoryUtil.checkItemStatus(ctx.guild.id, item_name)
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
        result = InventoryUtil.deleteItem(ctx.guild.id, item_name)
        if result == -1:
            await ctx.send("找不到該item，請確認名稱是否輸入錯誤!")
        else:
            await ctx.send(f"{item_name} 已被成功刪除!")

    @shop_group.command(name="deleteItems")
    async def delete_items(self, ctx: commands.Command, item_name: str):
        InventoryUtil.deleteItems(ctx.guild.id)
        await ctx.send("所有item已被成功刪除!")

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


def setup(client):
    client.add_cog(Shop(client))
