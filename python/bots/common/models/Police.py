from common.models.BaseModel import BaseModel
from peewee import *

class Police(BaseModel):
    id = AutoField() # record id
    guild_id = IntegerField() # guild id
    member_id = IntegerField() # member id
    police_type = TextField() # the type of this police
    expire_time = DateTimeField() # time this is created
    stopped = BooleanField(default=False) # whether this police is disabled manually or not
