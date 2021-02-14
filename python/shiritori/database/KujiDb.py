import pytz
import database.BaseModel as db
from peewee import SqliteDatabase
from database.Kuji_Cn import RecordCn
from database.Kuji_Jp import RecordJp
from datetime import datetime, timedelta, tzinfo
from tzlocal import get_localzone

TABLES = [RecordCn, RecordJp]

class KujiDb():
    def __init__(self, dbFile="KFP_Kuji.db", timeZone="Asia/Taipei"):
        self.sqliteDb = SqliteDatabase(dbFile)
        db.proxy.initialize(self.sqliteDb)
        self.sqliteDb.create_tables(TABLES)
        self.timeZone = timeZone

    def canDrawJp(self, member_id:int):
        return self.__canDraw(self.__getMemberJp(member_id))

    def canDrawCn(self, member_id:int):
        return self.__canDraw(self.__getMemberCn(member_id))
    
    def clearDb(self):
        RecordJp.delete().where(RecordJp.timestamp < datetime.now()).execute()
        RecordCn.delete().where(RecordCn.timestamp < datetime.now()).execute()

    def __canDraw(self, member):
        if not member:
            return True

        # both record and current is utc
        targetTimeZone = pytz.timezone(self.timeZone)

        today = datetime.now()
        todayWithTimeZone = today.astimezone(targetTimeZone)
        beginningTodayWithTimeZone = todayWithTimeZone - timedelta(hours=todayWithTimeZone.hour, minutes=todayWithTimeZone.minute, seconds=todayWithTimeZone.second, microseconds=todayWithTimeZone.microsecond)
        lastTime = member.timestamp
        lastTimeWithtimeZone = lastTime.astimezone(targetTimeZone)

        return lastTimeWithtimeZone < beginningTodayWithTimeZone

    def __hasMemberJp(self, member_id:int):
        return RecordJp.select().where(RecordJp.member_id == member_id).exists()
    
    def __hasMemberCn(self, member_id:int):
        return RecordCn.select().where(RecordCn.member_id == member_id).exists()
    
    def __getMemberJp(self, member_id:int):
        if self.__hasMemberJp(member_id):
            return RecordJp.get_by_id(member_id)
        return

    def __getMemberCn(self, member_id:int):
        if self.__hasMemberCn(member_id):
            return RecordCn.get_by_id(member_id)
        return

    def updateMemberJp(self, member_id:int):
        if self.__hasMemberJp(member_id):
            member = RecordJp.get_by_id(member_id)
        else:
            member = RecordJp.create(member_id=member_id)
        
        member.timestamp = datetime.now()
        member.save()
    
    def updateMemberCn(self, member_id:int):
        if self.__hasMemberCn(member_id):
            member = RecordCn.get_by_id(member_id)
        else:
            member = RecordCn.create(member_id=member_id)
        
        member.timestamp = datetime.now()
        member.save()
            