import common.models.BaseModel as db
from common.models.BaseModel import BaseModel
from peewee import *

class Member(BaseModel):
    member_id=AutoField() # INT PRIMARY KEY NOT NULL
    exp=IntegerField(default=0) # INT NOT NULL
    rank=BigIntegerField(default=0, null = True) # BITINT
    item_id_list=IntegerField(default='[]') # INT NOT NULL
    coin=BigIntegerField(default=0, null = True) # BITINT
    special_item_id_list=BigIntegerField(default='[]') # BIGINT NOT NULL
    extra_avator_image=BlobField(default=None, null = True) # BLOB,
    pure=IntegerField(default=None, null = True) # INT
