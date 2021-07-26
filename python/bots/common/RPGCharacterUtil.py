from common.models.Member import Member
from common.models.RPGCharacter import RPGCharacter
from common.LevelUtil import LevelUtil

class RPGCharacterUtil():
    def createNewRPGCharacter(member: Member):
        query = RPGCharacter.select().where(
            RPGCharacter.character == member
        )
        if query.exists():
            return -1 # character already exists
        new_hp = LevelUtil.generateNewHP(member.rank)
        new_mp = LevelUtil.generateNewMP(member.rank)
        new_attack = LevelUtil.generateAttack(member.rank)
        new_defense = LevelUtil.generateDefense(member.rank)
        return RPGCharacter.insert(
            character = member,
            hp_current = new_hp,
            hp_max = new_hp,
            mp_current = new_mp,
            mp_max = new_mp,
            attack_basic = new_attack,
            defense_basic = new_defense,
        )
        

    