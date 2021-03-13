from common.models.BaseModel import BaseModel
from peewee import *

class Channel(BaseModel):
    id = AutoField()
    channel_type = IntegerField() # common/Util.ChannelType
    channel_guild_id = IntegerField()
    channel_id = IntegerField()
