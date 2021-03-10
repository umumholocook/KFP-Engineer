import pytest
from common.Util import Util

class TestUtil():
    def setup_method(self, method):
        pass
    def teardown_method(self, method):
        pass

    def test_experienceCalculation(self):
        assert "386080.00" == "{:0.2f}".format(Util.get_rank_exp(57))
        assert "166355.00" == "{:0.2f}".format(Util.get_rank_exp(42))
        assert "226305.00" == "{:0.2f}".format(Util.get_rank_exp(47))