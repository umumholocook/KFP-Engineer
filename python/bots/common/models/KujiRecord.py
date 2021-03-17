from common.models.BaseModel import BaseModel
from datetime import datetime
from peewee import *

class KujiRecord(BaseModel):
    id = AutoField()
    member_id = IntegerField()
    index = IntegerField()
    kuji_type = IntegerField()
    timestamp = DateTimeField(default=datetime.now)