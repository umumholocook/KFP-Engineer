from operator import le
from common.models.InventoryRecord import InventoryRecord, ShopItem
from common.models.InventoryRecord import Item
from common.MemberUtil import MemberUtil
from enum import Enum

class ErrorCode(Enum):
    CannotFindProduct = -1
    LevelDoesNotReach = -2
    TokenDoesNotEnough = -3
    SupplyDoesNotEnough = -4


class InventoryUtil():

    def addItemToShop(guild_id: int, item_name: str, amount: int = 1, hidden=False):
        item: Item = InventoryUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # does not exist item
        if item is None:
            return -1
        shopitem: ShopItem = InventoryUtil.findShopItem(guild_id=guild_id, item_id=item.id)
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

    def searchItem(guild_id: int, item_name: str):
        query = Item.select().where(
            Item.guild_id == guild_id,
            Item.name == item_name,
        )
        if query.exists():
            item: Item = query.get()
            return item
        return None

    def createItem(guild_id: int, item_name: str, level_required: int = 10, price: int = 10, role_id: int = -1):
        item = InventoryUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # item exist
        if item is not None:
            return -1
        return Item.create(
            guild_id=guild_id,
            name=item_name,
            role_id=role_id,
            token_required=price,
            level_required=level_required,
        )


    def createInventory(guild_id: int, user_id: int, item: Item, amount: int):
        return InventoryRecord.insert(
            guild_id=guild_id,
            user_id=user_id,
            item=item,
            amount=amount
        ).execute()



    def buyItem(guild_id: int, user_id: int, item_id: int, count: int):
        shopItem = InventoryUtil.findShopItem(guild_id=guild_id, item_id=item_id)

        # Cannot find products
        if shopItem is None:
            return ErrorCode.CannotFindProduct
        member = MemberUtil.get_or_add_member(user_id)
        # level does not reach the restrictions
        if member.rank < shopItem.item.level_required:
            return ErrorCode.LevelDoesNotReach
        # Token is less then price
        if member.token < (shopItem.item.token_required * count):
            return ErrorCode.TokenDoesNotEnough
        # Transaction part
        if shopItem.amount < count:
            return ErrorCode.SupplyDoesNotEnough
        # shopItem is unlimited supply
        elif shopItem.amount != -1:
            shopItem.amount -= count
            shopItem.save()
        # Reduce member's token
        spend = shopItem.item.token_required * count * -1
        MemberUtil.add_token(member_id=user_id, amount=spend)
        InventoryUtil.addItemToUserInventory(guild_id, user_id, item_id, count)
        return shopItem

    def checkZeroAmount(guild_id: int):
        result = InventoryUtil.ShopMenu(guild_id)
        for product in result:
            if product.amount == 0:
                InventoryUtil.changeItemHiddenStatus(guild_id, product.item.name, True)

    def findShopItem(guild_id: int, item_id: int):
        query = ShopItem.select().where(
            ShopItem.guild_id == guild_id,
            ShopItem.item_id == item_id,
        )
        if query.exists():
            shopItem: ShopItem = query.get()
            return shopItem
        return None

    def addItemToUserInventory(guild_id: int, user_id: int, item_id: int, count: int):
        itemRecord: InventoryRecord = InventoryUtil.findItemRecord(guild_id=guild_id, user_id=user_id, item_id=item_id)
        # if member does not have InventoryRecord
        if itemRecord:
            itemRecord.amount += count
            itemRecord.save()
        shopItem = InventoryUtil.findShopItem(guild_id=guild_id, item_id=item_id)
        InventoryUtil.createInventory(guild_id=guild_id, user_id=user_id, item=shopItem.item, amount=count)

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

    def findItemRecord(guild_id: int, user_id: int, item_id: int):
        query = InventoryRecord.select().where(
            InventoryRecord.guild_id == guild_id,
            InventoryRecord.user_id == user_id,
            InventoryRecord.item_id == item_id)
        if query.exists():
            itemRecord: InventoryRecord = query.get()
            return itemRecord
        return None

    def ListAllItem(guild_id: int):
        result = []
        query = Item.select().where(
            Item.guild_id == guild_id,
        )
        if query.exists():
            for record in query.iterator():
                result.append(record)
            for i in range(len(result)):
                for j in range(i,len(result)):
                    if result[i].id > result[j].id:
                        tmp = result[i]
                        result[i] = result[j]
                        result[j] = tmp
        return result

    def ShopMenu(guild_id: int):
        result = []
        query = ShopItem.select().where(
            ShopItem.hidden == False,
        )
        if query.exists():
            for record in query.iterator():
                result.append(record)
            for i in range(len(result)):
                for j in range(i, len(result)):
                    if result[i].item.id > result[j].item.id:
                        tmp = result[i]
                        result[i] = result[j]
                        result[j] = tmp
        return result

    def getUserToken(guild_id: int, user_id: int):
        member = MemberUtil.get_or_add_member(user_id)
        return member.token

    def changeSupplyAmount(guild_id: int, item_name: str, newAmount: int = 1):
        item: Item = InventoryUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # does not exist item
        if item is None:
            return -1
        shopitem: ShopItem = InventoryUtil.findShopItem(guild_id=guild_id, item_id=item.id)
        if shopitem is not None:
            shopitem.amount = newAmount
            shopitem.save()
            return shopitem
        else:
            return -2

    def changeItemHiddenStatus(guild_id: int, item_name: str, hidden: bool):
        item: Item = InventoryUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # does not exist item
        if item is None:
            return -1
        shopitem: ShopItem = InventoryUtil.findShopItem(guild_id=guild_id, item_id=item.id)
        if shopitem is not None:
            shopitem.hidden = hidden
            shopitem.save()
            return shopitem
        else:
            return -2

    def checkItemStatus(guild_id: int, item_name: str):
        item: Item = InventoryUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # does not exist item
        if item is None:
            return -1
        shopitem: ShopItem = InventoryUtil.findShopItem(guild_id=guild_id, item_id=item.id)
        if shopitem is not None:
            return shopitem
        else:
            return -2

    def deleteItem(guild_id: int, item_name: str):
        item = InventoryUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # does not exist item
        if item is None:
            return -1
        Item.delete().where(
            Item.name == item_name
        ).execute()

    def deleteItems(guild_id: int):
        Item.delete().execute()

    def listHiddenShopItem(guild_id: int):
        result = []
        query = ShopItem.select().where(
            ShopItem.guild_id == guild_id,
            ShopItem.hidden == True,
        )
        if query.exists():
            for record in query.iterator():
                result.append(record)
            for i in range(len(result)):
                for j in range(i, len(result)):
                    if result[i].item.id > result[j].item.id:
                        tmp = result[i]
                        result[i] = result[j]
                        result[j] = tmp
        return result
