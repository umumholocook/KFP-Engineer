from enum import Enum

class ItemType(str, Enum):
    NONE = "一般道具"
    ATTACK = "攻擊道具"
    DEFENCE = "防禦道具"
    RECOVER = "回復道具"
    STATUS = "狀態道具"
