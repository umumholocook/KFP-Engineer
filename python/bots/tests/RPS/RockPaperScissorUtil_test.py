from common.RockPaperScissorsUtil import RockPaperScissorsUtil

class TestRockPaperScissorsUtil():
    def setup_method(self, method):
        pass
    def teardown_method(self, method):
        pass

    def test_optionAndWeightSameLength(self):
        assert len(RockPaperScissorsUtil.TOO_FAST) == len(RockPaperScissorsUtil.TOO_FAST_WEIGHT)
    
    def test_lastItemWeightCorrect(self):
        assert RockPaperScissorsUtil.TOO_FAST_WEIGHT[-1] == 40