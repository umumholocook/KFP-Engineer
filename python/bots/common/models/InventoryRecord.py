from common.models.BaseModel import BaseModel
from peewee import *

class Item(BaseModel):
    id = AutoField() # item id
    guild_id = IntegerField() # guild id
    name = CharField() # item name
    role_id = IntegerField() # any kind of role associate with this item
    token_required = IntegerField() # the token required to buy this item
    level_required = IntegerField() # the level required to buy this item
    hidden = BooleanField() # whether or not to hide this item

class InventoryRecord(BaseModel):
    id = AutoField() # record id
    guild_id = IntegerField() # guild id
    user_id = IntegerField() # user id
    item = ForeignKeyField(Item, backref='InventoryRecord')
    amount = IntegerField() # item amount

    
