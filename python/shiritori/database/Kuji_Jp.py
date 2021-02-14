from database.BaseModel import BaseModel
from datetime import datetime
from peewee import *

class RecordJp(BaseModel):
    member_id=AutoField()
    index=IntegerField()
    timestamp = DateTimeField(default=datetime.now)
