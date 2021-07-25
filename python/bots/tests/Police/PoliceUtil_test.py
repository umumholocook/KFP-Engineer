from common.PoliceUtil import PoliceUtil
from common.KFP_DB import KfpDb

class TestPoliceUtil():
    def setup_method(self, method):
        self.database = KfpDb(":memory:")
    
    def teardown_method(self, method):
        self.database.teardown()
    
    def test_getCurrentPolice_empty(self):
        currentPoliceType = PoliceUtil.getCurrentPoliceType(guild_id=1, user_id=1)
        assert len(currentPoliceType) == 0

    def test_createNewPolice_success(self):
        assert PoliceUtil.createNewPolice(guild_id=1, user_id=1, type="SLEEP")
        currentPoliceType = PoliceUtil.getCurrentPoliceType(guild_id=1, user_id=1)
        assert currentPoliceType == "SLEEP"
    
    def test_createNewPolice_failed(self):
        assert PoliceUtil.createNewPolice(guild_id=1, user_id=1, type="SLEEP")
        assert not PoliceUtil.createNewPolice(guild_id=1, user_id=1, type="STUDY")
    
    def test_stopPolice_fail(self):
        assert not PoliceUtil.stopPolice(guild_id=1, user_id=1)

    def test_stopPolice_success(self):
        assert PoliceUtil.createNewPolice(guild_id=1, user_id=1, type="SLEEP")
        assert PoliceUtil.stopPolice(guild_id=1, user_id=1)
        assert len(PoliceUtil.getCurrentPoliceType(
            guild_id=1,
            user_id=1
        )) == 0

    def test_timeout_success(self):
        assert PoliceUtil.createNewPoliceWithDuration(guild_id=1, user_id=1, duration_min=-61, type="SLEEP")
        assert len(PoliceUtil.getCurrentPoliceType(guild_id=1, user_id=1)) == 0