from common.models.BaseModel import BaseModel
from peewee import *

class GamblingBet(BaseModel):
    id = AutoField() # 賭注本身的id
    member_id = IntegerField() # 下注人的id
    game_id = IntegerField() # 這個賭注所屬的遊戲id
    item_index = IntegerField() # 這個賭注所壓的項目
    charge = IntegerField() # 下注數量
    create = DateTimeField() # 下注時間
    