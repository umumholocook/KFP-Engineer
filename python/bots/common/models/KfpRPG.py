from common.models.BaseModel import BaseModel
from common.models.Member import Member
from common.models.InventoryRecord import Item
from peewee import *

class Character(BaseModel):
    id = AutoField()
    character = ForeignKeyField(Member, backref='characters')

    hp_current = IntegerField()
    hp_max = IntegerField()
    mp_current = IntegerField()
    mp_max = IntegerField()
    attack_basic = IntegerField()
    # attack_bonus = ForeignKeyField()
    defense_basic = IntegerField()
    # defense_bonus = ForeignKeyField()

class GearParts(Item):
    pass

class Gear(GearParts):
    pass
