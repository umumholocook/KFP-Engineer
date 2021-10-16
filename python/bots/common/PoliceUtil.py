from datetime import datetime, timedelta
from common.models.Police import Police

class PoliceUtil():
    default_time = 60

    __policeName =  {
            "SLEEP": "睡覺",
            "EAT": "吃飯",
            "SHOWER": "洗澡",
            "STUDY": "讀書",
            "HOMEWORK": "寫作業",
            "BIRTHDAY": "生日",
        }

    def getPoliceTypeChineseName(type: str):
        return PoliceUtil.__policeName[type]
    
    def isProperType(type: str):
        if type in PoliceUtil.__policeName:
            return True
        return False

    def getCurrentPoliceType(guild_id: int, user_id: int):
        expire = datetime.now() - timedelta(minutes=PoliceUtil.default_time)
        query = Police.select().where(
            Police.guild_id == guild_id,
            Police.member_id == user_id,
            Police.expire_time > expire,
            Police.stopped == False
        )
        if query.exists():
            police: Police = query.get()
            return police.police_type
        else:
            return ""
    
    def createNewPoliceWithDuration(guild_id: int, user_id: int, duration_min: int, type: str):
        currentPoliceType = PoliceUtil.getCurrentPoliceType(guild_id=guild_id, user_id=user_id)
        if len(currentPoliceType) > 0:
            return False
        Police.insert(
            guild_id=guild_id,
            member_id=user_id,
            police_type=type,
            expire_time=datetime.now() + timedelta(minutes=duration_min)
            ).execute()
        return True

    def createNewPolice(guild_id: int, user_id: int, type: str):
        expireTime = PoliceUtil.default_time
        if "BIRTHDAY" == type:
            expireTime = 1440
        return PoliceUtil.createNewPoliceWithDuration(guild_id=guild_id, user_id=user_id, duration_min=expireTime, type=type)
    
    def stopPolice(guild_id: int, user_id: int):
        expire = datetime.now() - timedelta(minutes=PoliceUtil.default_time)
        query = Police.select().where(
            Police.guild_id == guild_id,
            Police.member_id == user_id,
            Police.expire_time > expire,
            Police.stopped == False
        )
        if query.exists():
            police: Police = query.get()
            police.stopped = True
            police.save()
            return True
        return False
        
    