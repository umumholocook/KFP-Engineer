from common.models.BaseModel import BaseModel
from peewee import *

attrs = {
    "member_id": AutoField(), # INT PRIMARY KEY NOT NULL
    "xp": IntegerField(), # INT NOT NULL
    "rank": BigIntegerField(null = True), # BITINT
    "item_id_list": IntegerField(), # INT NOT NULL
    "normal_coin": BigIntegerField(null = True), # BITINT
    "special_item_id_list": BigIntegerField(), # BIGINT NOT NULL
    "extra_avator_image": BlobField(null = True), # BLOB,
    "pure": IntegerField(null = True), # INT
}

Model_Cache = {}

def make_table_name(guild_id:int):
    return "server_{}".format(guild_id)

def get_model(table_name:str):
    return type(table_name, (BaseModel, ), attrs)

class Member:
    # For test only, do not use
    def get_all_tables():
        return Model_Cache.values()
    
    def get_tabel(guild_id:int):
        tableName = make_table_name(guild_id)
        if tableName in Model_Cache:
            return Model_Cache[tableName]
        else:
            raise ValueError("Table {} does not exist".format(tableName))
    
    def create_table(guild_id:int):
        tableName = make_table_name(guild_id)
        model = get_model(tableName)
        model.create_table()
        Model_Cache[tableName] = model
        print("table {} is created".format(tableName))
