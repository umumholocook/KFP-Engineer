from common.RPGUtil.RPGCharacterUtil import RPGCharacterUtil
from common.RPGUtil.StatusType import StatusType
from common.models.RPGCharacter import RPGCharacter
from common.RPGUtil.StatusUtil import StatusUtil
from common.KFP_DB import KfpDb


class TestStatusUtil():
    def setup_method(self, method):
        self.database = KfpDb(":memory:")

    def teardown_mehtod(self, method):
        self.database.teardown()

    def test_createRestStatus_success(self):
        expected_status = StatusUtil.createRestStatus(1, 1, 20, 30)
        status = StatusUtil.getStatus(1, 1, StatusType.REST)
        assert expected_status == status

    def test_applyExpiredStatus_success(self):
        c: RPGCharacter = RPGCharacterUtil.createNewRPGCharacter(1)
        RPGCharacterUtil.changeHp(c, -1000)
        StatusUtil.createRestStatus(1, 1, 20, -500)  # expired status
        StatusUtil.applyExpiredStatus()

        assert None == StatusUtil.getStatus(1, 1, StatusType.REST)

        c = RPGCharacterUtil.getRPGCharacter(1)
        assert c.hp_current > 0

    def test_createComaStatus_success(self):
        c: RPGCharacter = RPGCharacterUtil.createNewRPGCharacter(1)
        comaStatus = StatusUtil.createComaStatus(guild_id=1, user=c)
        status = StatusUtil.getStatus(guild_id=1, member_id=c.id, type=StatusType.COMA)
        assert comaStatus == status

    def test_removeComaStatusToRest(self):
        c: RPGCharacter = RPGCharacterUtil.createNewRPGCharacter(1)
        StatusUtil.createComaStatus(guild_id=1, user=c)
        StatusUtil.startResting(guild_id=1, user=c)
        status = StatusUtil.getStatus(guild_id=1, member_id=c.id, type=StatusType.COMA)
        assert status is None
        status = StatusUtil.getStatus(guild_id=1, member_id=c.id, type=StatusType.REST)
        assert status is not None
