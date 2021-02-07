import common.models.BaseModel as db
from common.models.BaseModel import BaseModel
from peewee import *

attrs = {
    "member_id": AutoField(), # INT PRIMARY KEY NOT NULL
    "xp": IntegerField(default=0), # INT NOT NULL
    "rank": BigIntegerField(default=0, null = True), # BITINT
    "item_id_list": IntegerField(default='[]'), # INT NOT NULL
    "normal_coin": BigIntegerField(default=0, null = True), # BITINT
    "special_item_id_list": BigIntegerField(default='[]'), # BIGINT NOT NULL
    "extra_avator_image": BlobField(default=None, null = True), # BLOB,
    "pure": IntegerField(default=None, null = True), # INT
}

Model_Cache = {}

def make_table_name(guild_id:int):
    return "server_{}".format(guild_id)

def get_model(table_name:str):
    return type(table_name, (BaseModel, ), attrs)

class Member(BaseModel):
    member_id=AutoField() # INT PRIMARY KEY NOT NULL
    xp=IntegerField(default=0) # INT NOT NULL
    rank=BigIntegerField(default=0, null = True) # BITINT
    item_id_list=IntegerField(default='[]') # INT NOT NULL
    normal_coin=BigIntegerField(default=0, null = True) # BITINT
    special_item_id_list=BigIntegerField(default='[]') # BIGINT NOT NULL
    extra_avator_image=BlobField(default=None, null = True) # BLOB,
    pure=IntegerField(default=None, null = True) # INT
