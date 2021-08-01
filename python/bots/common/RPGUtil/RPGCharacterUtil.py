from common.models.Member import Member
from common.models.RPGCharacter import RPGCharacter
from common.LevelUtil import LevelUtil

class RPGCharacterUtil():

    def hasAdvantureStared(member_id: int) -> bool:
        mQuery = Member.select().where(Member.member_id == member_id)
        if not mQuery.exists():
            return False
        member: Member = mQuery.get()
        if not member:
            return False
        query = RPGCharacter.select().where(
            RPGCharacter.character == member
        )
        if not query.exists():
            return False
        return True
    
    def retireRPGCharacter(member_id: int) -> bool:
        mQuery = Member.select().where(Member.member_id == member_id)
        if not mQuery.exists():
            return False
        member: Member = mQuery.get()
        RPGCharacter.delete().where(
            RPGCharacter.character == member
        ).execute()

    def createNewRPGCharacter(member_id: int) -> RPGCharacter:
        mQuery = Member.select().where(Member.member_id == member_id)
        if not mQuery.exists():
            return None
        member: Member = mQuery.get()
        query = RPGCharacter.select().where(
            RPGCharacter.character == member
        )
        if query.exists():
            return None # character already exists
        new_hp = LevelUtil.generateNewHP(member.rank)
        new_mp = LevelUtil.generateNewMP(member.rank)
        new_attack = LevelUtil.generateAttack(member.rank)
        new_defense = LevelUtil.generateDefense(member.rank)
        return RPGCharacter.create(
            character = member,
            hp_current = new_hp,
            hp_max = new_hp,
            mp_current = new_mp,
            mp_max = new_mp,
            attack_basic = new_attack,
            defense_basic = new_defense,
        )
        

    