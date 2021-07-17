from common.models.BaseModel import BaseModel
from peewee import *

class NicknameModel(BaseModel):
    id = AutoField() # nickname id
    guild_id = IntegerField() # guild user belongs
    member_id = IntegerField() # nick name owner id
    nick_name = CharField() # actual nick name value