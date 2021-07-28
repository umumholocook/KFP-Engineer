from common.models.InventoryRecord import Item
from common.RPGUtil.Buff import *
from enum import Enum
from common.customField.BuffField import BuffField


class ItemType(Enum):
    attackItem = 1
    defenceItem = 2
    RecoverItem = 3
    StatusItem = 4


class ItemUtil():

    def createItem(guild_id: int, item_name: str, itemtype: int, buff_type: int, buff_value: int, buff_round: int
                   , description: str = "無", level_required: int = 10, price: int = 10, role_id: int = -1):
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
                type=itemtype,
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
        Item.delete().where(
            Item.name == item_name
        ).execute()

    def deleteItems(guild_id: int):
        Item.delete().execute()

    def ListAllItem(guild_id: int):
        result = []
        query = Item.select().where(
            Item.guild_id == guild_id,
        )
        if query.exists():
            for record in query.iterator():
                result.append(record)
        return sorted(result, key=lambda x: x.id, reverse=False)
