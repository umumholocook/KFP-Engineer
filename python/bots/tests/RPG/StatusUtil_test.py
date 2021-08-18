from common.models.RPGCharacter import RPGCharacter
from common.RPGUtil.RPGCharacterUtil import RPGCharacterUtil
from common.RPGUtil.StatusUtil import StatusTypeEnum, StatusUtil
from common.KFP_DB import KfpDb

class TestStatusUtil():
    def setup_method(self, method):
        self.database = KfpDb(":memory:")
    
    def teardown_mehtod(self, method):
        self.database.teardown()

    def test_createRestStatus_success(self):
        expected_status = StatusUtil.createRestStatus(1, 20, 30)
        status = StatusUtil.getStatus(1, StatusTypeEnum.REST)
        assert expected_status == status

    def test_applyExpiredStatus_success(self):
        c: RPGCharacter = RPGCharacterUtil.createNewRPGCharacter(1)
        RPGCharacterUtil.changeHp(c, -1000)
        StatusUtil.createRestStatus(1, 20, -500) # expired status
        StatusUtil.applyExpiredStatus()

        assert None == StatusUtil.getStatus(1, StatusTypeEnum.REST)

        c = RPGCharacterUtil.getRPGCharacter(1)
        assert c.hp_current > 0
