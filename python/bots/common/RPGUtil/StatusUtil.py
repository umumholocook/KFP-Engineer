from peewee import fn

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
            member_id=member_id,
            guild_id=guild_id,
            type=StatusType.REST.value,
            buff=buff,
            expire_time=datetime.datetime.now() + datetime.timedelta(seconds=expire_seconds)
        )

    # indicate a member has been alerted, either create a new one or modify an existing one.
    def createOrUpdateAlertStatus(member_id: int, guild_id: int, expire_seconds: int):
        buff = Buff(BuffType.NONE, 0, -1)
        query = RPGStatus.select().where(
            RPGStatus.member_id == member_id,
            RPGStatus.guild_id == guild_id,
            RPGStatus.type == StatusType.ALERTED.value
        )
        new_time = datetime.datetime.now() + datetime.timedelta(seconds=expire_seconds)
        if query.exists():
            status: RPGStatus = query.get()
            status.expire_time = new_time
            status.save()
        else:
            RPGStatus.create(
                member_id=member_id,
                guild_id=guild_id,
                type=StatusType.ALERTED.value,
                buff=buff,
                expire_time=new_time
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

    def getAllStatus(type: StatusType):
        query = RPGStatus.select().where(
            RPGStatus.type == type.value
        )
        result = []
        if query.exists():
            for status in query.iterator():
                result.append(status)
        return result

    # loop through all the expired status and apply them if needed
    # only for rest
    def applyExpiredStatus():
        now = datetime.datetime.now()
        query = RPGStatus.select().where(
            RPGStatus.expire_time < now,
            RPGStatus.type == StatusType.REST.value
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

    def removeAlertStatus(member_id: int):
        query = RPGStatus.select().where(
            RPGStatus.member_id == member_id,
            RPGStatus.type == StatusType.ALERTED.value
        )
        if query.exists():
            status: RPGStatus
            for status in query.iterator():
                status.delete_instance()

    def _cleanUpStatus(status: RPGStatus):
        if not RPGCharacterUtil.hasAdventureStared(status.member_id):
            return
        character = RPGCharacterUtil.getRPGCharacter(status.member_id)
        if status.type == StatusType.REST.value:
            RPGCharacterUtil.changeHp(character, status.buff.buff_value)
        if status.type == StatusType.COMA.value:
            RPGCharacterUtil.changeHp(character, status.buff.buff_value)

    def isResting(user: User, guild_id: int):
        status = StatusUtil.getStatus(user.id, guild_id, StatusType.REST)
        return not status == None

    def isAlerted(user: User, guild_id: int):
        status: RPGStatus = StatusUtil.getStatus(user.id, guild_id, StatusType.ALERTED)
        return (not status == None) and (status.expire_time > datetime.datetime.now())

    def startResting(user: User, guild_id: int):
        rpg: RPGCharacter = RPGCharacterUtil.getRPGCharacter(user.id)
        if StatusUtil.getStatus(user.id, guild_id, StatusType.COMA) is not None:
            StatusUtil._removeComaStatus(user.id)
        StatusUtil.createRestStatus(user.id, guild_id, rpg.hp_max, 300)  # 5分鐘
        pass

    def _removeComaStatus(member_id: int):
        query = RPGStatus.select().where(
            RPGStatus.member_id == member_id,
            RPGStatus.type == StatusType.COMA.value
        )
        if query.exists():
            status: RPGStatus
            for status in query.iterator():
                status.delete_instance()

    def createComaStatus(guild_id: int, user: User, hp_max: int):
        buff = Buff(BuffType.NONE, hp_max, -1)
        return RPGStatus.create(
            member_id=user.id,
            guild_id=guild_id,
            type=StatusType.COMA.value,
            buff=buff,
            expire_time=datetime.datetime.now() + datetime.timedelta(seconds=10)
        )

    def isComa(user: User, guild_id: int):
        status = StatusUtil.getStatus(user.id, guild_id, StatusType.COMA)
        return not status == None

    def reviveComaStatus(reviveMemberCount: int=5):
        query = RPGStatus.select().where(
            RPGStatus.type == StatusType.COMA.value,
        )
        result = []
        if query.exists():
            count = RPGStatus.select().where(
                RPGStatus.type == StatusType.COMA.value,
            ).count()
            if count >= reviveMemberCount:
                status: RPGStatus
                for status in query.iterator():
                    result.append(StatusUpdate(status.member_id, status.guild_id, status.type))
                    StatusUtil._cleanUpStatus(status)
                    status.delete_instance()
        return result


