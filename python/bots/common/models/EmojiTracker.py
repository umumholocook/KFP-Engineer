from common.models.BaseModel import BaseModel
from peewee import *

# Object that record user_id, leaderboard, and count
class EmojiTracker(BaseModel):
    id = AutoField() 
    member_id = IntegerField() # user
    leaderboard_id = IntegerField() # the leaderboard this track belongs to
    emotion_id = IntegerField() # the id of a emotion
    count = IntegerField() # actual count
    
    