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

class Member:
    # For test only, do not use
    def get_all_tables():
        return Model_Cache.values()
    
    def get_table(guild_id:int):
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
    
    def get_member_row(guild_id:int, member_id:int):
        return Member.get_table(guild_id).get(member_id=member_id)

    def add_member(guild_id:int, member_id:int):
        table = Member.get_table(guild_id)
        member = table.create(member_id=member_id)
        member.save()
        
    def add_members(guild_id:int, member_ids):
        table = Member.get_table(guild_id)
        with db.proxy.atomic():
            for member_id in member_ids:
                table.create(member_id=member_id)

