from common.models.BaseModel import BaseModel
from common.customField.BuffField import BuffField
from peewee import *

class RPGStatus(BaseModel):
    id = AutoField() # PRIMARY KEY AUTO-INCREMENT
    member_id = IntegerField() # The character id this status assoticated with
    guild_id = IntegerField() # The guild this member belongs to
    type = IntegerField() # the type of this status
    buff = BuffField()  # side effect
    expire_time = DateTimeField() # time of this status expiration