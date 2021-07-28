from peewee import FixedCharField
from common.RPGUtil.Buff import *


class BuffField(FixedCharField):

    def __init__(self, *args, **kwargs):
        self.max_length = 10
        super(BuffField, self).__init__(max_length=self.max_length, *args, **kwargs)

    def db_value(self, buff: Buff):
        list = [str(buff.buff_type), str(buff.buff_value), str(buff.buff_round)]
        return ",".join(list)

    def python_value(self, value):
        results = value.split(",")
        results = [int(i) for i in results]
        buff: Buff = Buff(buff_type=results[0], buff_value=results[1], buff_round=results[2])
        return buff
