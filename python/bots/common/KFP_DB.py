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

    def create_table(self, guild_id:int):
        Member.create_table(guild_id=guild_id)

    def get_member_row(self, guild_id:int, member_id:int):
        return Member.get_member_row(guild_id, member_id)
    
    def add_member(self, guild_id:int, member_id:int):
        Member.add_member(guild_id, member_id)
    
    def add_members(self, guild_id:int, members_set:set):
        Member.add_members(guild_id, members_set)
        

        
