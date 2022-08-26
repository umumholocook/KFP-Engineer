from common.models.BaseModel import BaseModel
from peewee import *

class RouletteGame(BaseModel):
    id = AutoField() # roulette game id
    guild_id = IntegerField() # guild this game belongs to
    channel_id = IntegerField() # the channel this game is initiated with
    expire_time = DateTimeField() # the time this game should expire
    winning_number = IntegerField() # the winning number of this game, -1 if not finished.
    