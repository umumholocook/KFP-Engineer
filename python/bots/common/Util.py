from enum import IntEnum
# 工具類 methods
class Util:
    # 升級為next_rank所需的經驗值
    def get_rank_exp(next_rank:int):
        return 5 / 6 * next_rank * (2 * next_rank * next_rank + 27 * next_rank + 91)

    class ChannelType(IntEnum):
        UNKNOWN = 0
        RANK_UP = 1
        # 只能新添Channel, 不要刪除舊有的
