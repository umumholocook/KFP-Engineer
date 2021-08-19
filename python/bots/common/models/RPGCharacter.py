from common.models.BaseModel import BaseModel
from common.models.Member import Member
from peewee import *

class RPGCharacter(BaseModel):
    id = AutoField()                                            # PRIMARY KEY AUTO-INCREMENT
    character = ForeignKeyField(Member, backref='characters')   # FOREIGN KEY REFERENCES class Member
    
    hp_current = IntegerField()                                 # Current hit-points
    hp_max = IntegerField()                                     # Maximum hit-points

    mp_current = IntegerField()                                 # Current magic-points
    mp_max = IntegerField()                                     # Maximum magic-points

    attack_basic = IntegerField()                               # Basic attack points
    defense_basic = IntegerField()                              # Basic defense points

    retired = BooleanField()                                    # Indicator for if this character retired