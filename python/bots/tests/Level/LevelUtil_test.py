from common.LevelUtil import LevelUtil

class TestLevelUtil():
    def setup_method(self, method):
        pass
    def teardown_method(self, method):
        pass

    def test_calculateXPRequiredForLevel_correct(self):
        xp = LevelUtil.calculateXPRequiredForLevel(desire_level=10)
        assert xp == 4675.0

    def test_generateNewHP_success(self):
        assert LevelUtil.generateNewHP(2) > 10
        assert LevelUtil.generateNewHP(10) > 18
    
    def test_generateLevelUpHP_fail(self):
        assert LevelUtil.generateLevelUpHP(1, 0, 10) == 10 
        assert LevelUtil.generateLevelUpHP(1, 1, 10) == 10 
    
    def test_generateLevelUpHP_success(self):
        assert LevelUtil.generateLevelUpHP(1, 2, 10) > 10
        assert LevelUtil.generateLevelUpHP(1, 10, 10) > 18
    
    def test_generateLevelUpMP_fail(self):
        assert LevelUtil.generateLevelUpMP(1, 0, 10) == 10
        assert LevelUtil.generateLevelUpMP(1, 1, 10) == 10
    
    def test_generateLevelUpMP_success(self):
        assert LevelUtil.generateLevelUpHP(1, 2, 10) > 10
        assert LevelUtil.generateLevelUpHP(1, 10, 10) > 18

    def test_generateLevelUpAttack_fail(self):
        assert LevelUtil.generateLevelUpAttack(1, 0, 10) == 10
        assert LevelUtil.generateLevelUpAttack(1, 1, 10) == 10
    
    def test_generateLevelUpAttack_success(self):
        assert LevelUtil.generateLevelUpAttack(1, 2, 10) > 10
        assert LevelUtil.generateLevelUpAttack(1, 10, 10) > 18

    def test_generateLevelUpDefense_fail(self):
        assert LevelUtil.generateLevelUpDefense(1, 0, 10) == 10
        assert LevelUtil.generateLevelUpDefense(1, 1, 10) == 10
    
    def test_generateLevelUpDefense_success(self):
        assert LevelUtil.generateLevelUpDefense(1, 2, 10) > 10
        assert LevelUtil.generateLevelUpDefense(1, 10, 10) > 18
