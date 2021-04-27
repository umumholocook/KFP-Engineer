from common.models.BaseModel import BaseModel
from peewee import *

class ReactionMessage(BaseModel):
    id = AutoField()
    message_type = IntegerField() # common/Util.ReactionType
    message_id = IntegerField()
    guild_id = IntegerField()
