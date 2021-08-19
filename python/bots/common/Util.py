from enum import IntEnum

# 工具類 methods
class Util:
    # 預設database 位置
    DEFAULT_DB_PATH = r"./common/KFP_bot.db"

    class ChannelType(IntEnum):
        UNKNOWN = 0
        RANK_UP = 1 # 等級提升通知頻道
        REBOOT_MESSAGE = 2 # Bot重啟之後提示的頻道
        IGNORE_XP = 3 # 停止增加經驗值
        AUTO_DELETE = 4 # 自動刪除成員留言
        ROLE_EDITOR = 5 # 可以修改身分組的頻道
        PROFILE = 6 # 可以使用 profile 指令的頻道
        BANK = 7 # 可以使用 bank 指令的頻道
        RPG_GUILD = 8 # 可以使用RPG指令的頻道
        RPG_BATTLE_GROUND = 9 # 可以使用攻擊指令的頻道
        # 只能新添Channel, 不要刪除舊有的

    class KujiType(IntEnum):
        UNKNOWN = 0 
        LUNGSHAN = 1 # 龍山寺
        OMIKUJI = 2 # 日本神簽
        YI = 3 # 易經
        # 只能添加新的抽籤種類, 不要刪除舊有的

    # 一般會員身分組種類
    class RoleCategory(IntEnum):
        NONE = 0 # 其他
        KFP_DEFAULT = 1 # KFP預設 (雞蛋, 小雞... 等)
        KFP_LEWD = 2
        KFP_UTIL = 3
        KFP_ADVANTURE = 4
    
    # 賭盤狀態
    class GamblingStatus(IntEnum):
        init = 0
        ready = 1 #可以加註的狀態
        wait = 2 #等待賭局結果
        end = 3 #賭局結束
        # 只能新添Status, 不要刪除舊有的
    
    # 賭盤錯誤狀態
    class GamblingError(IntEnum):
        ok = 1
        error = 0
        state_wrong = -1
        # 只能新添Error, 不要刪除舊有的

    # 管理級別身分組類別
    class ManagementType(IntEnum):
        Gambling = 1
        # 只能新添Role, 不要刪除舊有的

    class ForwardType(IntEnum):
        DIRECT = 0
        BROADCAST = 1
        # 只能新添Type, 不要刪除舊有的

    # 抽籤種類
    class KujiType(IntEnum):
        OMIKUJI = 0
        LUNGSHAN = 1
        YI = 2
        # 只能新添Type, 不要刪除舊有的

    # 點選反應來增加身分組
    class ReactionType(IntEnum):
        UNKNOWN = 0
        LEWD = 1
        COLOR = 2
        # 只能新添Type, 不要刪除舊有的

    # 升級為next_rank所需的經驗值
    def get_rank_exp(next_rank:int):
        return round(5 / 6 * next_rank * (2 * next_rank * next_rank + 27 * next_rank + 91), 2)
    
    async def find_emoji_with_name(bot, guild_id:int, emoji_name: str):
        guild = await bot.fetch_guild(guild_id)
        for emoji in guild.emojis:
            if emoji_name == emoji.name:
                return emoji
        return emoji_name


    
