from common.models.BaseModel import BaseModel
from peewee import *

class GamblingGame(BaseModel):
    id = AutoField()
    name = TextField() # 賭盤名稱
    guild_id = IntegerField() # 賭盤的群id
    base = IntegerField() # 每注單位
    start = DateTimeField()
    end = DateTimeField()
    status = IntegerField() # 賭盤狀態
    pool = IntegerField() # 賭池, 目前下注的總資金
    creater_id = IntegerField() # 發起人
    message_id = IntegerField() # 觸發賭盤的消息id
    channel_id = IntegerField()
    winning_index = IntegerField() # 賭盤贏的項目
    item_list = TextField() # 賭盤裡可以下注的項目
