from common.RockPaperScissorsUtil import RockPaperScissorsUtil

class TestRockPaperScissorsUtil():
    def setup_method(self, method):
        pass
    def teardown_method(self, method):
        pass

    def test_optionAndWeightSameLength(self):
        assert len(RockPaperScissorsUtil.TOO_FAST) == len(RockPaperScissorsUtil.TOO_FAST_WEIGHT)
    
    def test_lastItemWeightCorrect(self):
        assert RockPaperScissorsUtil.TOO_FAST_WEIGHT[-1] == RockPaperScissorsUtil.DEFAULT_MAIN_RESPONSE_WEIGHT

    def test_optionAndWeightSameLength(self):
        assert len(RockPaperScissorsUtil.TIE_DIALOG) == len(RockPaperScissorsUtil.TIE_WEIGHT)
    
    def test_lastItemWeightCorrect(self):
        assert RockPaperScissorsUtil.TIE_WEIGHT[-1] == RockPaperScissorsUtil.DEFAULT_MAIN_RESPONSE_WEIGHT

    def test_optionAndWeightSameLength(self):
        assert len(RockPaperScissorsUtil.WIN_DIALOG) == len(RockPaperScissorsUtil.WIN_WEIGHT)
    
    def test_lastItemWeightCorrect(self):
        assert RockPaperScissorsUtil.WIN_WEIGHT[-1] == RockPaperScissorsUtil.DEFAULT_MAIN_RESPONSE_WEIGHT

    def test_optionAndWeightSameLength(self):
        assert len(RockPaperScissorsUtil.LOSE_DIALOG) == len(RockPaperScissorsUtil.LOSE_WEIGHT)
    
    def test_lastItemWeightCorrect(self):
        assert RockPaperScissorsUtil.LOSE_WEIGHT[-1] == RockPaperScissorsUtil.DEFAULT_MAIN_RESPONSE_WEIGHT
