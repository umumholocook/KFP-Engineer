from enum import Enum


class BuffType(Enum):
    attack = 1
    defence = 2
    magic = 3
    hit_point = 4


class Buff:
    def __init__(self, buff_type, buff_value, buff_round):
        self.buff_type = buff_type
        self.buff_value = buff_value
        self.buff_round = buff_round
