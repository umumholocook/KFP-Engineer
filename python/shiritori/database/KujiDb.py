from database.Kuji_Ls import RecordLs
import pytz
import database.BaseModel as db
from peewee import SqliteDatabase
from database.Kuji_Cn import RecordCn
from database.Kuji_Jp import RecordJp
from database.Kuji_Ls import RecordLs
from datetime import datetime, timedelta

TABLES = [RecordCn, RecordJp, RecordLs]

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

    def canDrawLs(self, member_id:int):
        return self.__canDraw(self.__getMemberLs(member_id))
    
    def clearDb(self):
        RecordJp.delete().where(RecordJp.timestamp < datetime.now()).execute()
        RecordCn.delete().where(RecordCn.timestamp < datetime.now()).execute()
        RecordLs.delete().where(RecordLs.timestamp < datetime.now()).execute()

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

    def __hasMemberLs(self, member_id:int):
        return RecordLs.select().where(RecordLs.member_id == member_id).exists()
    
    def __getMemberJp(self, member_id:int):
        if self.__hasMemberJp(member_id):
            return RecordJp.get_by_id(member_id)
        return

    def __getMemberCn(self, member_id:int):
        if self.__hasMemberCn(member_id):
            return RecordCn.get_by_id(member_id)
        return

    def __getMemberLs(self, member_id:int):
        if self.__hasMemberLs(member_id):
            return RecordLs.get_by_id(member_id)
        return

    def getHistoryLs(self, member_id:int):
        if self.__hasMemberLs(member_id):
            member = self.__getMemberLs(member_id)
            return (member.index, member.timestamp)
        return (-1, None)

    def getHistoryJp(self, member_id:int):
        if self.__hasMemberJp(member_id):
            member = self.__getMemberJp(member_id)
            return (member.index, member.timestamp)
        return (-1, None)

    def getHistoryCn(self, member_id:int):
        if self.__hasMemberCn(member_id):
            member = self.__getMemberCn(member_id) 
            return (member.sky, member.bottom, member.timestamp)
        return (-1, -1, None)

    def updateMemberLs(self, member_id:int, index:int):
        if self.__hasMemberLs(member_id):
            member = RecordLs.get_by_id(member_id)
        else:
            member = RecordLs.create(member_id=member_id, index=index, timestamp=datetime.now())
        member.timestamp = datetime.now()
        member.index = index
        member.save()

    def updateMemberJp(self, member_id:int, index:int):
        if self.__hasMemberJp(member_id):
            member = RecordJp.get_by_id(member_id)
        else:
            member = RecordJp.create(member_id=member_id, index=index, timestamp=datetime.now())
        
        member.timestamp = datetime.now()
        member.index = index
        member.save()
    
    def updateMemberCn(self, member_id:int, sky:int, bottom:int):
        if self.__hasMemberCn(member_id):
            member = RecordCn.get_by_id(member_id)
        else:
            member = RecordCn.create(member_id=member_id, sky=sky, bottom=bottom, timestamp=datetime.now())
        
        member.timestamp = datetime.now()
        member.sky = sky
        member.bottom = bottom
        member.save()
            