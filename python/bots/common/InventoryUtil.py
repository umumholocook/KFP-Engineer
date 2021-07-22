from operator import le
from common.models.InventoryRecord import InventoryRecord, ShopItem
from common.models.InventoryRecord import Item

class InventoryUtil():

    def addItemToShop(guild_id: int, item_name: str, amount: int = 1, hidden=False):
        item = InventoryUtil.createItem(guild_id=guild_id, item_name=item_name)
        ShopItem.create(
            guild_id=guild_id,
            item=item,
            amount=amount,
            hidden=hidden,
        )

    def createItem(guild_id: int, item_name: str, level_required: int = 10, price: int = 10, role_id: int = -1, hidden: bool = False):
        return Item.create(
            guild_id = guild_id,
            name = item_name,
            role_id = role_id,
            token_required = price,
            level_required = level_required,
            hidden = hidden,
        )
    
    def createInventory(guild_id: int, user_id: int, item: Item, amount: int):
        return InventoryRecord.create(
            guild_id = guild_id,
            user_id=user_id,
            item=item,
            amount=amount
        )

    def addItemToUserInventory(guild_id: int, user_id: int, item_id: int, count: int):
        itemRecord:InventoryRecord = InventoryUtil.findItemRecord(guild_id=guild_id, user_id=user_id, item_id=item_id)
        if not itemRecord:    
            itemRecord.amount += count
            itemRecord.save()
            return
        itemRecord = InventoryRecord.insert(
            guild_id = guild_id,
            user_id = user_id,
            item_id = item_id,
            amount = count
        ).execute()

    def getAvailableItems(guild_id: int):
        result = []
        query = Item.select().where(
            Item.guild_id == guild_id,
            Item.hidden == False)
        if query.exists():
            for record in query.iterator():
                result.append(record)
        return result
    
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
