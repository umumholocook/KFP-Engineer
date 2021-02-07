# 工具類 methods
class Util:
    # 升級為next_rank所需的經驗值
    def get_rank_xp(next_rank:int):
        return 5 / 6 * next_rank * (2 * next_rank * next_rank + 27 * next_rank + 91)
