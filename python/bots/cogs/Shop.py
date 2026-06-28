import discord
from common.RPGUtil.ItemType import ItemType
from common.RPGUtil.Buff import BuffType
from common.RPGUtil.InventoryUtil import InventoryUtil, ErrorCode
from common.RPGUtil.ItemUtil import ItemUtil
from discord import app_commands
from discord.ext import commands
from common.MemberUtil import MemberUtil
from common.GamblingUtil import GamblingUtil


@app_commands.guild_only()
class Shop(commands.GroupCog, group_name="商店", group_description="KFP炸機店小賣部"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="菜單", description="展示目前販賣中的商品")
    async def show_menu(self, interaction: discord.Interaction):
        result = InventoryUtil.ShopMenu(interaction.guild.id)
        if len(result) < 1:
            await interaction.response.send_message("目前商品都被買光了!")
        else:
            msg = "```\n"
            msg += "{:^63}".format("===商品價目表===")
            msg += "\n"
            for products in result:
                msg += " 購買ID: {}".format(str(products.item.id).ljust(3, " "))
                msg += " 商品名稱: {}".format(products.item.name).ljust(15, " ")
                msg += " 等級限制: {}".format(str(products.item.level_required).ljust(3, " "))
                msg += " 價格: {}".format(str(products.item.token_required).ljust(3, " "))
                msg += " 供應數量: {}\n".format(
                    str(products.amount).ljust(3, " ") if products.amount > 0 else "無限".ljust(3, " ")
                )
            msg += "```"
            await interaction.response.send_message(msg)

    @app_commands.command(name="購買", description="購買指定數量的商品")
    @app_commands.describe(count="購買數量", item_name="商品名稱")
    async def buy_item(self, interaction: discord.Interaction, count: int, item_name: str):
        result = InventoryUtil.buyShopitem(interaction.guild.id, interaction.user.id, item_name, count)
        if result == ErrorCode.CannotFindProduct:
            await interaction.response.send_message("沒有該項商品，請確認!")
        elif result == ErrorCode.LevelDoesNotReach:
            await interaction.response.send_message("等級不夠，無法購買!")
        elif result == ErrorCode.TokenDoesNotEnough:
            await interaction.response.send_message("雞腿不夠，無法購買!")
        elif result == ErrorCode.SupplyDoesNotEnough:
            await interaction.response.send_message("商品數量不足，無法購買!")
        else:
            await interaction.response.send_message(f"{count}個{result.item.name} 購買成功!")
        InventoryUtil.checkZeroAmount(interaction.guild.id)

    @app_commands.command(name="兌換", description="用硬幣兌換雞腿")
    @app_commands.describe(need_token="欲兌換的雞腿數量")
    async def exchange_token(self, interaction: discord.Interaction, need_token: int):
        member = MemberUtil.get_or_add_member(interaction.user.id)
        if member is None:
            await interaction.response.send_message("沒硬幣還想換雞腿，趕快去店外雜談區聊天賺硬幣!")
        else:
            coinspertoken = GamblingUtil.get_token_rate()
            spend = need_token * coinspertoken
            if member.coin > spend:
                MemberUtil.subtract_coin(member, spend)
                MemberUtil.add_token_to_member(member, need_token)
                await interaction.response.send_message(
                    f"成功以匯率一隻雞腿{coinspertoken}個硬幣兌換{need_token}個雞腿，目前剩下{member.coin}個硬幣"
                )
            else:
                msg = f"兌換失敗!不足{spend - member.coin}個硬幣\n"
                msg += f"目前匯率為 一隻雞腿{coinspertoken}個硬幣"
                await interaction.response.send_message(msg)

    @app_commands.command(name="雞腿", description="顯示目前擁有的雞腿數量")
    async def get_user_token(self, interaction: discord.Interaction):
        member = MemberUtil.get_or_add_member(interaction.user.id)
        if member is None:
            await interaction.response.send_message("你目前擁有0個雞腿")
        else:
            await interaction.response.send_message(f"你目前擁有{member.token}個雞腿")

    @app_commands.command(name="詳情", description="列出商品詳細資料")
    @app_commands.describe(item_name="商品名稱")
    async def show_shopitem_detail(self, interaction: discord.Interaction, item_name: str):
        item = ItemUtil.searchItem(guild_id=interaction.guild.id, item_name=item_name)
        if item is None:
            await interaction.response.send_message("找不到該商品，請確認名稱是否輸入錯誤!")
            return
        result = InventoryUtil.findShopItem(interaction.guild.id, item)
        if result is None:
            await interaction.response.send_message("找不到該商品，請確認名稱是否輸入錯誤!")
            return

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

        bufftype = Shop._get_buff_type(result.item.buff.buff_type)

        msg = "```"
        msg += f"商品名稱: {result.item.name}\n"
        msg += f"商品價錢: {result.item.token_required}\n"
        msg += "等級限制: {}\n".format(
            result.item.level_required if result.item.level_required > 0 else "無限制"
        )
        msg += f"道具種類: {itemtype}\n"
        msg += f"增幅種類: {bufftype}\n"
        msg += f"增幅數值: {result.item.buff.buff_value}\n"
        msg += "增幅時間: {}\n".format(
            f"{result.item.buff.buff_round}回合" if result.item.buff.buff_round > 0 else "無限制"
        )
        msg += f"商品描述: {result.item.description}\n"
        msg += "```"
        await interaction.response.send_message(msg)

    # --- 管理員指令 ---

    @app_commands.command(name="管理說明", description="商店管理員指令說明")
    @app_commands.default_permissions(administrator=True)
    async def list_items(self, interaction: discord.Interaction):
        msg = "```"
        msg += "如何新增?\n"
        msg += "\t1.先使用建立來創立商品\n"
        msg += "\t2.把新建立的商品使用上架販售\n"
        msg += "\n"
        msg += "指令集:\n"
        msg += "/商店 上架 <數量> <商品名稱> 上架<商品名稱>到商店裡，若已存在則會增加供應量\n"
        msg += "/商店 建立 <商品名稱> <道具類型> <增幅類型> <增幅數值> <增幅持續時間> <等級限制> <價格> <商品描述> 新增一個Item\n"
        msg += "道具類型(1~5): 1.一般道具 2.攻擊道具 3.防禦道具 4.回復道具 5.狀態道具\n"
        msg += "增幅類型(1~5): 1.無 2.攻擊力 3.防禦力 4.魔法力 5.生命力\n\n"
        msg += "範例: /商店 建立 蘋果 1 5 10 0 0 10 一顆蘋果\n\n"
        msg += "/商店 修改數量 <新的供應數量> <商品名稱> 更改shopitem的供應量\n"
        msg += "/商店 隱藏 <商品名稱> <商品隱藏與否(True為隱藏/False為顯示)>\n"
        msg += "/商店 狀態 <商品名稱> 確認item是否上架(或上架但隱藏)\n"
        msg += "/商店 物品列表 將目前創建好的item列出\n"
        msg += "/商店 刪除 <商品名稱> 刪除特定item\n"
        msg += "/商店 清空全部 將目前創建好的所有item刪除(若已上架則會一併清除ShopItem)\n"
        msg += "/商店 隱藏列表 顯示隱藏狀態的商品\n"
        msg += "/商店 更新屬性 <商品名稱> <商品屬性> <新的數值> 商品屬性為[道具類型,增幅類型,增幅數值,增幅持續時間,等級限制,價格,商品描述]其中之一"
        msg += "\n\n"
        msg += "註1:修改數量指令會直接改動目前供應數量，適用時機為\n"
        msg += "\t1.將無限量供應商品修正為有限供應，或\n"
        msg += "\t2.強制改動供應數量\n"
        msg += "註2:若上架商品數量後菜單中仍未發現商品，可使用狀態確認商品是否為隱藏狀態，若是則使用隱藏顯示該項商品\n"
        msg += "```"
        await interaction.response.send_message(msg)

    @app_commands.command(name="上架", description="上架商品到商店")
    @app_commands.describe(item_count="上架數量", item_name="商品名稱")
    @app_commands.default_permissions(administrator=True)
    async def add_item(self, interaction: discord.Interaction, item_count: int, item_name: str):
        if item_count == 0:
            await interaction.response.send_message("新增數量為0?那你新增幹嘛?浪費我的時間")
        elif item_count < -1:
            await interaction.response.send_message("新增不能為負數，請重新輸入!")
        else:
            result = InventoryUtil.addItemToShop(interaction.guild.id, item_name, item_count)
            if result == -1:
                await interaction.response.send_message(f"{item_name}上架失敗!請確認商品名字是否正確!")
            elif result == -2:
                await interaction.response.send_message(f"{item_name}上架失敗!該物品目前無限量供應!")
            elif result == -3:
                await interaction.response.send_message(
                    f"{item_name}目前限量存在，若需更改為無限量供應，請使用/商店 修改數量指令"
                )
            else:
                if result.amount != item_count:
                    await interaction.response.send_message(
                        f"{item_name}已存在{result.amount - item_count}個，已更新提供數量至{result.amount}個!"
                    )
                else:
                    await interaction.response.send_message(f"{item_count}個{item_name} 商品上架成功!")

    @app_commands.command(name="建立", description="新增一個商品 Item")
    @app_commands.describe(
        item_name="商品名稱",
        itemtype="道具類型(1~5)",
        buff_type="增幅類型(1~5)",
        buff_value="增幅數值",
        buff_round="增幅持續時間(-1為永遠)",
        level_required="等級限制",
        price="價格",
        description="商品描述",
    )
    @app_commands.default_permissions(administrator=True)
    async def create_item(
        self,
        interaction: discord.Interaction,
        item_name: str,
        itemtype: int,
        buff_type: int,
        buff_value: int,
        buff_round: int,
        level_required: int,
        price: int,
        description: str,
    ):
        if len(item_name) > 15:
            await interaction.response.send_message("名稱不可超過15個中英字元!")
        elif price < 0:
            await interaction.response.send_message("價錢不可為負!請重新輸入!")
        elif not 0 < itemtype < len(ItemType) + 1:
            await interaction.response.send_message("道具類型錯誤!請重新輸入!")
        elif not 0 < buff_type < len(BuffType) + 1:
            await interaction.response.send_message(f"增幅類型只有{len(BuffType)}種!請重新輸入!")
        elif buff_round < -1:
            await interaction.response.send_message("增幅持續時間不可為負數(-1為永遠不毀滅)!請重新輸入!")
        else:
            result = ItemUtil.createItem(
                interaction.guild.id,
                item_name,
                ItemType.list()[itemtype - 1],
                BuffType.list()[buff_type - 1],
                buff_value,
                buff_round,
                description,
                level_required,
                price,
            )
            if result == -1:
                await interaction.response.send_message(item_name + " 已經存在!")
            else:
                await interaction.response.send_message(item_name + " 新增成功!")

    @app_commands.command(name="物品列表", description="列出目前創建好的所有 item")
    @app_commands.default_permissions(administrator=True)
    async def list_item(self, interaction: discord.Interaction):
        result = ItemUtil.ListAllItem(interaction.guild.id)
        if len(result) < 1:
            await interaction.response.send_message("目前沒有商品")
        else:
            msg = "```"
            for products in result:
                msg += " 購買ID: {}".format(str(products.id).ljust(3, " "))
                msg += " 商品名稱: {}".format(products.name).ljust(15, " ")
                msg += " 等級限制: {}".format(str(products.level_required).ljust(3, " "))
                msg += " 價格: {}\n".format(str(products.token_required).ljust(3, " "))
            msg += "```"
            await interaction.response.send_message(msg)

    @app_commands.command(name="修改數量", description="更改 shopitem 的供應量")
    @app_commands.describe(amount="新的供應數量", item_name="商品名稱")
    @app_commands.default_permissions(administrator=True)
    async def change_shopitem_amount(self, interaction: discord.Interaction, amount: int, item_name: str):
        if amount < -1:
            await interaction.response.send_message("商品供應數量不能為負數!")
        else:
            result = InventoryUtil.changeSupplyAmount(interaction.guild.id, item_name, amount)
            if result == -1:
                await interaction.response.send_message("查無此項目，請確認商品名稱是否輸入錯誤!")
            elif result == -2:
                await interaction.response.send_message("該商品存在但尚未上架!")
            else:
                if amount == 0:
                    await interaction.response.send_message("數量為0，建議下架商品實在點")
                else:
                    await interaction.response.send_message(f"修改成功! 目前{item_name}供給數量已改成{result.amount}")

    @app_commands.command(name="隱藏", description="設定商品是否隱藏")
    @app_commands.describe(item_name="商品名稱", hidden="True 為隱藏，False 為顯示")
    @app_commands.default_permissions(administrator=True)
    async def change_shopitem_hidden_status(
        self, interaction: discord.Interaction, item_name: str, hidden: bool
    ):
        result = InventoryUtil.changeShopitemHiddenStatus(interaction.guild.id, item_name, hidden)
        if result == -1:
            await interaction.response.send_message("查無此項目，請確認商品名稱是否輸入錯誤!")
        elif result == -2:
            await interaction.response.send_message("該商品存在但尚未上架!")
        else:
            if hidden:
                await interaction.response.send_message(f"修改成功! 目前{item_name}狀態改為隱藏")
            else:
                await interaction.response.send_message(f"修改成功! 目前{item_name}供給數量為{result.amount}")

    @app_commands.command(name="狀態", description="確認商品是否上架")
    @app_commands.describe(item_name="商品名稱")
    @app_commands.default_permissions(administrator=True)
    async def check_shopitem_status(self, interaction: discord.Interaction, item_name: str):
        result = InventoryUtil.checkShopitemStatus(interaction.guild.id, item_name)
        if result == -1:
            await interaction.response.send_message("查無此項目，請確認商品名稱是否輸入錯誤!")
        elif result == -2:
            await interaction.response.send_message(f"{item_name}存在但尚未上架!")
        else:
            msg = f"{item_name}已上架，狀態為"
            if result.hidden is True:
                msg += "隱藏"
            else:
                msg += "顯示"
            await interaction.response.send_message(msg)

    @app_commands.command(name="刪除", description="刪除特定 item")
    @app_commands.describe(item_name="商品名稱")
    @app_commands.default_permissions(administrator=True)
    async def delete_item(self, interaction: discord.Interaction, item_name: str):
        result = ItemUtil.deleteItem(interaction.guild.id, item_name)
        if result == -1:
            await interaction.response.send_message("找不到該item，請確認名稱是否輸入錯誤!")
        else:
            await interaction.response.send_message(f"{item_name} 已被成功刪除!")

    @app_commands.command(name="清空全部", description="刪除本群所有 item")
    @app_commands.default_permissions(administrator=True)
    async def clear_all_items(self, interaction: discord.Interaction):
        InventoryUtil.deleteShopItems(interaction.guild.id)
        ItemUtil.deleteItems(interaction.guild.id)
        await interaction.response.send_message("本群所有item清理結束")

    @app_commands.command(name="隱藏列表", description="顯示隱藏狀態的商品")
    @app_commands.default_permissions(administrator=True)
    async def list_hidden_shop_item(self, interaction: discord.Interaction):
        result = InventoryUtil.listHiddenShopItem(interaction.guild.id)
        if len(result) < 1:
            await interaction.response.send_message("沒有任何商品隱藏")
        else:
            msg = "```\n"
            for product in result:
                msg += product.item.name + "\n"
            msg += "```"
            await interaction.response.send_message(msg)

    @app_commands.command(name="更新屬性", description="更新商品屬性")
    @app_commands.describe(item_name="商品名稱", item_property="商品屬性", new_value="新的數值")
    @app_commands.choices(
        item_property=[
            app_commands.Choice(name="道具類型", value="道具類型"),
            app_commands.Choice(name="增幅類型", value="增幅類型"),
            app_commands.Choice(name="增幅數值", value="增幅數值"),
            app_commands.Choice(name="增幅持續時間", value="增幅持續時間"),
            app_commands.Choice(name="等級限制", value="等級限制"),
            app_commands.Choice(name="價格", value="價格"),
            app_commands.Choice(name="商品描述", value="商品描述"),
        ]
    )
    @app_commands.default_permissions(administrator=True)
    async def update_item_detail(
        self, interaction: discord.Interaction, item_name: str, item_property: str, new_value: str
    ):
        item = ItemUtil.searchItem(guild_id=interaction.guild.id, item_name=item_name)
        if item is None:
            await interaction.response.send_message("找不到該商品，請確認名稱是否輸入錯誤!")
            return
        result = InventoryUtil.findShopItem(interaction.guild.id, item)
        if result is None:
            await interaction.response.send_message("找不到該商品，請確認名稱是否輸入錯誤!")
            return

        if item_property == "道具類型":
            try:
                value = int(new_value)
                if value < 0 or value > 5:
                    await interaction.response.send_message(
                        "道具類型只能為數字1-5:\n1.一般道具 2.攻擊道具 3.防禦道具 4.回復道具 5.狀態道具"
                    )
                    return
                ItemUtil.updateItemType(item, ItemType.list()[value - 1])
                await interaction.response.send_message(
                    f"道具'{item.name}'類型已更新為 '{ItemType.list()[value - 1]}'"
                )
                return
            except ValueError:
                await interaction.response.send_message(
                    "道具類型只能為數字1-5:\n1.一般道具 2.攻擊道具 3.防禦道具 4.回復道具 5.狀態道具"
                )
                return
        if item_property == "增幅類型":
            try:
                value = int(new_value)
                if value < 0 or value > 5:
                    await interaction.response.send_message(
                        "增幅類型只能為數字(1~5):\n1.無 2.攻擊力 3.防禦力 4.魔法力 5.生命力"
                    )
                    return
                ItemUtil.updateItemBuffType(item, BuffType.list()[value - 1])
                await interaction.response.send_message(
                    f"道具'{item.name}'增幅類型已更新為 '{Shop._get_buff_type(BuffType.list()[value - 1])}'"
                )
                return
            except ValueError:
                await interaction.response.send_message(
                    "增幅類型只能為數字(1~5):\n1.無 2.攻擊力 3.防禦力 4.魔法力 5.生命力"
                )
                return
        if item_property == "增幅數值":
            try:
                value = int(new_value)
                ItemUtil.updateItemBuffValue(item, value)
                await interaction.response.send_message(f"道具'{item.name}'增幅數值已更新為 '{value}'")
                return
            except ValueError:
                await interaction.response.send_message("增幅數值只能為數字.")
                return
        if item_property == "增幅持續時間":
            try:
                value = int(new_value)
                if value < 0:
                    await interaction.response.send_message("增幅持續時間只能為正整數.")
                    return
                ItemUtil.updateItemBuffRound(item, value)
                await interaction.response.send_message(f"道具'{item.name}'增幅持續時間已更新為 '{value}'")
                return
            except ValueError:
                await interaction.response.send_message("增幅持續時間只能為數字.")
                return
        if item_property == "等級限制":
            try:
                value = int(new_value)
                if value < 0:
                    await interaction.response.send_message("等級限制只能為正整數.")
                    return
                ItemUtil.updateItemLevelLimit(item, value)
                await interaction.response.send_message(f"道具'{item.name}'等級限制已更新為 '{value}'")
                return
            except ValueError:
                await interaction.response.send_message("等級限制只能為數字.")
                return
        if item_property == "價格":
            try:
                value = int(new_value)
                if value < 0:
                    await interaction.response.send_message("價格只能為正整數.")
                    return
                ItemUtil.updateItemPrice(item, value)
                await interaction.response.send_message(f"道具'{item.name}'價格已更新為 '{value}'")
                return
            except ValueError:
                await interaction.response.send_message("商品價格只能為數字.")
                return
        if item_property == "商品描述":
            ItemUtil.updateItemDescription(item, new_value)
            await interaction.response.send_message(f"道具'{item.name}'描述已更新完成")
            return

    @staticmethod
    def _get_buff_type(buff_type: str) -> str:
        buff_type_enum = BuffType[buff_type]
        if buff_type_enum == BuffType.ATTACK:
            return "攻擊力"
        elif buff_type_enum == BuffType.DEFENCE:
            return "防禦力"
        elif buff_type_enum == BuffType.MAGIC:
            return "魔法力"
        elif buff_type_enum == BuffType.HIT_POINT:
            return "生命力"
        else:
            return "無屬性"


async def setup(client):
    await client.add_cog(Shop(client))