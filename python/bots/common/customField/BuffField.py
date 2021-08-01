from peewee import CharField
from common.RPGUtil.Buff import *


class BuffField(CharField):

    def db_value(self, buff: Buff):
        return buff.toString()

    def python_value(self, value: str):
        return Buff.fromString(value)
