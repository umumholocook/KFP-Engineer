from operator import le
from common.models.InventoryRecord import InventoryRecord, ShopItem
from common.models.InventoryRecord import Item
from common.MemberUtil import MemberUtil
from common.GamblingUtil import GamblingUtil


class InventoryUtil():

    def addItemToShop(guild_id: int, item_name: str, amount: int = 1, hidden=False):
        item: Item = InventoryUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # does not exist item
        if item is None:
            return -1
        shopItem: ShopItem = InventoryUtil.findShopItem(guild_id=guild_id, item_id=item.id)
        # if exists, add amount
        if shopItem is not None:
            shopItem.amount += amount
            shopItem.save()
            return shopItem
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
            return -1
        member = MemberUtil.get_member(user_id)

        # level does not reach the restrictions

        # Token is less then price
        if member.token < (shopItem.item.token_required * count):
            return -2

        # Transaction part
        if shopItem.amount < count:
            return -3
        # shopItem is unlimited supply
        elif shopItem.amount != -1:
            shopItem.amount -= count
        # Reduce member's token
        spend = shopItem.item.token_required * count * -1
        MemberUtil.add_token(member_id=user_id, amount=spend)
        InventoryUtil.addItemToUserInventory(guild_id, user_id, item_id, count)
        return shopItem.item.name

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
        return result

    def ShopMenu(guild_id: int):
        result = []
        query = ShopItem.select()
        if query.exists():
            for record in query.iterator():
                result.append(record)
        return result

    def getUserToken(guild_id: int, user_id: int):
        member = MemberUtil.get_member(user_id)
        return member.token
