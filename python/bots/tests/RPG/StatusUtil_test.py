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
        comaStatus = StatusUtil.createComaStatus(guild_id=1, user=c, hp_max=c.hp_max)
        status = StatusUtil.getStatus(guild_id=1, member_id=c.id, type=StatusType.COMA)
        assert comaStatus == status
        statuslist = StatusUtil.reviveComaStatus()
        assert len(statuslist) == 0
        ch: RPGCharacter = RPGCharacterUtil.createNewRPGCharacter(2)
        comaStatus1 = StatusUtil.createComaStatus(guild_id=1, user=ch, hp_max=ch.hp_max)
        status1 = StatusUtil.getStatus(guild_id=1, member_id=ch.id, type=StatusType.COMA)
        assert comaStatus1 == status1
        statuslist = StatusUtil.reviveComaStatus()
        assert len(statuslist) == 0
        assert c.hp_max == c.hp_current



    def test_removeComaStatusToRest(self):
        c: RPGCharacter = RPGCharacterUtil.createNewRPGCharacter(1)
        StatusUtil.createComaStatus(guild_id=1, user=c, hp_max=c.hp_max)
        StatusUtil.startResting(guild_id=1, user=c)
        status = StatusUtil.getStatus(guild_id=1, member_id=c.id, type=StatusType.COMA)
        assert status is None
        status = StatusUtil.getStatus(guild_id=1, member_id=c.id, type=StatusType.REST)
        assert status is not None
