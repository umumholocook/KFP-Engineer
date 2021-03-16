from common.ForwardUtil import ForwardUtil
from common.models.Forward import Forward
from common.KFP_DB import KfpDb

class TestForwardUtil():
    def setup_method(self, method):
        self.database = KfpDb()

    def teardown_method(self, method):
        self.database.teardown()

    def test_getAllForward_empty(self):
        forwards = ForwardUtil.get_all_forward()
        assert len(forwards) == 0

    def test_getAllForward_empty(self):
        ForwardUtil.create_forward(1, 1, 1, 2)
        ForwardUtil.create_forward(1, 1, 1, 5)
        forwards = ForwardUtil.get_all_forward()

        assert len(forwards) == 2

    def test_getForward_empty(self):
        forwards = ForwardUtil.get_forward(1, 1)
        
        assert len(forwards) == 0
    
    def test_createForward_success(self):
        ForwardUtil.create_forward(1, 1, 1, 2, True)
        forward: Forward = ForwardUtil.get_forward(1, 1)[0]

        assert forward.receive_channel_id == 2
        assert forward.receive_guild_id == 1
        assert forward.delete_original == True

    def test_createForward_noOverride(self):
        ForwardUtil.create_forward(1, 1, 1, 2)
        ForwardUtil.create_forward(1, 1, 1, 3)
        forwards = ForwardUtil.get_forward(1, 1)
        assert forwards[0].receive_channel_id == 2
        assert forwards[1].receive_channel_id == 3

    def test_deleteForward_noRecord(self):
        ForwardUtil.delete(123)

        forwards = ForwardUtil.get_all_forward()
        assert len(forwards) == 0

    def test_deleteForward_success(self):
        ForwardUtil.create_forward(1, 1, 1, 2)
        ForwardUtil.delete(1)

        forwards = ForwardUtil.get_all_forward()
        assert len(forwards) == 0


