from enum import IntEnum
# 工具類 methods
class Util:
    # 預設database 位置
    DEFAULT_DB_PATH = r"./common/KFP_bot.db"

    class ChannelType(IntEnum):
        UNKNOWN = 0
        RANK_UP = 1
        REBOOT_MESSAGE = 2
        ROLE_EDITOR = 3
        # 只能新添Channel, 不要刪除舊有的

    class KujiType(IntEnum):
        UNKNOWN = 0 
        LUNGSHAN = 1 # 龍山寺
        OMIKUJI = 2 # 日本神簽
        YI = 3 # 易經
        # 只能添加新的抽籤種類, 不要刪除舊有的
        
    # 升級為next_rank所需的經驗值
    def get_rank_exp(next_rank:int):
        return round(5 / 6 * next_rank * (2 * next_rank * next_rank + 27 * next_rank + 91), 2)
