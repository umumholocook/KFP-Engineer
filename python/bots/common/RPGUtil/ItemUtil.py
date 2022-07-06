from common.RPGUtil import InventoryUtil
from common.RPGUtil.ItemType import ItemType
from common.models.InventoryRecord import Item
from common.RPGUtil.Buff import *

class ItemUtil():

    def createItem(guild_id: int, item_name: str, item_type: ItemType = ItemType.NONE, buff_type: BuffType = BuffType.NONE, buff_value: int = 0, buff_round: int = -1
                   , description: str = "", level_required: int = 10, price: int = 10, role_id: int = -1):
        item = ItemUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # item exist
        if item is not None:
            return -1
        else:
            buff = Buff(buff_type=buff_type, buff_value=buff_value, buff_round=buff_round)
            return Item.create(
                guild_id=guild_id,
                name=item_name,
                role_id=role_id,
                token_required=price,
                level_required=level_required,
                type=item_type,
                buff=buff,
                description=description
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

    def deleteItem(guild_id: int, item_name: str):
        item = ItemUtil.searchItem(guild_id=guild_id, item_name=item_name)
        # does not exist item
        if item is None:
            return -1
        shopItem = InventoryUtil.findShopItem(guild_id=guild_id, item=item)
        if shopItem is not None:
            InventoryUtil.deleteShopItem(guild_id=guild_id, item=item)
        Item.delete().where(
            Item.name == item_name,
            Item.guild_id == guild_id
        ).execute()

    def deleteItems(guild_id: int):
        Item.delete().where(Item.guild_id == guild_id).execute()

    def ListAllItem(guild_id: int):
        result = []
        query = Item.select().where(
            Item.guild_id == guild_id,
        )
        if query.exists():
            for record in query.iterator():
                result.append(record)
        return sorted(result, key=lambda x: x.id, reverse=False)
        
    def updateItemType(item: Item, new_type: ItemType):
        item.type = new_type
        item.save()
    
    def updateItemBuffType(item: Item, new_buff_type: BuffType):
        item.buff.buff_type = new_buff_type
        item.save()
    
    def updateItemBuffValue(item: Item, new_buff_value: int):
        item.buff.buff_value = new_buff_value
        item.save()
    
    def updateItemBuffRound(item: Item, new_buff_round: int):
        item.buff.buff_round = new_buff_round
        item.save()
    
    def updateItemLevelLimit(item: Item, new_level_limit: int):
        item.level_required = new_level_limit
        item.save()
    
    def updateItemPrice(item: Item, new_price: int):
        item.token_required = new_price
        item.save()
    
    def updateItemDescription(item: Item, new_description: str):
        item.description = new_description
        item.save()
