from common.RPGUtil.Buff import Buff, BuffType


class TestBuffObject():
    def setup_method(self, method):
        pass
    def teardown_method(self, method):
        pass

    def test_toString_correct(self):
        buff = Buff(BuffType.ATTACK, 30, 2)

        assert buff.toString() == '{"buff_type": "attack", "buff_value": 30, "buff_round": 2}'

    def test_fromString_correct(self):
        buff_string = '{"buff_type": "defence", "buff_value": 20, "buff_round": 5}'

        buff: Buff = Buff.fromString(buff_string)

        assert buff.buff_type == BuffType.DEFENCE
        assert buff.buff_round == 5
        assert buff.buff_value == 20

    def test_buffType_fromInt_correct(self):
        assert BuffType.list()[0] == BuffType.NONE.name
    
    def test_buffType_length_correct(self):
        assert len(BuffType) == len(BuffType.list())