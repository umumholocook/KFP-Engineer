from common.LevelUtil import LevelUtil

class TestLevelUtil():
    def setup_method(self, method):
        pass
    def teardown_method(self, method):
        pass

    def test_calculateXPRequiredForLevel_correct(self):
        xp = LevelUtil.calculateXPRequiredForLevel(desire_level=10)
        assert xp == 4675.0
