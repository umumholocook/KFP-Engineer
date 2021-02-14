from database.BaseModel import BaseModel
from datetime import datetime
from peewee import *

class RecordJp(BaseModel):
    member_id=AutoField()
    timestamp = DateTimeField(default=datetime.now)
