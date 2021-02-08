from common.models.BaseModel import BaseModel
from peewee import *

class Channel(BaseModel):
    id = AutoField()
    channel_type = IntegerField()
    channel_discord_id = IntegerField()
