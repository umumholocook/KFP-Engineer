from common.KujiUtil import KujiUtil
from common.Util import Util
from common.KujiObj import KujiObj
from common.KFP_DB import KfpDb

class TestKujiUtil():
    def setup_method(self):
        self.database = KfpDb()
        
    def teardown_method(self):
        self.database.teardown()

    def test_canDraw_true(self):
        assert KujiUtil.canDrawJp(1)
        assert KujiUtil.canDrawCn(1)
        assert KujiUtil.canDrawLs(1)
    
    def test_canDrawJp_false(self):
        KujiUtil.updateMemberJp(1, 1)
        assert not KujiUtil.canDrawJp(1)
    
    def test_canDrawCn_false(self):
        KujiUtil.updateMemberCn(1, 0, 0)
        assert not KujiUtil.canDrawCn(1)
    
    def test_canDrawLs_false(self):
        KujiUtil.updateMemberLs(1, 1)
        assert not KujiUtil.canDrawLs(1)

    def test_canDraw_false(self):
        KujiUtil.updateMemberJp(1, 1)
        KujiUtil.updateMemberCn(1, 0, 0)
        KujiUtil.updateMemberLs(1, 1)
        assert not KujiUtil.canDrawLs(1)
    
    def test_getHistoryJp(self):
        KujiUtil.updateMemberJp(1, 1)
        history = KujiUtil.getHistoryJp(1)

        assert history[0] == 1

    def test_getHistoryLs(self):
        KujiUtil.updateMemberLs(1, 1)
        history = KujiUtil.getHistoryLs(1)

        assert history[0] == 1
    
    def test_getHistoryCn(self):
        KujiUtil.updateMemberCn(1, 1, 2)
        history = KujiUtil.getHistoryCn(1)

        assert history[0] == 1
        assert history[1] == 2

    def test_clearData(self):
        KujiUtil.updateMemberJp(1, 1)
        KujiUtil.clearData()
        assert KujiUtil.canDrawJp(1)

        KujiUtil.updateMemberCn(1, 1, 2)
        assert not KujiUtil.canDrawCn(1)
