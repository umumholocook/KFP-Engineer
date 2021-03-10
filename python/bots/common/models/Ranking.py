from re import T
from common.models.BaseModel import BaseModel
from peewee import *

class Ranking(BaseModel):
    id = AutoField()
    rankingt_type = IntegerField()
    ranking_key = TextField()
    user_id = IntegerField()
    guild_id = IntegerField()
    count = IntegerField() 
    timestamp = DoubleField() #this will save python object 


