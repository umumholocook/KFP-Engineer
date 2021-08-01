from peewee import CharField
from common.RPGUtil.ItemType import *


class ItemTypeField(CharField):

    def db_value(self, type: ItemType):
        return type

    def python_value(self, value: str):
        return ItemType(value)
