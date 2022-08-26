from common.models.BaseModel import BaseModel
from peewee import *

class RouletteGameBet(BaseModel):
    id = AutoField() # roulette bet id
    game_id = IntegerField() # the id this game associated with
    member_id = IntegerField() # the member who place this bet
    betting_number = IntegerField() # the number member bet on
    amount = IntegerField() # the amount of coin this bet is worth
    