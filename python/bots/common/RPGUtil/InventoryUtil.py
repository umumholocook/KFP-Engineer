from operator import le
from common.models.InventoryRecord import InventoryRecord, ShopItem
from common.models.InventoryRecord import Item
from common.MemberUtil import MemberUtil
from common.RPGUtil.ItemUtil import ItemUtil
from enum import Enum


class ErrorCode(Enum):
    CannotFindProduct = -1
    LevelDoesNotReach = -2
    TokenDoesNotEnough = -3
    SupplyDoesNotEnough = -4


class InventoryUtil():

    def addItemToShop(guild_id: int, item_name: str, amount: int = 1, hidden=False):
        item: Item = ItemUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # does not exist item
        if item is None:
            return -1
        shopitem: ShopItem = InventoryUtil.findShopItem(guild_id=guild_id, item=item)
        # if exists, add amount
        if shopitem is not None:
            # if is Unlimited supply, failed
            if shopitem.amount == -1:
                return -2
            else:
                if amount == -1:
                    return -3
                else:
                    shopitem.amount += amount
                    shopitem.save()
                    return shopitem
        elif item != -1:
            return ShopItem.create(
                guild_id=guild_id,
                item=item,
                amount=amount,
                hidden=hidden,
            )

    def createInventory(guild_id: int, user_id: int, item: Item, amount: int):
        return InventoryRecord.insert(
            guild_id=guild_id,
            user_id=user_id,
            item=item,
            amount=amount
        ).execute()

    def buyShopitem(guild_id: int, user_id: int, item_name: str, count: int):
        item: Item = ItemUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # does not exist item
        if item is None:
            return ErrorCode.CannotFindProduct

        shopItem = InventoryUtil.findShopItem(guild_id=guild_id, item=item)
        # Cannot find products
        if shopItem is None or shopItem.hidden is True:
            return ErrorCode.CannotFindProduct
        member = MemberUtil.get_or_add_member(user_id)
        # level does not reach the restrictions
        if member.rank < shopItem.item.level_required:
            return ErrorCode.LevelDoesNotReach
        # Token is less then price
        if member.token < (shopItem.item.token_required * count):
            return ErrorCode.TokenDoesNotEnough
        # Transaction part
        if shopItem.amount < count and shopItem.amount != -1:
            return ErrorCode.SupplyDoesNotEnough
        # shopItem is unlimited supply
        elif shopItem.amount != -1:
            shopItem.amount -= count
            shopItem.save()
        # Reduce member's token
        spend = shopItem.item.token_required * count * -1
        MemberUtil.add_token(member_id=user_id, amount=spend)
        InventoryUtil.addItemToUserInventory(guild_id, user_id, item, count)
        return shopItem

    def checkZeroAmount(guild_id: int):
        result = InventoryUtil.ShopMenu(guild_id)
        if result is not None:
            for product in result:
                if product.amount == 0:
                    InventoryUtil.changeShopitemHiddenStatus(guild_id, product.item.name, True)

    def findShopItem(guild_id: int, item: Item):
        query = ShopItem.select().where(
            ShopItem.guild_id == guild_id,
            ShopItem.item == item,
        )
        if query.exists():
            shopItem: ShopItem = query.get()
            return shopItem
        return None

    def addItemToUserInventory(guild_id: int, user_id: int, item: Item, count: int):
        itemRecord: InventoryRecord = InventoryUtil.findItemRecord(guild_id=guild_id, user_id=user_id, item=item)
        # if member does not have InventoryRecord
        if itemRecord:
            itemRecord.amount += count
            itemRecord.save()
        InventoryUtil.createInventory(guild_id=guild_id, user_id=user_id, item=item, amount=count)

    def getAllItemsBelongToUser(guild_id: int, user_id: int):
        result = []
        query = InventoryRecord.select().where(
            InventoryRecord.guild_id == guild_id,
            InventoryRecord.user_id == user_id)
        if query.exists():
            record: InventoryRecord
            for record in query.iterator():
                result.append(record)
        return result

    def findItemRecord(guild_id: int, user_id: int, item: Item):
        query = InventoryRecord.select().where(
            InventoryRecord.guild_id == guild_id,
            InventoryRecord.user_id == user_id,
            InventoryRecord.item == item)
        if query.exists():
            itemRecord: InventoryRecord = query.get()
            return itemRecord
        return None

    def ShopMenu(guild_id: int):
        result = []
        query = ShopItem.select().where(
            ShopItem.hidden == False,
        )
        if query.exists():
            for record in query.iterator():
                result.append(record)
        return sorted(result, key=lambda x: x.item.id, reverse=False)

    def changeSupplyAmount(guild_id: int, item_name: str, newAmount: int = 1):
        item: Item = ItemUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # does not exist item
        if item is None:
            return -1
        shopitem: ShopItem = InventoryUtil.findShopItem(guild_id=guild_id, item=item)
        if shopitem is not None:
            shopitem.amount = newAmount
            shopitem.save()
            return shopitem
        else:
            return -2

    def changeShopitemHiddenStatus(guild_id: int, item_name: str, hidden: bool):
        item: Item = ItemUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # does not exist item
        if item is None:
            return -1
        shopitem: ShopItem = InventoryUtil.findShopItem(guild_id=guild_id, item=item)
        if shopitem is not None:
            shopitem.hidden = hidden
            shopitem.save()
            return shopitem
        else:
            return -2

    def checkShopitemStatus(guild_id: int, item_name: str):
        item: Item = ItemUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # does not exist item
        if item is None:
            return -1
        shopitem: ShopItem = InventoryUtil.findShopItem(guild_id=guild_id, item=item)
        if shopitem is not None:
            return shopitem
        else:
            return -2

    def listHiddenShopItem(guild_id: int):
        result = []
        query = ShopItem.select().where(
            ShopItem.guild_id == guild_id,
            ShopItem.hidden == True,
        )
        if query.exists():
            for record in query.iterator():
                result.append(record)
        return sorted(result, key=lambda x: x.item.id, reverse=False)
