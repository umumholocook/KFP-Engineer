# common/database/

## Purpose
SQLite schema migration for the KFP bot database.

## Files
- `KfpMigrator.py` — `KfpMigrator.KfpMigrate(database)` called on every `KfpDb()` init

## How Migrations Work
Uses Peewee `playhouse.migrate` (`SqliteMigrator`, `migrate()`):
1. Check if table exists
2. Inspect columns via `database.get_columns()`
3. Add/rename/drop columns conditionally

## Examples of Past Migrations
- `rpgcharacter`: added `retired`, `last_attack`
- `member`: added `token`
- `channel`: renamed `channel_discord_id` → `channel_id`, added `channel_guild_id`
- `item`: dropped deprecated `hidden`, `buff_type` columns

## Adding a Migration
```python
if "tablename" in tables:
    columns = database.get_columns("tablename")
    if not KfpMigrator.hasColumn("new_col", columns):
        migrate(migrator.add_column("tablename", "new_col", FieldType(default=...)))
```

## Testing
`tests/Database/KfpMigrator_test.py`