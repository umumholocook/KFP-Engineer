from common.models.BaseModel import BaseModel
from peewee import *

# This is a simple data object for Leaderboard
# This object contains only name
class Leaderboard(BaseModel):
    id = AutoField()
    name = CharField() # name of leaderboard