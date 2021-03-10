import pytest
from cogs.RockPaperScissors import RockPaperScissors

class TestRockPaperScissors():
    def setup_method(self, method):
        pass
    def teardown_method(self, method):
        pass

    def test_RockPaperScissorsWinning(self):
        rps = RockPaperScissors(None)
        assert 1 == rps.whoWin("石頭", "剪刀")
        assert 1 == rps.whoWin("布", "石頭")
        assert 1 == rps.whoWin("剪刀", "布")

    def test_RockPaperScissorsLose(self):
        rps = RockPaperScissors(None)
        assert -1 == rps.whoWin("石頭", "布")
        assert -1 == rps.whoWin("布", "剪刀")
        assert -1 == rps.whoWin("剪刀", "石頭")

    def test_RockPaperScissorsTie(self):
        rps = RockPaperScissors(None)
        assert 0 == rps.whoWin("石頭", "石頭")
        assert 0 == rps.whoWin("布", "布")
        assert 0 == rps.whoWin("剪刀", "剪刀")