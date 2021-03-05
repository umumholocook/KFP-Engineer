from common.models.BaseModel import BaseModel
from peewee import *

class PermissionRole(BaseModel):
    id = AutoField()
    guild_id = IntegerField() #群id
    role_id = IntegerField() #身分id 
    role_type = IntegerField() #身分組的種類