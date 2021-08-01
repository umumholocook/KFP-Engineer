from enum import Enum
import json

class BuffType(str, Enum):
    NONE = "none"
    ATTACK = "attack"
    DEFENCE = "defence"
    MAGIC = "magic"
    HIT_POINT = "hit_point"

    @staticmethod
    def list():
        return list(map(lambda c: c.name, BuffType))


class Buff:
    buff_type: BuffType
    buff_value: int
    buff_round: int

    def __init__(self, buff_type: BuffType, buff_value: int, buff_round: int):
        self.buff_type = buff_type
        self.buff_value = buff_value
        self.buff_round = buff_round
    
    def fromString(buff: str):
        return json.loads(buff, object_hook=lambda d: Buff(**d))
    
    def toString(self):
        return json.dumps(self.__dict__)
