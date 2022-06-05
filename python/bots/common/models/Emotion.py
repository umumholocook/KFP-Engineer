from common.models.BaseModel import BaseModel
from peewee import *

# Use this object to keep track 
# which leaderboard is tracking what emotion
class Emotion(BaseModel):
    id = AutoField() # emotion id
    leaderboard_id = IntegerField() # leaderboard id
    emoji = CharField() # the actual emoji to track
    