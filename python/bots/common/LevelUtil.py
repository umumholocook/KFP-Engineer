import random

# 用於計算等級的
class LevelUtil():
    # 計算升級至等級X所需要的經驗值
    # desire_level: 欲升成的等級
    def calculateXPRequiredForLevel(desire_level: int):
        return 5 / 6 * desire_level * (2 * desire_level * desire_level + 27 * desire_level + 91)

    # 計算打敗X等級敵人所獲的的經驗值
    # opponent_level: 敵人的等級
    def getBattleVictoryExperience(opponent_level: int):
        required_xp = LevelUtil.calculateXPRequiredForLevel(opponent_level)
        return required_xp // 10
    
    # 根據等級, 隨機生成新的HP
    def generateNewHP(level: int):
        return LevelUtil.generateLevelUpHP(1, level, 10)

    # 根據等級的提升, 計算新的HP    
    def generateLevelUpHP(old_level:int, new_level: int, current_hp: int):
        loop = new_level - old_level
        if loop < 1:
            return current_hp
        hp = current_hp
        for _ in range(loop):
            hp += random.randint(1, min(5, new_level // 10 + 1))
        return hp

    # 根據等級, 隨機生成新的MP
    def generateNewMP(level: int):
        return LevelUtil.generateLevelUpMP(1, level, 1)

    # 根據等級的提升, 計算新的MP
    def generateLevelUpMP(old_level: int, new_level: int, current_mp: int):
        loop = new_level - old_level
        if loop < 1:
            return current_mp
        new_mp = 0
        for _ in range(loop):
            new_mp += random.randint(1, min(9, new_level // 10 + 1))
        return new_mp // 3 + current_mp

    def generateAttack(level: int):
        return LevelUtil.generateLevelUpAttack(1, level, 1)
    
    def generateLevelUpAttack(old_level: int, new_level: int, current_attack: int):
        loop = new_level - old_level
        if loop < 1:
            return current_attack
        new_attack = 0
        for _ in range(loop):
            new_attack += random.randint(1, 3)
        return current_attack + new_attack
    
    def generateDefense(level: int):
        return LevelUtil.generateLevelUpDefense(1, level, 1)

    def generateLevelUpDefense(old_level: int, new_level: int, current_defence: int):
        return LevelUtil.generateLevelUpAttack(old_level, new_level, current_defence)