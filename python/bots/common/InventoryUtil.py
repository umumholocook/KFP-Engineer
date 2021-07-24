from operator import le
from common.models.InventoryRecord import InventoryRecord, ShopItem
from common.models.InventoryRecord import Item


class InventoryUtil():

    def addItemToShop(guild_id: int, item_name: str, amount: int = 1, hidden=False):
        try:
            item = InventoryUtil.searchItem(guild_id=guild_id, item_name=item_name)
            return ShopItem.create(
                guild_id=guild_id,
                item=item,
                amount=amount,
                hidden=hidden,
            )
        except:
            return -1


    def searchItem(guild_id: int, item_name: str):
        query = Item.select().where(
            Item.guild_id == guild_id,
            Item.name == item_name,
        )
        return query.get()

    def createItem(guild_id: int, item_name: str, level_required: int = 10, price: int = 10, role_id: int = -1,):
        return Item.create(
            guild_id=guild_id,
            name=item_name,
            role_id=role_id,
            token_required=price,
            level_required=level_required,
        )

    def createInventory(guild_id: int, user_id: int, item: Item, amount: int):
        return InventoryRecord.create(
            guild_id=guild_id,
            user_id=user_id,
            item=item,
            amount=amount
        )

    def addItemToUserInventory(guild_id: int, user_id: int, item_id: int, count: int):
        itemRecord: InventoryRecord = InventoryUtil.findItemRecord(guild_id=guild_id, user_id=user_id, item_id=item_id)
        if not itemRecord:
            itemRecord.amount += count
            itemRecord.save()
            return
        itemRecord = InventoryRecord.insert(
            guild_id=guild_id,
            user_id=user_id,
            item_id=item_id,
            amount=count
        ).execute()

    # def getAvailableItems(guild_id: int):
    #     result = []
    #     query = Item.select().where(
    #         Item.guild_id == guild_id,
    #         Item.hidden == False)
    #     if query.exists():
    #         for record in query.iterator():
    #             result.append(record)
    #     return result

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

    # def deleteItem(guild_id: int):
    #     try:
    #         query = Item.delete().where(
    #             Item.guild_id == guild_id
    #         )
    #         query.execute()
    #         return 1
    #     except:
    #         return -1
    #
    # def deleteMenu(guild_id: int):
    #     try:
    #         query = ShopItem.delete().where(
    #             ShopItem.guild_id == guild_id
    #         )
    #         query.execute()
    #         return 1
    #     except:
    #         return -1

    def ListAllItem(guild_id: int):
        result = []
        query = Item.select().where(
            Item.guild_id == guild_id,
        )
        if query.exists():
            for record in query.iterator():
                # print(record.index)
                result.append(record)
        return result

    def ShopMenu(guild_id: int):
        result = []
        query = ShopItem.select()
        if query.exists():
            for record in query.iterator():
                # print(record.index)
                result.append(record)
        return result
