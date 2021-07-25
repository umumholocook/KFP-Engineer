from common.models.BaseModel import BaseModel
from common.models.Member import Member
from peewee import *

class Character(BaseModel):
    id = AutoField()                                            # PRIMARY KEY AUTO-INCREMENT
    character = ForeignKeyField(Member, backref='characters')   # FOREIGN KEY REFERENCES class Member
    
    hp_current = IntegerField()                                 # Current hit-points
    hp_max = IntegerField()                                     # Maximum hit-points

    mp_current = IntegerField()                                 # Current magic-points
    mp_max = IntegerField()                                     # Maximum magic-points

    attack_basic = IntegerField()                               # Basic attack points
    # attack_bonus = ForeignKeyField()                          # Additional attack points affected by gears, etc.

    defense_basic = IntegerField()                              # Basic defense points
    # defense_bonus = ForeignKeyField()                         # Additional defense points affected by gears, etc.
