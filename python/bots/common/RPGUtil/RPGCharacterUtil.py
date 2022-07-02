from discord.abc import User
from peewee import DateTimeField
from common.models.Member import Member
from common.MemberUtil import MemberUtil
from common.models.RPGCharacter import RPGCharacter
from common.LevelUtil import LevelUtil
from datetime import datetime
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

    def hasAdventureStared(member_id: int):
        character: RPGCharacter = RPGCharacterUtil.getRPGCharacter(member_id)
        return character != None and not character.retired

    def retireRPGCharacter(member_id: int):
        character: RPGCharacter = RPGCharacterUtil.getRPGCharacter(member_id)
        character.retired = True
        character.save()

    def levelUpCharacter(user: User, old_level: int, new_level: int):
        RPGCharacterUtil.levelUpCharacter(user.id, old_level, new_level)

    def levelUpCharacter(member_id: int, old_level: int, new_level: int):
        if not RPGCharacterUtil.hasAdventureStared(member_id):
            return  # ignore if user hasn't start Adventure
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
        if RPGCharacterUtil.hasAdventureStared(member_id):
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
            character=member,
            hp_current=new_hp,
            hp_max=new_hp,
            mp_current=new_mp,
            mp_max=new_mp,
            attack_basic=new_attack,
            defense_basic=new_defense,
            retired=False,
            last_attack=datetime.now().replace(year=2000)
        )

    def changeHp(character: RPGCharacter, hp: int):
        new_hp = character.hp_current + hp
        new_hp = min(character.hp_max, new_hp)
        new_hp = max(0, new_hp)
        character.hp_current = new_hp
        character.save()
        return new_hp < 1

    def getDefensePoint(character: RPGCharacter):
        return character.defense_basic

    def getAttackPoint(attacker: RPGCharacter, victim: RPGCharacter):
        return RPGCharacterUtil.__getDamange(attacker, victim)

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

    # 計算攻擊力[attackPoint] 對於玩家[victim]造成多少傷害
    def __getDamange(attacker: RPGCharacter, victim: RPGCharacter):
        # 防禦方的身體防禦吸收
        absorbBare = RPGCharacterUtil.__getAbsorb(victim)
        # 防禦方的防具防禦力
        armorPoint = RPGCharacterUtil.__getArmorPoint(victim)
        # 攻擊方的武器穿透力
        penetration = RPGCharacterUtil.__getWeaponPenetration(attacker)
        # 防禦方的防具防禦吸收
        armorAbsorb = RPGCharacterUtil.__getArmorAbsorb(armorPoint, penetration)
        # 攻擊方的武器攻擊力
        attackPoint = RPGCharacterUtil.__getWeaponAttack(attacker)
        # 總傷害
        damange = round(attackPoint * (1 - (absorbBare + armorAbsorb)))

        return damange
    
    def __getWeaponAttack(character: RPGCharacter):
        # TODO: 讀取武器攻擊力以及其他的加成
        return character.attack_basic

    def getArmorPointDebug(character: RPGCharacter):
        return RPGCharacterUtil.__getArmorPoint(character)

    def __getArmorPoint(character: RPGCharacter):
        # TODO: 讀取防具防禦力以及其他的加成
        return 0
    
    def __getWeaponPenetration(attacker: RPGCharacter):
        # TODO: 讀取武器穿透力以及其他的加成
        return 0

    def getAbsoreDebug(character: RPGCharacter):
        return RPGCharacterUtil.__getAbsorb(character)

    # 防禦吸收, 玩家的等級的1/100, 最多是10%. 此數值只是人物本身數值
    def __getAbsorb(character: RPGCharacter):
        return min(character.character.rank * .01, .1)

    def getArmorAbsoreDebug(armorPoint: int, penetration: int):
        return RPGCharacterUtil.__getArmorAbsorb(armorPoint, penetration)
    
    # 防具的防禦吸收, 最多是80%.
    def __getArmorAbsorb(armorPoint: int, penetration: int):
        magicNumber = 602
        attack = max(armorPoint - penetration, 0)
        return min(attack / (attack + magicNumber), .80)
    
    def attackSuccess(character: RPGCharacter):
        character.last_attack = datetime.now()
        character.save()
        
