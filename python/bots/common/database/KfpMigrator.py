from common.models.Member import Member
from peewee import SqliteDatabase
from peewee import BigIntegerField
from playhouse.migrate import SqliteMigrator
from playhouse.migrate import migrate

class KfpMigrator():
    def KfpMigrate(database: SqliteDatabase):
        tables = database.get_tables()
        migrator = SqliteMigrator(database)

        if "member" in tables:
            columns = database.get_columns("member")
            if not KfpMigrator.hasColumn("token", columns):
                tokenField = BigIntegerField(default=100)
                migrate(
                    migrator.add_column("member", 'token', tokenField)
                )
        return True

    def hasColumn(columnName: str, columns):
        for column in columns:
            column_name = column[0]
            if column_name == columnName:
                return True
        return False