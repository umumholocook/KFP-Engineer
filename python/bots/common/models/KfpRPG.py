from common.models.BaseModel import BaseModel
from common.models.Member import Member
from peewee import *

class Character(BaseModel):
    id = AutoField()
    character = ForeignKeyField(Member, backref='characters')

    hp_current = IntegerField()
    hp_max = IntegerField()
    mp_current = IntegerField()
    mp_max = IntegerField()

class Gear(BaseModel):
    pass

