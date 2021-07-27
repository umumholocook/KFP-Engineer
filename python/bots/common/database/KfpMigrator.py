from common.models.Member import Member
from peewee import SqliteDatabase
from peewee import BigIntegerField, IntegerField
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
        if "channel" in tables:
            columns = database.get_columns("channel")
            if not KfpMigrator.hasColumn("channel_id", columns):
                guildIdField = IntegerField(default=-1)
                migrate(
                    migrator.add_column('channel', 'channel_guild_id', guildIdField),
                    migrator.rename_column('channel', 'channel_discord_id', 'channel_id'),
                )
        if "item" in tables:
            columns = database.get_columns("item")
            if KfpMigrator.hasColumn("hidden", columns):
                typeField = IntegerField(default=0)
                buff_type = IntegerField(default=0)
                buff_value = IntegerField(default=0)
                migrate(
                    migrator.drop_column('item', 'hidden'),
                    migrator.add_column('item', 'type', typeField),
                    migrator.add_column('item', 'buff_type', buff_type),
                    migrator.add_column('item', 'buff_value', buff_value)
                )
        return True

    def hasColumn(columnName: str, columns):
        for column in columns:
            column_name = column[0]
            if column_name == columnName:
                return True
        return False