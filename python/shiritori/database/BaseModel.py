from peewee import SqliteDatabase, Model, DatabaseProxy

proxy = DatabaseProxy()

class BaseModel(Model):
    class Meta:
        database = proxy