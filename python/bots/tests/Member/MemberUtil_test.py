from common.MemberUtil import MemberUtil
from common.KFP_DB import KfpDb

class TestMemberUtil():
    def setup_method(self, method):
        self.database = KfpDb(":memory:")
        
    def teardown_method(self, method):
        self.database.teardown()

    def test_getCountZero(self):
        assert MemberUtil.get_member_count() == 0

    def test_getCountSuccess(self):
        self.database.add_member(1)
        assert MemberUtil.get_member_count() == 1
        self.database.add_member(2)
        assert MemberUtil.get_member_count() == 2
        
    def test_getTotalTokenZero(self):
        assert MemberUtil.get_total_token() == 0

    def test_getTotalTokenSuccess(self):
        self.database.add_member(123)

        assert MemberUtil.get_total_token() == 100

        self.database.add_member(321)
        
        assert MemberUtil.get_total_token() == 200

    def test_getTotalCoinZero(self):
        assert MemberUtil.get_total_coin() == 0
    
    def test_getTotalCoinSuccess(self):
        self.database.add_member(123)
        self.database.add_coin(123, 100)

        assert MemberUtil.get_total_coin() == 100

        self.database.add_member(321)
        self.database.add_coin(321, 100)

        assert MemberUtil.get_total_coin() == 200
