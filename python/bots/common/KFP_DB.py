import sqlite3
import common.models.BaseModel as db
from common.models.Member import Member
from peewee import SqliteDatabase

class KfpDb():

    def __init__(self, dbFile="./common/KFP_bot.db"):
        self.sqliteDb = SqliteDatabase(dbFile)
        db.proxy.initialize(self.sqliteDb)
        self.sqliteDb.create_tables([Member])

    # For test only, do not use
    def get_database(self):
        return self.sqliteDb

    def get_member_row(self, member_id:int):
        Member.get(member_id=member_id)
    
    def add_member(self, member_id:int):
        member = Member.create(member_id=member_id)
        member.save()
    
    def add_members(self, member_ids):
        data = []
        for member_id in member_ids:
            data.append({'member_id': member_id})
        Member.insert_many(data).execute()
        

        
