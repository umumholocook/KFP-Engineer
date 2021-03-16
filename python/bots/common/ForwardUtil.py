from common.models.Forward import Forward
from common.Util import Util

class ForwardUtil():
    def create_forward(send_guild_id: int, send_channel_id: int, receive_guild_id: int, receive_channel_id: int, delete_original:bool):
        if send_guild_id != receive_guild_id:
            # 目前不支援跨群直傳
            return False
        if send_guild_id == 0:
            # 群id不能為0
            return False
        query = Forward.select().where(
            Forward.send_guild_id==send_guild_id, 
            Forward.send_channel_id==send_channel_id, 
            Forward.receive_guild_id==receive_guild_id, 
            Forward.receive_channel_id==receive_channel_id, 
            Forward.forward_type==Util.ForwardType.DIRECT)
        if query.exists():
            return True # 紀錄已存在, 跳過
        Forward.insert(send_guild_id=send_guild_id, send_channel_id=send_channel_id, receive_guild_id=receive_guild_id, receive_channel_id=receive_channel_id, forward_type=Util.ForwardType.DIRECT, delete_original=delete_original).execute()
        return True
    
    def get_all_forward():
        result = []
        query = Forward.select().where(Forward.forward_type == Util.ForwardType.DIRECT)
        if query.exists():
            for forward in query.iterator():
                result.append(forward)
        return result
    
    def get_forward(guild_id:int, channel_id:int):
        result = []
        query = Forward.select().where(Forward.send_guild_id == guild_id, Forward.send_channel_id == channel_id)
        if query.exists():
            for forward in query.iterator():
                result.append(forward)
        return result

    def delete(forward_id:int):
        query = Forward.select().where(Forward.id == forward_id)
        if query.exists():
            forward: Forward = query.get()
            forward.delete_instance()