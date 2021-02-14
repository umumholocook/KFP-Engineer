from database.BaseModel import BaseModel
from datetime import datetime
from peewee import *

class RecordCn(BaseModel):
    member_id=AutoField()
    timestamp = DateTimeField(default=datetime.now)
