from common.models.BaseModel import BaseModel
from peewee import *

class KfpRole(BaseModel):
    id = AutoField()
    guild_id = IntegerField()
    role_id = IntegerField()
    role_name = TextField()
    color = TextField()
    level = IntegerField(default = 0)
    category = IntegerField(default = 0)