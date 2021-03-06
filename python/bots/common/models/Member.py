from common.models.BaseModel import BaseModel
from peewee import *

class Member(BaseModel):
    member_id=IntegerField(primary_key=True) # INT PRIMARY KEY NOT NULL
    exp=IntegerField(default=0) # INT NOT NULL
    rank=BigIntegerField(default=0, null = True) # BITINT
    coin=BigIntegerField(default=0, null = True) # BITINT
    pure=IntegerField(default=0, null = True) # INT
