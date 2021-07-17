import random
from common.models.NicknameModel import NicknameModel
from discord import User

class NicknameUtil():
    def set_nickname(guild_id: int, user_id: int, nickname: str):
        NicknameModel.insert(guild_id=guild_id, member_id=user_id, nick_name=nickname).execute()
        return True

    def clear_nickname(guild_id: int, user_id: int):
        query = NicknameModel.select().where(NicknameModel.guild_id == guild_id, NicknameModel.member_id == user_id)
        count = 0
        if query.exists():
            for nickname in query.iterator():
                nickname.delete_instance()
                count += 1
        return count
    
    def get_all_nicknames(guild_id:int, user_id: int):
        result = []
        query = NicknameModel.select().where(NicknameModel.guild_id == guild_id, NicknameModel.member_id == user_id)
        if query.exists():
            for nickname in query.iterator():
                result.append(nickname.nick_name)
        return result
    
    def get_user_nickname_or_default(guild_id:int, user: User):
        nicknames = NicknameUtil.get_all_nicknames(guild_id=guild_id, user_id=user.id)
        if len(nicknames) < 1:
            return user.name
        else:
            return random.choice(nicknames)
