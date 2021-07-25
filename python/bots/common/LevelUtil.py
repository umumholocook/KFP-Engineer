
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
    
    
