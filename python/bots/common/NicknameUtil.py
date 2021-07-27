import random
from common.models.NicknameModel import NicknameModel
from discord import User, Guild

class NicknameUtil():
    def set_nickname(guild_id: int, user_id: int, nickname: str):
        print(str)
        if NicknameUtil.has_nickname(guild_id, user_id, nickname):
            return False
        NicknameModel.insert(guild_id=guild_id, member_id=user_id, nick_name=nickname).execute()
        return True

    def has_nickname(guild_id: int, user_id: int, nickname: str):
        query = NicknameModel.select().where(
            NicknameModel.guild_id == guild_id, 
            NicknameModel.member_id == user_id,
            NicknameModel.nick_name == nickname)
        return query.exists()

    def clear_nickname(guild_id: int, user_id: int):
        query = NicknameModel.select().where(NicknameModel.guild_id == guild_id, NicknameModel.member_id == user_id)
        count = 0
        if query.exists():
            for nickname in query.iterator():
                nickname.delete_instance()
                count += 1
        return count

    def remove_nickname(guild_id: int, user_id: int, name:str):
        query = NicknameModel.select().where(
            NicknameModel.guild_id == guild_id, 
            NicknameModel.member_id == user_id,
            NicknameModel.nick_name == name)
        if query.exists():
            nickname: NicknameModel = query.get()
            nickname.delete_instance()
            return True
        return False

    def remove_nickname_id(guild_id: int, user_id: int, name_id: int):
        query = NicknameModel.select().where(
            NicknameModel.id == name_id,
            NicknameModel.guild_id == guild_id, 
            NicknameModel.member_id == user_id)
        if query.exists():
            nickname: NicknameModel = query.get()
            nickname.delete_instance()
            return True
        return False
    
    def get_all_nicknames_detail(guild_id: int, user_id: int):
        result = []
        query = NicknameModel.select().where(NicknameModel.guild_id == guild_id, NicknameModel.member_id == user_id)
        if query.exists():
            for nickname in query.iterator():
                result.append(nickname)
        return result

    def get_all_nicknames(guild_id:int, user_id: int):
        result = []
        query = NicknameModel.select().where(NicknameModel.guild_id == guild_id, NicknameModel.member_id == user_id)
        if query.exists():
            for nickname in query.iterator():
                result.append(nickname.nick_name)
        return result
    
    async def get_user_nickname_or_default(guild: Guild, user: User):
        nicknames = NicknameUtil.get_all_nicknames(guild_id=guild.id, user_id=user.id)
        member = await guild.fetch_member(user.id)
        if len(nicknames) < 1:
            if member:
                return member.display_name
            return user.name
        else:
            return random.choice(nicknames)
