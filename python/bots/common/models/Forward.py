from common.models.BaseModel import BaseModel
from peewee import *

class Forward(BaseModel):
    id = AutoField()
    send_guild_id = IntegerField(null=True) # 發送消息的群組
    send_channel_id = IntegerField() # 發送消息的頻道
    receive_guild_id = IntegerField(null=True) # 接收消息的群組
    receive_channel_id = IntegerField(null=True) # 接收消息的頻道
    forward_type = IntegerField(default=0) # 復誦類型, 預設是一對一
    delete_original = BooleanField(default=False) # 是否刪除原始消息