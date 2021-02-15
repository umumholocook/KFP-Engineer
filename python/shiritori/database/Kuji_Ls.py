from database.BaseModel import BaseModel
from datetime import datetime
from peewee import *

class RecordLs(BaseModel):
    member_id=AutoField()
    index=IntegerField()
    timestamp = DateTimeField(default=datetime.now)