from common.models.RPGCharacter import RPGCharacter
from discord.abc import User
from common.RPGUtil.StatusType import StatusType
from common.RPGUtil.StatusUpdate import StatusUpdate
from common.RPGUtil.RPGCharacterUtil import RPGCharacterUtil
from common.models.RPGStatus import RPGStatus
from common.RPGUtil.Buff import Buff, BuffType
import datetime

class StatusUtil():
    # create rest status for member
    def createRestStatus(member_id: int, guild_id: int, max_hp: int, expire_seconds: int):
        buff = Buff(BuffType.NONE, max_hp, -1)
        return RPGStatus.create(
            member_id = member_id,
            guild_id = guild_id,
            type = StatusType.REST.value,
            buff = buff,
            expire_time = datetime.datetime.now() + datetime.timedelta(seconds=expire_seconds)
        )

    def getStatus(member_id: int, guild_id: int, type: StatusType):
        query = RPGStatus.select().where(
            RPGStatus.member_id == member_id,
            RPGStatus.guild_id == guild_id,
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
        result = []
        if query.exists():
            status: RPGStatus
            for status in query.iterator():
                result.append(StatusUpdate(status.member_id, status.guild_id, status.type))
                StatusUtil._cleanUpStatus(status)
                status.delete_instance()
        return result

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
        if status.type == StatusType.REST.value:
            RPGCharacterUtil.changeHp(character, status.buff.buff_value)

    def isResting(user: User, guild_id: int):
        status = StatusUtil.getStatus(user.id, guild_id, StatusType.REST)
        return not status == None

    def startResting(user: User, guild_id: int):
        rpg: RPGCharacter = RPGCharacterUtil.getRPGCharacter(user.id)
        StatusUtil.createRestStatus(user.id, guild_id, rpg.hp_max, 300) # 5分鐘
        pass