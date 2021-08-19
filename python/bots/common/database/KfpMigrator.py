from common.RPGUtil.ItemType import ItemType
from common.customField.BuffField import BuffField
from common.RPGUtil.Buff import Buff, BuffType
from peewee import BooleanField, SqliteDatabase, CharField
from peewee import BigIntegerField, IntegerField
from playhouse.migrate import SqliteMigrator
from playhouse.migrate import migrate

class KfpMigrator():
    def KfpMigrate(database: SqliteDatabase):
        tables = database.get_tables()
        migrator = SqliteMigrator(database)
        if "rpgcharacter" in tables:
            columns = database.get_columns("rpgcharacter")
            if not KfpMigrator.hasColumn("retired", columns):
                retiredField = BooleanField(default=False)
                migrate(
                    migrator.add_column("rpgcharacter", "retired", retiredField)
                )
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
                migrate(
                    migrator.drop_column('item', 'hidden'),
                )
            if KfpMigrator.hasColumn("buff_type", columns):                
                migrate(
                    migrator.drop_column('item', 'buff_type'),
                )
            if KfpMigrator.hasColumn("buff_value", columns):                
                migrate(
                    migrator.drop_column('item', 'buff_value'),
                )
            if not KfpMigrator.hasColumn("type", columns):
                typeField = CharField(default=ItemType.NONE)
                migrate(
                    migrator.add_column('item', 'type', typeField),
                )
            if not KfpMigrator.hasColumn("buff", columns):
                buff = BuffField(default=Buff(BuffType.NONE, 0, -1))
                migrate(
                    migrator.add_column('item', 'buff', buff),
                )
            if not KfpMigrator.hasColumn("description", columns):
                description = CharField(default="")
                migrate(
                    migrator.add_column('item', 'description', description),
                )
        return True

    def hasColumn(columnName: str, columns):
        for column in columns:
            column_name = column[0]
            if column_name == columnName:
                return True
        return False