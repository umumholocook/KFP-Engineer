import sqlite3
import common.models.BaseModel as db
from common.models.Member import Member
from peewee import SqliteDatabase

class KfpDb():

    def __init__(self, dbFile="./common/KFP_bot.db"):
        self.sqliteDb = SqliteDatabase(dbFile)
        db.proxy.initialize(self.sqliteDb)

    # For test only, do not use
    def get_database(self):
        return self.sqliteDb

    def get_all_tables(self):
        return Member.get_all_tables()

    def create_table(self, guild_id:int):
        Member.create_table(guild_id=guild_id)

    def get_member_row(self, guild_id:int, member_id:int):
        return Member.get_tabel(guild_id).get(member_id=member_id)
    
    def add_member(self, guild_id:int, member_id:int):
        table = Member.get_tabel(guild_id)
        member = table.create(
            member_id=member_id,
            xp=0,
            rank=0,
            item_id_list='[]',
            normal_coin=0,
            special_item_id_list='[]',
            extra_avator_image=None,
            pure=None)
        member.save()
        
