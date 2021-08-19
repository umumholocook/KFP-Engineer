from discord.abc import User
from common.models.Member import Member
from common.MemberUtil import MemberUtil
from common.models.RPGCharacter import RPGCharacter
from common.LevelUtil import LevelUtil
import random


class RPGCharacterUtil():
    def getRPGCharacter(user: User):
        return RPGCharacterUtil.getRPGCharacter(user.id)

    def getRPGCharacter(member_id: int):
        member: Member = MemberUtil.get_or_add_member(member_id)
        query = RPGCharacter.select().where(
            RPGCharacter.character == member
        )
        if query.exists():
            return query.get()
        return None

    def hasAdvantureStared(member_id: int):
        character: RPGCharacter = RPGCharacterUtil.getRPGCharacter(member_id) 
        return character != None and not character.retired
    
    def retireRPGCharacter(member_id: int):
        character: RPGCharacter = RPGCharacterUtil.getRPGCharacter(member_id)
        character.retired = True
        character.save()
        
    def levelUpCharacter(user: User, old_level: int, new_level: int):
        RPGCharacterUtil.levelUpCharacter(user.id, old_level, new_level)

    def levelUpCharacter(member_id: int, old_level: int, new_level: int):
        if not RPGCharacterUtil.hasAdvantureStared(member_id):
            return # ignore if user hasn't start advanture 
        rpg: RPGCharacter = RPGCharacterUtil.getRPGCharacter(member_id)
        print(f"old hp: {rpg.hp_max}")
        rpg.hp_max = LevelUtil.generateLevelUpHP(old_level, new_level, rpg.hp_max)
        print(f"new hp: {rpg.hp_max}")
        rpg.hp_current = rpg.hp_max 
        rpg.mp_max = LevelUtil.generateLevelUpMP(old_level, new_level, rpg.mp_max)
        rpg.mp_current = rpg.mp_max
        rpg.attack_basic = LevelUtil.generateLevelUpAttack(old_level, new_level, rpg.attack_basic)
        rpg.defense_basic = LevelUtil.generateLevelUpDefense(old_level, new_level, rpg.defense_basic)
        rpg.save()

    def createNewRPGCharacter(member_id: int) -> RPGCharacter:
        if RPGCharacterUtil.hasAdvantureStared(member_id):
            return None
        character: RPGCharacter = RPGCharacterUtil.getRPGCharacter(member_id)
        if character:
            character.retired = False
            character.save()
            return character
        member: Member = MemberUtil.get_member(member_id)
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
            retired = False
        )
    
    def changeHp(character: RPGCharacter, hp: int):
        new_hp = character.hp_current + hp
        new_hp = min(character.hp_max, new_hp)
        new_hp = max(0, new_hp)
        character.hp_current = new_hp
        character.save()

    def getDefensePoint(character: RPGCharacter):
        return character.defense_basic
    
    def getAttackPoint(character: RPGCharacter):
        return character.attack_basic
        
    def _rollAttack(character: RPGCharacter):
        # roll a d20
        total = 0
        diceCount = character.character.rank // 10 + 1
        for _ in range(diceCount):
            total += random.randint(1, 20)

        return total + character.attack_basic
    
    def tryToAttack(attacker: RPGCharacter, victim: RPGCharacter):
        atkPoint = RPGCharacterUtil._rollAttack(attacker)
        defensePoint = RPGCharacterUtil.getDefensePoint(victim)
        # print(f"{atkPoint} vs {defensePoint}")
        return atkPoint > defensePoint
    