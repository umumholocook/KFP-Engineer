from common.RPGUtil.RPGCharacterUtil import RPGCharacterUtil
from common.models.RPGStatus import RPGStatus
from common.RPGUtil.Buff import Buff, BuffType
import datetime, enum

class StatusTypeEnum(enum.IntEnum):
    REST = 1

class StatusUtil():
    # create rest status for member
    def createRestStatus(member_id: int, max_hp: int, expire_seconds: int):
        buff = Buff(BuffType.NONE, max_hp, -1)
        return RPGStatus.create(
            member_id = member_id,
            type = StatusTypeEnum.REST.value,
            buff = buff,
            expire_time = datetime.datetime.now() + datetime.timedelta(seconds=expire_seconds)
        )

    def getStatus(member_id: int, type: StatusTypeEnum):
        query = RPGStatus.select().where(
            RPGStatus.member_id == member_id,
            RPGStatus.type == type.value,
        )
        if query.exists():
            return query.get()
        return None

    # loop through all the expired status and apply them if needed
    def applyExpiredStatus():
        now = datetime.datetime.now()
        query = RPGStatus.select().where(
            RPGStatus.expire_time < now
        )
        if query.exists():
            status: RPGStatus
            for status in query.iterator():
                StatusUtil._cleanUpStatus(status)
                status.delete_instance()
    
    # remove all status associated with a member
    def removeAllStatus(member_id: int):
        query = RPGStatus.select().where(
            RPGStatus.member_id == member_id
        )
        if query.exists():
            status: RPGStatus
            for status in query.iterator():
                status.delete_instance()
    
    def _cleanUpStatus(status: RPGStatus):
        character = RPGCharacterUtil.getRPGCharacter(status.member_id)
        if status.type == StatusTypeEnum.REST.value:
            RPGCharacterUtil.changeHp(character, status.buff.buff_value)
